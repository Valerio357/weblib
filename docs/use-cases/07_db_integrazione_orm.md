07 — Database e ORM (stato attuale e esempi)

Stato MVP

- È incluso un adapter `SQLiteORM` minimale per CRUD su SQLite. Per database esterni (Postgres/MySQL, ecc.) puoi usare driver/ORM esterni e integrarli via DI.
- Vedi anche: `08_orm_sqlite_adapter.md` per lo use case completo con l'adapter incluso.

Opzioni supportate (esterni)

- PostgreSQL: `asyncpg` diretto, oppure SQLAlchemy 2.x async (`asyncpg` come driver).
- SQLite: `aiosqlite` diretto, oppure SQLAlchemy 2.x async con `sqlite+aiosqlite://`.
- MySQL/MariaDB: SQLAlchemy async con `asyncmy` o `aiomysql`.

A) Esempio Postgres con `asyncpg` (pool in DI)

```python
import os
import asyncpg
from weblib import WebApp
from weblib.routing import Routes, route, HTTP

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")

routes = Routes()

async def get_pool(req):
    di = req.state.setdefault("di", {})
    if "db_pool" not in di:
        di["db_pool"] = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        async with di["db_pool"].acquire() as conn:
            await conn.execute("""
            create table if not exists items (
              id serial primary key,
              name text not null
            );
            """)
    return di["db_pool"]

@route.post("/items")
async def create_item(req):
    data = await req.json()
    pool = await get_pool(req)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("insert into items(name) values($1) returning id, name", data["name"]) 
    return HTTP.created(dict(row))

@route.get("/items/{id:int}")
async def get_item(req, id: int):
    pool = await get_pool(req)
    async with pool.acquire() as conn:
        row = await conn.fetchrow("select id, name from items where id=$1", id)
    return HTTP.ok(dict(row) if row else {"error": "not_found"})

routes.register(create_item, get_item)
app = WebApp(routes=routes)
asgi = app.asgi
```

B) Esempio SQLite con `aiosqlite` (leggero, dev/test)

```python
import aiosqlite
from weblib import WebApp
from weblib.routing import Routes, route, HTTP

routes = Routes()

async def get_db(req):
    di = req.state.setdefault("di", {})
    if "sqlite" not in di:
        db = await aiosqlite.connect("./app.db")
        await db.execute("create table if not exists notes (id integer primary key autoincrement, body text not null)")
        await db.commit()
        di["sqlite"] = db
    return di["sqlite"]

@route.post("/notes")
async def create_note(req):
    data = await req.json()
    db = await get_db(req)
    cur = await db.execute("insert into notes(body) values (?)", (data["body"],))
    await db.commit()
    return HTTP.created({"id": cur.lastrowid})

@route.get("/notes")
async def list_notes(req):
    db = await get_db(req)
    async with db.execute("select id, body from notes order by id desc") as cur:
        rows = await cur.fetchall()
    return HTTP.ok([{"id": r[0], "body": r[1]} for r in rows])

routes.register(create_note, list_notes)
app = WebApp(routes=routes)
asgi = app.asgi
```

C) SQLAlchemy 2.x async (pattern consigliato)

```python
# pip install sqlalchemy[asyncio] asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import select

class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

DATABASE_URL = "postgresql+asyncpg://user:pass@localhost:5432/db"
engine = create_async_engine(DATABASE_URL, pool_size=5, max_overflow=5)
Session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# WebLib DI
from weblib import WebApp
from weblib.routing import Routes, route, HTTP

routes = Routes()

@route.post("/items")
async def create_item(req):
    data = await req.json()
    di = req.state.setdefault("di", {})
    if "Session" not in di:
        di["Session"] = Session
        await init_db()
    async with di["Session"]() as session:
        i = Item(name=data["name"])
        session.add(i)
        await session.commit()
        await session.refresh(i)
        return HTTP.created({"id": i.id, "name": i.name})

@route.get("/items/{id:int}")
async def get_item(req, id: int):
    Session = req.state.setdefault("di", {}).setdefault("Session", Session)
    async with Session() as session:
        i = (await session.execute(select(Item).where(Item.id == id))).scalar_one_or_none()
        return HTTP.ok({"id": i.id, "name": i.name}) if i else HTTP.ok({"error": "not_found"})

routes.register(create_item, get_item)
app = WebApp(routes=routes)
asgi = app.asgi
```

Implementare un adapter `ORM` (bozza)

Se vuoi un’integrazione uniforme, puoi creare una classe che implementi il Protocol in `weblib.orm.protocol` e incapsuli SQLAlchemy:

```python
from weblib.orm import ORM, Model

class SQLAlchemyORM:
    def __init__(self, engine, Session):
        self.engine = engine
        self.Session = Session

    async def create_database(self): ...
    async def drop_database(self): ...
    async def migrate(self): ...  # integrazione Alembic opzionale
    def session(self):
        return self.Session()  # context manager async
    def repo(self, model: type[Model]):
        return SQLARepository(model, self.Session)
```

Consigli operativi

- Produzione: usa SQLAlchemy async per portabilità (Postgres/SQLite/MySQL) e migrazioni (Alembic).
- Sviluppo veloce: `asyncpg` o `aiosqlite` diretti sono semplici e veloci da configurare.
- Integrazione WebLib: metti engine/pool/session nel DI (`req.state["di"]`) o in `WebApp.provide()` e recuperali nei handler.
