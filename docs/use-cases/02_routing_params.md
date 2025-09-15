02 — Routing e parametri

Obiettivo: usare path params tipati e leggere query/body.

Path params

```python
from weblib.routing import Routes, route, HTTP

routes = Routes()

@route.get("/users/{id:int}")
async def show_user(req, id: int):
    return HTTP.ok({"user_id": id})

routes.register(show_user)
```

Query string e body JSON

```python
@route.get("/search")
async def search(req):
    # accesso grezzo alla query string
    qs = req.query_string
    return HTTP.ok({"q": qs})

@route.post("/echo")
async def echo(req):
    data = await req.json()
    return HTTP.created({"you_sent": data})
```

Note

- Converter disponibili: `int`, `str` (default), `bool`.
- Il path matcher accetta trailing slash opzionale.

