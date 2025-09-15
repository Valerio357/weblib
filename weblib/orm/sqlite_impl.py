from __future__ import annotations

import asyncio
import os
import sqlite3
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncContextManager, Dict, Iterable, List, Optional, Tuple, Type

from .fields import Field


def _sql_type(f: Field) -> str:
    if f.kind == "int":
        return "INTEGER"
    if f.kind == "bool":
        return "INTEGER"
    if f.kind in {"str", "text"}:
        return "TEXT"
    if f.kind == "datetime":
        return "TEXT"  # ISO string
    if f.kind == "fk":
        return "INTEGER"
    return "TEXT"


@dataclass
class _ModelInfo:
    table: str
    fields: List[Tuple[str, Field]]  # (name, field)
    pk: Optional[str]


def _introspect_model(model: Type) -> _ModelInfo:
    # Table name
    table = getattr(getattr(model, "Meta", object), "table_name", None) or model.__name__.lower()
    # Keep declared order (class dict preserves order)
    names_fields: List[Tuple[str, Field]] = []
    pk_name: Optional[str] = None
    for name, value in model.__dict__.items():
        if isinstance(value, Field):
            names_fields.append((name, value))
            if value.pk:
                pk_name = name
    # Fallback pk if present by convention
    if pk_name is None:
        for n, f in names_fields:
            if n == "id" and f.kind == "int":
                pk_name = n
                break
    return _ModelInfo(table=table, fields=names_fields, pk=pk_name)


class _AioSQLite:
    def __init__(self, path: str) -> None:
        self.path = path
        self._conn: Optional[sqlite3.Connection] = None

    async def __aenter__(self):
        def _open():
            conn = sqlite3.connect(self.path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn

        self._conn = await asyncio.to_thread(_open)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self._conn is not None:
            conn = self._conn
            self._conn = None
            await asyncio.to_thread(conn.close)

    async def execute(self, sql: str, params: Iterable[Any] | None = None):
        assert self._conn is not None
        return await asyncio.to_thread(self._conn.execute, sql, tuple(params or ()))

    async def executemany(self, sql: str, seq: Iterable[Iterable[Any]]):
        assert self._conn is not None
        return await asyncio.to_thread(self._conn.executemany, sql, list(seq))

    async def fetchone(self, sql: str, params: Iterable[Any] | None = None) -> Optional[sqlite3.Row]:
        cur = await self.execute(sql, params)
        return await asyncio.to_thread(cur.fetchone)

    async def fetchall(self, sql: str, params: Iterable[Any] | None = None) -> List[sqlite3.Row]:
        cur = await self.execute(sql, params)
        return await asyncio.to_thread(cur.fetchall)

    async def commit(self):
        assert self._conn is not None
        await asyncio.to_thread(self._conn.commit)


class SQLiteORM:
    """ORM minimale basato su SQLite (async via threadpool).

    - Nessuna dipendenza esterna
    - Mapping semplice campi→colonne
    - Repository e Query basilari
    """

    def __init__(self, path: str = ":memory:") -> None:
        self.path = path
        self._models: Dict[Type, _ModelInfo] = {}
        self._ensured: set[str] = set()

    async def create_database(self):
        # Per SQLite il DB è creato on-demand all'apertura
        if self.path != ":memory:" and not os.path.exists(self.path):
            # apri/chiudi per creare il file
            async with _AioSQLite(self.path):
                pass

    async def drop_database(self):
        if self.path != ":memory:" and os.path.exists(self.path):
            os.remove(self.path)

    @asynccontextmanager
    async def session(self) -> AsyncContextManager[_AioSQLite]:
        async with _AioSQLite(self.path) as db:
            try:
                yield db
                await db.commit()
            except Exception:
                # SQLite non ha rollback automatico qui; semplifichiamo
                raise

    async def migrate(self):
        # Crea tabelle per i modelli registrati (repo() chiamato almeno una volta)
        async with self.session() as db:
            for mi in self._models.values():
                sql = _create_table_sql(mi)
                await db.execute(sql)

    def repo(self, model: Type) -> "Repository":
        mi = self._models.get(model)
        if not mi:
            mi = _introspect_model(model)
            self._models[model] = mi
            # collega helper al model (create/get/query)
            _bind_model_helpers(self, model)
        return Repository(self, model, mi)

    async def _ensure_table(self, mi: _ModelInfo):
        if mi.table in self._ensured:
            return
        async with self.session() as db:
            await db.execute(_create_table_sql(mi))
        self._ensured.add(mi.table)


def _create_table_sql(mi: _ModelInfo) -> str:
    cols: List[str] = []
    for name, f in mi.fields:
        parts = [name, _sql_type(f)]
        if f.pk:
            parts.append("PRIMARY KEY")
            if f.kind == "int":
                parts.append("AUTOINCREMENT")
        if f.unique:
            parts.append("UNIQUE")
        cols.append(" ".join(parts))
    return f"create table if not exists {mi.table} (" + ", ".join(cols) + ")"


@dataclass
class Record:
    _repo: "Repository"
    _data: Dict[str, Any]

    def __getattr__(self, item: str) -> Any:
        if item in self._data:
            return self._data[item]
        raise AttributeError(item)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._data)

    async def update(self, **fields) -> "Record":
        await self._repo.update_one(self._data, fields)
        self._data.update(fields)
        return self

    async def delete(self) -> None:
        await self._repo.delete_one(self._data)


