08 — ORM adapter SQLite (incluso)

Stato: incluso nella libreria come `weblib.orm.SQLiteORM`, con `fields` dichiarativi e binding helper sul `Model`.

Definizione modello

```python
from weblib.orm import Model, fields

class Todo(Model):
    id = fields.Int(pk=True)
    title = fields.Str()
    done = fields.Bool(default=False)
```

Setup ORM e DI

```python
from weblib.orm import SQLiteORM
from weblib import WebApp
from weblib.routing import Routes, route, HTTP

orm = SQLiteORM(path="./app.db")
routes = Routes()

@route.post("/todos")
async def create_todo(req):
    data = await req.json()
    # Usa i metodi bindati sul Model: create/get/query
    t = await Todo.create(title=data["title"], done=bool(data.get("done", False)))
    return HTTP.created(t.to_dict())

@route.get("/todos/{id:int}")
async def get_todo(req, id: int):
    t = await Todo.get(id=id)
    return HTTP.ok(t.to_dict()) if t else HTTP.ok({"error": "not_found"})

@route.get("/todos")
async def list_todos(req):
    items = await Todo.query().order("id desc").limit(100).all()
    return HTTP.ok([x.to_dict() for x in items])

@route.patch("/todos/{id:int}")
async def update_todo(req, id: int):
    data = await req.json()
    t = await Todo.get(id=id)
    if not t:
        return HTTP.ok({"error": "not_found"})
    await t.update(**{k: v for k, v in data.items() if k in {"title", "done"}})
    return HTTP.ok(t.to_dict())

@route.delete("/todos/{id:int}")
async def delete_todo(req, id: int):
    t = await Todo.get(id=id)
    if t:
        await t.delete()
    return HTTP.ok({"ok": True})

routes.register(create_todo, get_todo, list_todos, update_todo, delete_todo)

app = WebApp(routes=routes)
asgi = app.asgi
```

Dettagli tecnici

- Tipi supportati: `Int/Str/Text/Bool/Datetime/ForeignKey` (FK come `INTEGER`, senza enforcement on_delete nell’MVP).
- Creazione tabelle: on-demand al primo accesso; opzionale `await orm.migrate()` per preparare tutto.
- Async: usa `sqlite3` standard in threadpool (`asyncio.to_thread`).
- Record: i metodi `create/get/query` restituiscono `Record` con `update()`/`delete()` e `to_dict()`.

Nota

- L’API copre lo use case CRUD base. Per progetti complessi, valuta SQLAlchemy async come backend alternativo.

