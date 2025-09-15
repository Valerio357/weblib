from weblib import WebApp
from weblib.routing import Routes, route, HTTP
from weblib.page import Page
from weblib.elements import E
from weblib.css import CSS, css
from urllib.parse import parse_qs

routes = Routes()

base_css = CSS.scope("base").add(
    css("body", {"font-family": "system-ui"}),
)

@route.get("/")
async def home(req):
    # Sample data for table
    users = [
        {"id": 1, "name": "Alice", "email": "alice@example.com"},
        {"id": 2, "name": "Bob", "email": "bob@example.com"},
        {"id": 3, "name": "Carol", "email": "carol@example.com"},
    ]

    page = (
        Page(title="WebLib + Bootstrap")
        .use_css(base_css)
        .head(
            E.link(
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
            )
        )
        .body(
            E.nav(
                E.div(
                    E.a("WebLib", href="#", cls="navbar-brand"),
                ).cls("container-fluid"),
                cls="navbar navbar-expand-lg navbar-dark bg-dark",
            ),
            E.main(
                E.div(
                    E.h1("Esempi Bootstrap", cls="my-4"),

                    # Grid: 3 colonne
                    E.div(
                        E.div(
                            E.div(
                                E.h5("Colonna 1", cls="card-title"),
                                E.p("Contenuto della prima colonna", cls="card-text"),
                                cls="card-body",
                            ),
                            cls="card h-100",
                        ).cls("col-md-4 mb-3"),
                        E.div(
                            E.div(
                                E.h5("Colonna 2", cls="card-title"),
                                E.p("Seconda colonna con altro testo", cls="card-text"),
                                cls="card-body",
                            ),
                            cls="card h-100",
                        ).cls("col-md-4 mb-3"),
                        E.div(
                            E.div(
                                E.h5("Colonna 3", cls="card-title"),
                                E.p("Terza colonna con card", cls="card-text"),
                                cls="card-body",
                            ),
                            cls="card h-100",
                        ).cls("col-md-4 mb-3"),
                        cls="row",
                    ),

                    # Tabella
                    E.h2("Tabella utenti", cls="mt-4"),
                    E.table(
                        E.thead(
                            E.tr(
                                E.th("ID"), E.th("Nome"), E.th("Email")
                            )
                        ),
                        E.tbody(
                            *[
                                E.tr(
                                    E.td(u["id"]), E.td(u["name"]), E.td(u["email"])
                                )
                                for u in users
                            ]
                        ),
                        cls="table table-striped",
                    ),

                    # Form
                    E.h2("Form di esempio", cls="mt-4"),
                    E.form(
                        E.div(
                            E.label("Nome", for_="name", cls="form-label"),
                            E.input(type="text", name="name", id="name", cls="form-control", placeholder="Mario Rossi"),
                            cls="mb-3",
                        ),
                        E.div(
                            E.label("Email", for_="email", cls="form-label"),
                            E.input(type="email", name="email", id="email", cls="form-control", placeholder="mario@example.com"),
                            cls="mb-3",
                        ),
                        E.div(
                            E.label("Ruolo", for_="role", cls="form-label"),
                            E.select(
                                E.option("User", value="user"),
                                E.option("Admin", value="admin"),
                                name="role",
                                id="role",
                                cls="form-select",
                            ),
                            cls="mb-3",
                        ),
                        E.div(
                            E.input(type="checkbox", name="terms", id="terms", cls="form-check-input"),
                            E.label("Accetto i termini", for_="terms", cls="form-check-label ms-2"),
                            cls="form-check mb-3",
                        ),
                        E.button("Invia", type="submit", cls="btn btn-primary"),
                        method="POST",
                        action="/submit",
                        cls="mt-2",
                    ),
                    cls="container",
                ),
            ),
        )
        .scripts(
            E.script(src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js")
        )
    )
    return page


@route.post("/submit")
async def submit(req):
    raw = (await req.body()).decode("utf-8")
    parsed = {k: v[0] if isinstance(v, list) and v else v for k, v in parse_qs(raw).items()}
    alert = E.div(
        E.strong("Dati inviati: "), E.pre(str(parsed), cls="m-0"),
        cls="alert alert-success",
    )
    page = (
        Page(title="Form inviato")
        .head(
            E.link(
                rel="stylesheet",
                href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css",
            )
        )
        .body(E.div(E.h1("Risultato"), alert, E.a("Torna alla home", href="/", cls="btn btn-link mt-3"), cls="container py-4"))
    )
    return page

routes.register(home, submit)

app = WebApp(routes=routes)
asgi = app.asgi
