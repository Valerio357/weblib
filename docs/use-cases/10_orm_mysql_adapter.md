10 — ORM adapter MySQL (asyncmy/aiomysql)

Requisiti

```
pip install asyncmy
# oppure: pip install aiomysql
export MYSQL_DSN=mysql://user:pass@localhost:3306/dbname
```

Modello e setup

```python
from weblib.orm import Model, fields, MySQLORM
from weblib import WebApp
from weblib.routing import Routes, route, HTTP

class Note(Model):
    id = fields.Int(pk=True)
    body = fields.Text()

orm = MySQLORM(dsn=os.getenv("MYSQL_DSN"))
routes = Routes()

@route.post("/notes")
async def create_note(req):
    data = await req.json()
    n = await Note.create(body=data["body"])
    return HTTP.created(n.to_dict())

@route.get("/notes")
async def list_notes(req):
    notes = await Note.query().order("id desc").limit(50).all()
    return HTTP.ok([x.to_dict() for x in notes])

routes.register(create_note, list_notes)
app = WebApp(routes=routes)
asgi = app.asgi
```

Note

- Supporta `asyncmy` o `aiomysql`; usa automaticamente un DictCursor per avere dict nei risultati.
- Le tabelle vengono create on-demand; opzionale `await orm.migrate()`.

