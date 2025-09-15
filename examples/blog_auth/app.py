from __future__ import annotations

import os
import secrets
import asyncio
from urllib.parse import parse_qs
from hashlib import pbkdf2_hmac

from weblib import WebApp
from weblib.routing import Routes, route, HTTP
from weblib.page import Page
from weblib.elements import E
from weblib.runtime.middleware import security_headers, request_id, logging_middleware, cors, sessions


DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")


async def get_pool(req):
    try:
        import asyncpg  # type: ignore
    except Exception:
        # Mark missing dependency; routes will render a helpful page
        req.state.setdefault("flags", {})["missing_asyncpg"] = True
        return None

    di = req.state.get("di", {})
    pool = di.get("db_pool")
    if pool is None:
        pool = await asyncpg.create_pool(DATABASE_URL, min_size=1, max_size=5)
        # store in DI
        req.state["di"]["db_pool"] = pool
        # ensure schema
        async with pool.acquire() as conn:
            await conn.execute(
                """
                create table if not exists users (
                    id serial primary key,
                    email text unique not null,
                    password_hash text not null,
                    created_at timestamptz default now()
                );
                create table if not exists posts (
                    id serial primary key,
                    user_id integer not null references users(id) on delete cascade,
                    body text not null,
                    created_at timestamptz default now()
                );
                """
            )
    return pool


def missing_db_page(title: str = "Database non configurato") -> Page:
    help_box = E.div(
        E.h5("PostgreSQL e asyncpg richiesti", cls="card-title"),
        E.p("Installa la dipendenza e configura la variabile DATABASE_URL", cls="card-text"),
        E.pre(
            "pip install asyncpg\nexport DATABASE_URL=postgresql://user:pass@localhost:5432/dbname\n",
            cls="bg-light p-3"
        ),
        E.p("Poi ricarica la pagina."),
        cls="card-body",
    )
    card = E.div(help_box, cls="card")
    return Page(title=title, layout=layout).body(shell(title, card))


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return "pbkdf2$" + salt.hex() + "$" + digest.hex()


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, salt_hex, hash_hex = stored.split("$")
        if algo != "pbkdf2":
            return False
        salt = bytes.fromhex(salt_hex)
        digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return secrets.compare_digest(digest.hex(), hash_hex)
    except Exception:
        return False


routes = Routes()


def layout(page: Page) -> Page:
    return (
        page.head(
            E.link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css")
        ).scripts(
            E.script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js")
        )
    )


def shell(title: str, *content):
    return E.div(
        E.div(
            E.a("WebLib Blog", href="/", cls="navbar-brand"),
            cls="container-fluid",
        ).cls("navbar navbar-dark bg-dark"),
        E.div(
            E.div(
                E.ul(
                    E.li(E.a("Home", href="/", cls="nav-link"), cls="nav-item"),
                    E.li(E.a("Posts", href="/posts", cls="nav-link"), cls="nav-item"),
                    E.li(E.a("Register", href="/register", cls="nav-link"), cls="nav-item"),
                    E.li(E.a("Login", href="/login", cls="nav-link"), cls="nav-item"),
                    E.li(E.form(E.button("Logout", type="submit", cls="btn btn-link p-0 nav-link"), method="POST", action="/logout"), cls="nav-item"),
                    cls="nav flex-column nav-pills",
                ),
                cls="col-3",
            ),
            E.div(
                E.h1(title, cls="mb-4"),
                *content,
                cls="col-9",
            ),
            cls="row mt-4",
        ).cls("container")
    )


@route.get("/")
async def home(req):
    s = req.state.get("session", {})
    user_id = s.get("user_id")
    left = E.div(
        E.p("Benvenuto!" if not user_id else f"Sei autenticato (user {user_id})."),
        E.p("Usa il menu a sinistra per navigare."),
    )
    return Page(title="Home", layout=layout).body(shell("Home", left))


@route.get("/register")
async def register_form(req):
    form = E.form(
        E.div(E.label("Email", for_="email", cls="form-label"), E.input(type="email", name="email", id="email", cls="form-control"), cls="mb-3"),
        E.div(E.label("Password", for_="password", cls="form-label"), E.input(type="password", name="password", id="password", cls="form-control"), cls="mb-3"),
        E.button("Crea account", type="submit", cls="btn btn-primary"),
        method="POST", action="/register"
    )
    return Page(title="Register", layout=layout).body(shell("Register", form))


