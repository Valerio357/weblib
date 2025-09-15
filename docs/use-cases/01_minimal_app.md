01 — App minima

Obiettivo: definire una rotta, restituire una pagina HTML e avviare con Uvicorn.

Codice

```python
from weblib import WebApp
from weblib.routing import Routes, route
from weblib.page import Page
from weblib.elements import E

routes = Routes()

@route.get("/")
async def home(req):
    return Page(title="Hello").body(E.div(E.h1("Hello WebLib")))

routes.register(home)
app = WebApp(routes=routes)
asgi = app.asgi
```

Esecuzione

```
uvicorn myapp:asgi --reload
```

Note

- Gli handler possono restituire `Page`, `str`, `dict/list` (→ JSON) o `Response`.
- Le risposte sono normalizzate automaticamente da `adapt_result`.

