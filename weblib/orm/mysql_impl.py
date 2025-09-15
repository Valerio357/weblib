from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncContextManager, Dict, Iterable, List, Optional, Tuple, Type

from .fields import Field


def _sql_type_mysql(f: Field) -> str:
    if f.kind == "int":
        return "INT"
    if f.kind == "bool":
        return "TINYINT(1)"
    if f.kind == "str":
        # se max_length non definito, usa TEXT per semplicità
        return "VARCHAR(255)" if (f.max_length and f.max_length > 0) else "TEXT"
    if f.kind == "text":
        return "TEXT"
    if f.kind == "datetime":
        return "DATETIME"
    if f.kind == "fk":
        return "INT"
    return "TEXT"


@dataclass
class _ModelInfo:
    table: str
    fields: List[Tuple[str, Field]]
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
            cols.append(f"{name} INT PRIMARY KEY AUTO_INCREMENT")
            continue
        parts = [name, _sql_type_mysql(f)]
        if f.pk:
            parts.append("PRIMARY KEY")
        if f.unique:
            parts.append("UNIQUE")
        cols.append(" ".join(parts))
    return f"create table if not exists {mi.table} (" + ", ".join(cols) + ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"


class _MySQLPool:
    def __init__(self, dsn: str):
        # dsn come: mysql://user:pass@host:3306/dbname
        self.dsn = dsn
        self.pool = None
        self._mod = None
        self._dict_cursor_cls = None

    async def ensure(self):
        mod = None
        try:
            import asyncmy as mod  # type: ignore
        except Exception:
            try:
                import aiomysql as mod  # type: ignore
            except Exception as e:
                raise RuntimeError("Nessun driver MySQL async trovato. Installa asyncmy o aiomysql.") from e

        if self.pool is None:
            # parse DSN manualmente
            import re
            m = re.match(r"^mysql://(?P<user>[^:]+):(?P<pwd>[^@]+)@(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<db>.+)$", self.dsn)
            if not m:
                raise ValueError("DSN MySQL non valido. Esempio: mysql://user:pass@localhost:3306/dbname")
            cfg = m.groupdict()
            host = cfg["host"]
            user = cfg["user"]
            password = cfg["pwd"]
            db = cfg["db"]
            port = int(cfg.get("port") or 3306)
            self.pool = await mod.create_pool(host=host, port=port, user=user, password=password, db=db, minsize=1, maxsize=10)  # type: ignore[attr-defined]
            # salva riferimenti per cursor dict
            self._mod = mod
            try:
                # asyncmy
                from asyncmy.cursors import DictCursor as _DC  # type: ignore
                self._dict_cursor_cls = _DC
            except Exception:
                try:
                    from aiomysql.cursors import DictCursor as _DC  # type: ignore
                    self._dict_cursor_cls = _DC
                except Exception:
                    self._dict_cursor_cls = None
        return self.pool

    @asynccontextmanager
    async def acquire(self):
        pool = await self.ensure()
        async with pool.acquire() as conn:  # type: ignore[attr-defined]
            if self._dict_cursor_cls is not None:
                async with conn.cursor(self._dict_cursor_cls) as cur:  # type: ignore[attr-defined]
                    yield conn, cur
            else:
                async with conn.cursor() as cur:  # type: ignore[attr-defined]
                    yield conn, cur


