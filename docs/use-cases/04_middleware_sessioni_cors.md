04 — Middleware: logging, security, CORS, sessioni

Obiettivo: applicare middleware globali e usare una sessione in‑memory.

Setup middleware

```python
from weblib import WebApp
from weblib.routing import Routes, route, HTTP
from weblib.runtime.middleware import (
    logging_middleware, request_id, security_headers, cors, sessions
)

routes = Routes()

@route.get("/session")
async def session_counter(req):
    s = req.state.get("session", {})
    s["count"] = s.get("count", 0) + 1
    return HTTP.ok({"count": s["count"]})

routes.register(session_counter)

app = WebApp(routes=routes)
app.use(logging_middleware())
app.use(request_id())
app.use(security_headers())
app.use(cors())
app.use(sessions())
asgi = app.asgi
```

Note

- `sessions()` usa cookie HttpOnly e store in‑memory: adatto solo a sviluppo.
- `cors()` risponde anche alle `OPTIONS` preflight.
- `security_headers()` aggiunge header safe‑by‑default; preset `strict` imposta anche una CSP base.

