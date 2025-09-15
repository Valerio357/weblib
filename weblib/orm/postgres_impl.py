from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncContextManager, Dict, Iterable, List, Optional, Tuple, Type

from .fields import Field


def _sql_type_pg(f: Field) -> str:
    if f.kind == "int":
        return "INTEGER"
    if f.kind == "bool":
        return "BOOLEAN"
    if f.kind in {"str", "text"}:
        return "TEXT"
    if f.kind == "datetime":
        return "TIMESTAMPTZ"
    if f.kind == "fk":
        return "INTEGER"
    return "TEXT"


@dataclass
class _ModelInfo:
    table: str
    fields: List[Tuple[str, Field]]  # (name, field)
    pk: Optional[str]


def _introspect_model(model: Type) -> _ModelInfo:
    table = getattr(getattr(model, "Meta", object), "table_name", None) or model.__name__.lower()
    names_fields: List[Tuple[str, Field]] = []
    pk_name: Optional[str] = None
    for name, value in model.__dict__.items():
        if isinstance(value, Field):
            names_fields.append((name, value))
            if value.pk:
                pk_name = name
    if pk_name is None:
        for n, f in names_fields:
            if n == "id" and f.kind == "int":
                pk_name = n
                break
    return _ModelInfo(table=table, fields=names_fields, pk=pk_name)


def _create_table_sql(mi: _ModelInfo) -> str:
    cols: List[str] = []
    for name, f in mi.fields:
        if f.pk and f.kind == "int":
            cols.append(f"{name} SERIAL PRIMARY KEY")
            continue
        parts = [name, _sql_type_pg(f)]
        if f.pk:
            parts.append("PRIMARY KEY")
        if f.unique:
            parts.append("UNIQUE")
        cols.append(" ".join(parts))
    return f"create table if not exists {mi.table} (" + ", ".join(cols) + ")"


class _PgPool:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None  # type: ignore[assignment]

    async def ensure(self):
        if self.pool is None:
            try:
                import asyncpg  # type: ignore
            except Exception as e:
                raise RuntimeError("asyncpg non installato. Esegui: pip install asyncpg") from e
            self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=10)
        return self.pool

    @asynccontextmanager
    async def acquire(self):
        pool = await self.ensure()
        async with pool.acquire() as conn:  # type: ignore[attr-defined]
            yield conn


class PostgresORM:
    def __init__(self, dsn: str) -> None:
        self._pool = _PgPool(dsn)
        self._models: Dict[Type, _ModelInfo] = {}
        self._ensured: set[str] = set()

    async def create_database(self):
        # delegato all'istanza del server/utente; non gestito qui
        await self._pool.ensure()

    async def drop_database(self):
        # non implementato: operazione distruttiva fuori scope
        pass

    @asynccontextmanager
    async def session(self):
        async with self._pool.acquire() as conn:
            yield conn

    async def migrate(self):
        async with self.session() as conn:
            for mi in self._models.values():
                await conn.execute(_create_table_sql(mi))

    def repo(self, model: Type) -> "Repository":
        mi = self._models.get(model)
        if not mi:
            mi = _introspect_model(model)
            self._models[model] = mi
            _bind_model_helpers(self, model)
        return Repository(self, model, mi)

    async def _ensure_table(self, mi: _ModelInfo):
        if mi.table in self._ensured:
            return
        async with self.session() as conn:
            await conn.execute(_create_table_sql(mi))
        self._ensured.add(mi.table)


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
    def __init__(self, orm: PostgresORM, model: Type, mi: _ModelInfo) -> None:
        self.orm = orm
        self.model = model
        self.mi = mi

    async def create(self, **fields) -> Record:
        await self.orm._ensure_table(self.mi)
        cols = []
        vals = []
        ph = []
        for name, f in self.mi.fields:
            if name in fields and not f.pk:
                cols.append(name)
                vals.append(fields[name])
                ph.append(f"${len(vals)}")
        sql = f"insert into {self.mi.table} (" + ",".join(cols) + ") values (" + ",".join(ph) + ") returning *"
        async with self.orm.session() as conn:
            row = await conn.fetchrow(sql, *vals)
        return Record(self, dict(row))

    async def get(self, **filters) -> Optional[Record]:
        await self.orm._ensure_table(self.mi)
        where_sql, params = _where_pg(filters)
        sql = f"select * from {self.mi.table} {where_sql} limit 1"
        async with self.orm.session() as conn:
            row = await conn.fetchrow(sql, *params)
        return Record(self, dict(row)) if row else None

    def query(self) -> Query:
        return Query(self)

    async def find(self, where: List[Tuple[str, Any]] | None = None, order: Optional[str] = None, limit: Optional[int] = None) -> List[Record]:
        await self.orm._ensure_table(self.mi)
        filters = {k: v for (k, v) in (where or [])}
        where_sql, params = _where_pg(filters)
        order_sql = f" order by {order}" if order else ""
        limit_sql = f" limit {int(limit)}" if limit is not None else ""
        sql = f"select * from {self.mi.table}{where_sql}{order_sql}{limit_sql}"
        async with self.orm.session() as conn:
            rows = await conn.fetch(sql, *params)
        return [Record(self, dict(r)) for r in rows]

    async def update_one(self, data: Dict[str, Any], changes: Dict[str, Any]) -> None:
        if not self.mi.pk or self.mi.pk not in data:
            raise ValueError("Update requires primary key on record")
        await self.orm._ensure_table(self.mi)
        sets = []
        params: List[Any] = []
        for k, v in changes.items():
            params.append(v)
            sets.append(f"{k}=${len(params)}")
        params.append(data[self.mi.pk])
        sql = f"update {self.mi.table} set {', '.join(sets)} where {self.mi.pk}=${len(params)}"
        async with self.orm.session() as conn:
            await conn.execute(sql, *params)

    async def delete_one(self, data: Dict[str, Any]) -> None:
        if not self.mi.pk or self.mi.pk not in data:
            raise ValueError("Delete requires primary key on record")
        await self.orm._ensure_table(self.mi)
        sql = f"delete from {self.mi.table} where {self.mi.pk}=$1"
        async with self.orm.session() as conn:
            await conn.execute(sql, data[self.mi.pk])


def _where_pg(filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
    if not filters:
        return "", []
    parts = []
    params: List[Any] = []
    for k, v in filters.items():
        params.append(v)
        parts.append(f"{k}=${len(params)}")
    return " where " + " and ".join(parts), params


def _bind_model_helpers(orm: PostgresORM, model: Type) -> None:
    async def create_cls(**fields):
        return await orm.repo(model).create(**fields)

    async def get_cls(**filters):
        return await orm.repo(model).get(**filters)

    def query_cls():
        return orm.repo(model).query()

    setattr(model, "create", staticmethod(create_cls))
    setattr(model, "get", staticmethod(get_cls))
    setattr(model, "query", staticmethod(query_cls))

