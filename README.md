# WebLib v2 (MVP)

Una libreria Python minimale (ASGI) che segue le specifiche in `specifiche.txt`.

Caratteristiche implementate nell’MVP:
- WebApp con DI minimale, plugin hook, security headers base.
- Routing con decorators (`@route.get`, `@route.post`, ...), path params tipati basilari (`{id:int}`, `{slug}`), `Routes.register`.
- HTTP helpers (`HTTP.ok/created/redirect/html/stream/file`).
- Request/Response ASGI minimi (senza dipendenze esterne).
- Page/Element/Component immutabili, DSL `E.div(...)` con escaping HTML, `Page.render()`.
- CSS scope/merge/minify (no-op) e render compatto.
- Static assets con mount semplice.
- Middleware: `security_headers`, `request_id`, `logging_middleware`, `cors`, `rate_limit`, `sessions` (in-memory, dev-only).
- CLI minimale (`weblib new`, `weblib dev`, `weblib routes`).
- ORM: adapter `SQLiteORM` minimale con `fields` dichiarativi e CRUD base.

Installazione locale:

```bash
pip install -e .
```

Esecuzione esempio minimale:

```bash
uvicorn examples.minimal.app:asgi --reload
```

Esempio Blog con Auth + Postgres:

Requisiti: `asyncpg` e un Postgres in ascolto su 5432.

```bash
pip install asyncpg
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
uvicorn examples.blog_auth.app:asgi --reload
```

Funzionalità:
- Registrazione e Login/Logout (password PBKDF2, cookie sessione in‑memory)
- Creazione post di testo (solo utenti autenticati)
- Lista post come card con autore e timestamp
- Navigazione tramite menu laterale

Esempio rapido:

```python
from weblib import WebApp
from weblib.routing import Routes, route, HTTP
from weblib.page import Page
from weblib.elements import E
from weblib.css import CSS, css

routes = Routes()

base_css = CSS.scope("base").add(
    css("body", {"font-family": "system-ui"}),
    css(".container", {"max-width": "720px", "margin": "0 auto"}),
)

@route.get("/")
async def home(req):
    return (Page(title="Home").use_css(base_css)
            .body(E.div(E.h1("Hello WebLib"), E.p("It works"), cls="container")))

@route.post("/echo")
async def echo(req):
    data = await req.json()
    return HTTP.created({"you_sent": data})

routes.register(home, echo)
app = WebApp(routes=routes)
asgi = app.asgi
# Avvio (es.): uvicorn myapp:asgi --reload
```

Note:
- Questo è un MVP focalizzato sull’API e DX; template, WS/SSE, plugin avanzati e migrazioni evolute sono previsti in future iterazioni.
- Nessuna dipendenza esterna per l’ORM incluso (usa `sqlite3` standard via threadpool). Performance e sicurezza sono “best-effort” per dev.

Licenza: MIT
