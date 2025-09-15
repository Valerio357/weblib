11 — Autenticazione (weblib.auth)

Funzionalità incluse

- `hash_password(password)`: PBKDF2‑HMAC‑SHA256 con salt e iterazioni (200k)
- `verify_password(password, stored)`: verifica costante
- `login_user(req, user_id)`: salva l’id utente nella sessione
- `logout_user(req)`: rimuove l’utente dalla sessione
- `current_user_id(req)`: legge l’utente corrente
- `require_login(redirect_to="/login")`: middleware di route per richiedere login

Esempio

```python
from weblib import WebApp
from weblib.routing import Routes, route
from weblib.runtime.middleware import sessions
from weblib import hash_password, verify_password, login_user, logout_user, current_user_id, require_login

routes = Routes()

@route.post("/login")
async def login(req):
    data = await req.json()
    # recupera user e hash dal DB (omesso)
    if verify_password(data["password"], stored_hash):
        login_user(req, user_id)
        return HTTP.redirect("/")
    return HTTP.html("<p>Invalid</p>", status=401)

@route.get("/secret")
@require_login("/login")
async def secret(req):
    return HTTP.ok({"user": current_user_id(req)})

routes.register(login, secret)
app = WebApp(routes=routes)
app.use(sessions())
asgi = app.asgi
```

Nota

- Per usare `login_user`/`current_user_id` serve il middleware `sessions()`.
- Per production, valutare header di sicurezza più restrittivi e rate limiting su login.

