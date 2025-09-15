Architettura (MVP)

Obiettivo: offrire un set minimale ma coerente per costruire web app server‑side in Python (ASGI), con routing, rendering HTML dichiarativo, CSS inline scoping, middleware basilari e utilità HTTP.

Moduli principali

- `weblib.app`:
  - `WebApp`, `WebAppConfig`: contenitore dell’applicazione; compone router, static assets, middleware e normalizza le risposte.
  - Espone `app.asgi` per l’esecuzione con Uvicorn/Hypercorn.

- `weblib.runtime`:
  - `asgi.py`: Request/Response minimi, tipizzati; helpers `html/json/text`.
  - `adapters.py`: `adapt_result` converte Page/dict/str in `Response`.
  - `middleware.py`: middleware inclusi: `security_headers`, `request_id`, `logging_middleware`, `cors`, `rate_limit`, `sessions` (in‑memory, dev-only).

- `weblib.routing`:
  - `core.py`: `Routes`, `Router`, decorator `route.get/post/...`, path params tipati (es. `{id:int}`).
  - `responses.py`: helper HTTP (`HTTP.ok/created/redirect/html/stream/file`).

- `weblib.page`:
  - `page.py`: `Page` immutabile con `head/body/scripts/use_css` e `render()`.

- `weblib.elements`:
  - `core.py`: DSL HTML con `E.div(...)`, `Element`, `Component`, `Var`, escaping HTML by default.

- `weblib.css`:
  - `css.py`: `CSS` e `css()` per regole, merge e render compatto inline via `<style>`.

- `weblib.assets`:
  - `static.py`: server statico semplice, montato su prefisso (default `/static`).

- `weblib.cli`:
  - `main.py`: CLI minima `weblib new/dev/routes`.

Flusso di richiesta (semplificato)

1) ASGI chiama `WebApp.asgi(scope, receive, send)`.
2) Se il path è sotto `Static.mount`, serve l’asset; altrimenti crea `Request`.
3) `Router.match()` trova handler + parametri + middleware di route.
4) Applica middleware globali+di‑route e invoca l’handler.
5) `adapt_result` normalizza il risultato in `Response` (Page/JSON/HTML/testo).
6) Applica security headers base e invia la risposta.

Mappa responsabilità

- Routing: definizione dichiarativa con decorators e registrazione via `Routes.register()`.
- Rendering: `Page` + DSL `E.*` per HTML sicuro, CSS inline via `CSS.render()`.
- Middleware: composizione semplice funzione→funzione, esempi inclusi.
- Static: montaggio directory con protezione path traversal.

Differenze rispetto alle specifiche complete

- ORM/protocol, templates Jinja, WS/SSE e plugin avanzati sono fuori dall’MVP.
- Sessioni sono in‑memory per sviluppo.
- Dev server integrato non incluso; usare Uvicorn.