class MySQLORM:
    def __init__(self, dsn: str) -> None:
        self._pool = _MySQLPool(dsn)
        self._models: Dict[Type, _ModelInfo] = {}
        self._ensured: set[str] = set()

    async def create_database(self):
        await self._pool.ensure()

    async def drop_database(self):
        pass

    @asynccontextmanager
    async def session(self):
        async with self._pool.acquire() as pair:
            yield pair  # (conn, cur)

    async def migrate(self):
        for mi in self._models.values():
            await self._ensure_table(mi)

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
        async with self.session() as (conn, cur):
            await cur.execute(_create_table_sql(mi))
            await conn.commit()  # type: ignore[attr-defined]
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
    def __init__(self, orm: MySQLORM, model: Type, mi: _ModelInfo) -> None:
        self.orm = orm
        self.model = model
        self.mi = mi

    async def create(self, **fields) -> Record:
        await self.orm._ensure_table(self.mi)
        cols: List[str] = []
        vals: List[Any] = []
        ph: List[str] = []
        for name, f in self.mi.fields:
            if name in fields and not f.pk:
                cols.append(name)
                vals.append(fields[name])
                ph.append("%s")
        sql = f"insert into {self.mi.table} (" + ",".join(cols) + ") values (" + ",".join(ph) + ")"
        async with self.orm.session() as (conn, cur):
            await cur.execute(sql, vals)
            last_id = cur.lastrowid  # type: ignore[attr-defined]
            await conn.commit()  # type: ignore[attr-defined]
        data = dict(fields)
        if self.mi.pk and self.mi.pk not in data:
            data[self.mi.pk] = last_id
        return Record(self, data)

    async def get(self, **filters) -> Optional[Record]:
        await self.orm._ensure_table(self.mi)
        where_sql, params = _where_mysql(filters)
        sql = f"select * from {self.mi.table} {where_sql} limit 1"
        async with self.orm.session() as (_conn, cur):
            await cur.execute(sql, params)
            row = await cur.fetchone()
        return Record(self, dict(row)) if row else None  # row è già dict con DictCursor

    def query(self) -> Query:
        return Query(self)

    async def find(self, where: List[Tuple[str, Any]] | None = None, order: Optional[str] = None, limit: Optional[int] = None) -> List[Record]:
        await self.orm._ensure_table(self.mi)
        filters = {k: v for (k, v) in (where or [])}
        where_sql, params = _where_mysql(filters)
        order_sql = f" order by {order}" if order else ""
        limit_sql = f" limit {int(limit)}" if limit is not None else ""
        sql = f"select * from {self.mi.table}{where_sql}{order_sql}{limit_sql}"
        async with self.orm.session() as (_conn, cur):
            await cur.execute(sql, params)
            rows = await cur.fetchall()
        return [Record(self, dict(r)) for r in rows]

    async def update_one(self, data: Dict[str, Any], changes: Dict[str, Any]) -> None:
        if not self.mi.pk or self.mi.pk not in data:
            raise ValueError("Update requires primary key on record")
        await self.orm._ensure_table(self.mi)
        sets = ",".join(f"{k}=%s" for k in changes.keys())
        sql = f"update {self.mi.table} set {sets} where {self.mi.pk}=%s"
        params = list(changes.values()) + [data[self.mi.pk]]
        async with self.orm.session() as (conn, cur):
            await cur.execute(sql, params)
            await conn.commit()  # type: ignore[attr-defined]

    async def delete_one(self, data: Dict[str, Any]) -> None:
        if not self.mi.pk or self.mi.pk not in data:
            raise ValueError("Delete requires primary key on record")
        await self.orm._ensure_table(self.mi)
        sql = f"delete from {self.mi.table} where {self.mi.pk}=%s"
        async with self.orm.session() as (conn, cur):
            await cur.execute(sql, [data[self.mi.pk]])
            await conn.commit()  # type: ignore[attr-defined]


def _where_mysql(filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
    if not filters:
        return "", []
    parts = []
    params: List[Any] = []
    for k, v in filters.items():
        parts.append(f"{k}=%s")
        params.append(v)
    return " where " + " and ".join(parts), params


def _bind_model_helpers(orm: MySQLORM, model: Type) -> None:
    async def create_cls(**fields):
        return await orm.repo(model).create(**fields)

    async def get_cls(**filters):
        return await orm.repo(model).get(**filters)

    def query_cls():
        return orm.repo(model).query()

    setattr(model, "create", staticmethod(create_cls))
    setattr(model, "get", staticmethod(get_cls))
    setattr(model, "query", staticmethod(query_cls))
