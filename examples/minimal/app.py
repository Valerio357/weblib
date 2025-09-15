from weblib import WebApp
from weblib.routing import Routes, route, HTTP
from weblib.page import Page
from weblib.elements import E
from weblib.css import CSS, css
from weblib.runtime.middleware import security_headers, request_id, logging_middleware, cors, sessions

routes = Routes()

base_css = CSS.scope("base").add(
    css("body", {"font-family": "system-ui", "margin": "0"}),
    css(".container", {"max-width": "720px", "margin": "0 auto", "padding": "24px"}),
)


@route.get("/")
async def home(req):
    return (
        Page(title="Hello WebLib").use_css(base_css).body(
            E.div(
                E.h1("Hello WebLib", cls="text-3xl mb-6"),
                E.p("It works!"),
            ).cls("container")
        )
    )


routes.register(home)

app = WebApp(routes=routes)
app.use(logging_middleware())
app.use(request_id())
app.use(security_headers())
app.use(cors())
app.use(sessions())


@route.get("/session")
async def session_counter(req):
    s = req.state.get("session", {})
    s["count"] = s.get("count", 0) + 1
    return HTTP.ok({"count": s["count"]})

routes.register(session_counter)

asgi = app.asgi

# Run: uvicorn examples.minimal.app:asgi --reload