@route.post("/register")
async def register_submit(req):
    pool = await get_pool(req)
    if pool is None:
        return missing_db_page("Register")
    raw = (await req.body()).decode("utf-8")
    data = {k: v[0] if isinstance(v, list) and v else v for k, v in parse_qs(raw).items()}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return HTTP.html("<p>Missing email or password</p>", status=400)
    pwd = hash_password(password)
    async with pool.acquire() as conn:
        try:
            row = await conn.fetchrow("insert into users(email, password_hash) values($1, $2) returning id", email, pwd)
        except Exception as e:
            return HTTP.html("<p>Email già registrata</p>", status=400)
    req.state["session"]["user_id"] = row["id"]
    return HTTP.redirect("/posts")


@route.get("/login")
async def login_form(req):
    form = E.form(
        E.div(E.label("Email", for_="email", cls="form-label"), E.input(type="email", name="email", id="email", cls="form-control"), cls="mb-3"),
        E.div(E.label("Password", for_="password", cls="form-label"), E.input(type="password", name="password", id="password", cls="form-control"), cls="mb-3"),
        E.button("Login", type="submit", cls="btn btn-primary"),
        method="POST", action="/login"
    )
    return Page(title="Login", layout=layout).body(shell("Login", form))


@route.post("/login")
async def login_submit(req):
    pool = await get_pool(req)
    if pool is None:
        return missing_db_page("Login")
    raw = (await req.body()).decode("utf-8")
    data = {k: v[0] if isinstance(v, list) and v else v for k, v in parse_qs(raw).items()}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("select id, password_hash from users where email=$1", email)
    if not row or not verify_password(password, row["password_hash"]):
        return HTTP.html("<p>Credenziali non valide</p>", status=401)
    req.state["session"]["user_id"] = row["id"]
    return HTTP.redirect("/posts")


@route.post("/logout")
async def logout(req):
    req.state.get("session", {}).pop("user_id", None)
    return HTTP.redirect("/")


@route.get("/posts")
async def list_posts(req):
    pool = await get_pool(req)
    if pool is None:
        return missing_db_page("Posts")
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            "select p.id, p.body, p.created_at, u.email from posts p join users u on u.id=p.user_id order by p.created_at desc limit 100"
        )
    cards = [
        E.div(
            E.div(
                E.h5(r["email"], cls="card-title"),
                E.p(r["body"], cls="card-text"),
                E.small(str(r["created_at"]), cls="text-muted"),
                cls="card-body",
            ),
            cls="card mb-3",
        )
        for r in rows
    ]

    s = req.state.get("session", {})
    create_form = (
        E.form(
            E.div(E.label("Nuovo post", for_="body", cls="form-label"), E.textarea(name="body", id="body", cls="form-control", rows="3"), cls="mb-3"),
            E.button("Pubblica", type="submit", cls="btn btn-success"),
            method="POST", action="/posts"
        )
        if s.get("user_id") else E.div(E.a("Login per postare", href="/login", cls="btn btn-outline-primary"))
    )

    content = E.div(create_form, *cards)
    return Page(title="Posts", layout=layout).body(shell("Posts", content))


@route.post("/posts")
async def create_post(req):
    s = req.state.get("session", {})
    user_id = s.get("user_id")
    if not user_id:
        return HTTP.redirect("/login")
    raw = (await req.body()).decode("utf-8")
    data = {k: v[0] if isinstance(v, list) and v else v for k, v in parse_qs(raw).items()}
    body = (data.get("body") or "").strip()
    if not body:
        return HTTP.html("<p>Testo mancante</p>", status=400)
    pool = await get_pool(req)
    if pool is None:
        return missing_db_page("Posts")
    async with pool.acquire() as conn:
        await conn.execute("insert into posts(user_id, body) values($1, $2)", int(user_id), body)
    return HTTP.redirect("/posts")


routes.register(
    home,
    register_form,
    register_submit,
    login_form,
    login_submit,
    logout,
    list_posts,
    create_post,
)


app = WebApp(routes=routes)
app.use(logging_middleware())
app.use(request_id())
# Use a basic security preset (no strict CSP) so CDN assets load
app.use(security_headers(preset="basic"))
app.use(cors())
app.use(sessions())

asgi = app.asgi

# Run:
#   export DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
#   uvicorn examples.blog_auth.app:asgi --reload
