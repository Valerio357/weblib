WebLib v2 — Documentazione (MVP)

Questa cartella raccoglie una panoramica dell'architettura e una serie di use case pratici per capire e usare la codebase.

- Panoramica architetturale: vedere `docs/architettura.md`
- CLI: comandi e flusso: vedere `docs/cli.md`
- Use case guidati: indice in `docs/use-cases/README.md`

Installazione locale

```
pip install -e .
```

Esecuzione esempi inclusi

```
# Esempio minimale
uvicorn examples.minimal.app:asgi --reload

# Esempio Blog con Auth + Postgres (richiede asyncpg e DATABASE_URL)
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
pip install asyncpg
uvicorn examples.blog_auth.app:asgi --reload
```

Struttura della repo (MVP)

- `weblib/`: libreria principale (ASGI, routing, page/elements, css, assets, middleware, CLI)
- `examples/`: app di esempio pronte all'uso
- `mysite/`: progetto di esempio con Bootstrap
- `specifiche.txt`: specifica ampia, l’MVP implementa un sottoinsieme