class Query:
    def __init__(self, repo: "Repository") -> None:
        self.repo = repo
        self._where: List[Tuple[str, Any]] = []
        self._order: Optional[str] = None
        self._limit: Optional[int] = None

    def where(self, **eq) -> "Query":
        for k, v in eq.items():
            self._where.append((k, v))
        return self

    def order(self, expr: str) -> "Query":
        self._order = expr
        return self

    def limit(self, n: int) -> "Query":
        self._limit = n
        return self

    async def all(self) -> List[Record]:
        return await self.repo.find(self._where, self._order, self._limit)

    async def first(self) -> Optional[Record]:
        rows = await self.limit(1).all()
        return rows[0] if rows else None


class Repository:
    def __init__(self, orm: SQLiteORM, model: Type, mi: _ModelInfo) -> None:
        self.orm = orm
        self.model = model
        self.mi = mi

    async def create(self, **fields) -> Record:
        cols = []
        vals = []
        ph = []
        for name, f in self.mi.fields:
            if name in fields and not f.pk:
                cols.append(name)
                vals.append(fields[name])
                ph.append("?")
        sql = f"insert into {self.mi.table} (" + ",".join(cols) + ") values (" + ",".join(ph) + ")"
        await self.orm._ensure_table(self.mi)
        async with self.orm.session() as db:
            cur = await db.execute(sql, vals)
            last_id = cur.lastrowid
        data = dict(fields)
        if self.mi.pk and self.mi.pk not in data:
            data[self.mi.pk] = last_id
        return Record(self, data)

    async def get(self, **filters) -> Optional[Record]:
        where_sql, params = _where(filters)
        sql = f"select * from {self.mi.table} {where_sql} limit 1"
        await self.orm._ensure_table(self.mi)
        async with self.orm.session() as db:
            row = await db.fetchone(sql, params)
        if row is None:
            return None
        return Record(self, dict(row))

    def query(self) -> Query:
        return Query(self)

    async def find(self, where: List[Tuple[str, Any]] | None = None, order: Optional[str] = None, limit: Optional[int] = None) -> List[Record]:
        filters = {k: v for (k, v) in (where or [])}
        where_sql, params = _where(filters)
        order_sql = f" order by {order}" if order else ""
        limit_sql = f" limit {int(limit)}" if limit is not None else ""
        sql = f"select * from {self.mi.table}{where_sql}{order_sql}{limit_sql}"
        await self.orm._ensure_table(self.mi)
        async with self.orm.session() as db:
            rows = await db.fetchall(sql, params)
        return [Record(self, dict(r)) for r in rows]

    async def update_one(self, data: Dict[str, Any], changes: Dict[str, Any]) -> None:
        if not self.mi.pk or self.mi.pk not in data:
            raise ValueError("Update requires primary key on record")
        sets = ",".join(f"{k}=?" for k in changes.keys())
        sql = f"update {self.mi.table} set {sets} where {self.mi.pk}=?"
        params = list(changes.values()) + [data[self.mi.pk]]
        await self.orm._ensure_table(self.mi)
        async with self.orm.session() as db:
            await db.execute(sql, params)

    async def delete_one(self, data: Dict[str, Any]) -> None:
        if not self.mi.pk or self.mi.pk not in data:
            raise ValueError("Delete requires primary key on record")
        sql = f"delete from {self.mi.table} where {self.mi.pk}=?"
        params = [data[self.mi.pk]]
        await self.orm._ensure_table(self.mi)
        async with self.orm.session() as db:
            await db.execute(sql, params)


def _where(filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
    if not filters:
        return "", []
    parts = []
    params: List[Any] = []
    for k, v in filters.items():
        parts.append(f"{k}=?")
        params.append(v)
    return " where " + " and ".join(parts), params


def _bind_model_helpers(orm: SQLiteORM, model: Type) -> None:
    async def create_cls(**fields):
        return await orm.repo(model).create(**fields)

    async def get_cls(**filters):
        return await orm.repo(model).get(**filters)

    def query_cls():
        return orm.repo(model).query()

    async def update_self(self, **changes):
        # self è un Record
        return await self.update(**changes)

    async def delete_self(self):
        return await self.delete()

    # Collega metodi
    setattr(model, "create", staticmethod(create_cls))
    setattr(model, "get", staticmethod(get_cls))
    setattr(model, "query", staticmethod(query_cls))
    setattr(model, "update", update_self)
    setattr(model, "delete", delete_self)
