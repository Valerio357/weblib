06 — Blog con Auth + Postgres

Obiettivo: usare l’esempio `examples/blog_auth/app.py` per registrazione/login e post testuali.

Prerequisiti

```
pip install asyncpg
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
```

Avvio

```
uvicorn examples.blog_auth.app:asgi --reload
```

Cosa dimostra

- Uso di `req.state["di"]` come DI minimale per condividere pool DB.
- Sessioni con cookie HttpOnly e redirect dopo login/logout.
- Rendering UI con DSL `E.*` e layout con Bootstrap CDN.
- Gestione errori “dev-friendly”: se `asyncpg` manca, viene mostrata una pagina di aiuto.

Note

- Le password sono salvate con PBKDF2‑HMAC; per produzione usare librerie mature (argon2, rate‑limit, CSRF, ecc.).
- Lo store sessione è in‑memory: in produzione usare backend esterno (es. Redis).

