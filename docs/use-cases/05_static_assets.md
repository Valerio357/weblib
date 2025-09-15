05 — Static assets

Obiettivo: servire file statici (es. CSS/JS/immagini) da una directory.

Setup

```python
from weblib import WebApp
from weblib.assets import Static
from weblib.routing import Routes, route

routes = Routes()

@route.get("/")
async def home(req):
    from weblib.page import Page
    from weblib.elements import E
    return Page(title="Static").body(E.link(rel="stylesheet", href="/static/app.css"))

routes.register(home)

static = Static("static", mount="/static")  # cartella locale ./static
app = WebApp(routes=routes, static=static)
asgi = app.asgi
```

Note

- Il server statico imposta `Cache-Control: public, max-age=3600`.
- È prevenuto il path traversal; solo file sotto la directory configurata vengono serviti.

