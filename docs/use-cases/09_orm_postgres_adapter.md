09 — ORM adapter Postgres (asyncpg)

Requisiti

```
pip install asyncpg
export DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

Modello e setup

```python
from weblib.orm import Model, fields, PostgresORM
from weblib import WebApp
from weblib.routing import Routes, route, HTTP

class Item(Model):
    id = fields.Int(pk=True)
    name = fields.Str()

orm = PostgresORM(dsn=os.getenv("DATABASE_URL"))
routes = Routes()

@route.post("/items")
async def create_item(req):
    data = await req.json()
    i = await Item.create(name=data["name"])  # ritorna Record
    return HTTP.created(i.to_dict())

@route.get("/items/{id:int}")
async def get_item(req, id: int):
    i = await Item.get(id=id)
    return HTTP.ok(i.to_dict()) if i else HTTP.ok({"error": "not_found"})

@route.get("/items")
async def list_items(req):
    items = await Item.query().order("id desc").limit(100).all()
    return HTTP.ok([x.to_dict() for x in items])

routes.register(create_item, get_item, list_items)
app = WebApp(routes=routes)
asgi = app.asgi
```

Note

- Usa `asyncpg` e un connection pool interno.
- Le tabelle vengono create on-demand; opzionale `await orm.migrate()` per forzarne la creazione.

