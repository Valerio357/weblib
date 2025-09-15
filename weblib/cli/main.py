from __future__ import annotations

import argparse
import os
import sys


def cmd_new(args: argparse.Namespace) -> int:
    name = args.name
    os.makedirs(name, exist_ok=True)
    app_py = os.path.join(name, "app.py")
    if not os.path.exists(app_py):
        with open(app_py, "w", encoding="utf-8") as f:
            f.write(
                """
from weblib import WebApp
from weblib.routing import Routes, route
from weblib.page import Page
from weblib.elements import E
from weblib.css import CSS, css

routes = Routes()

base_css = CSS.scope("base").add(
    css("body", {"font-family": "system-ui", "margin": "0"}),
    css(".container", {"max-width": "720px", "margin": "0 auto", "padding": "24px"}),
)

@route.get("/")
async def home(req):
    page = (Page(title="Hello WebLib")
            .use_css(base_css)
            .body(E.div(
                E.h1("Hello WebLib", cls="text-3xl mb-6"),
                E.p("It works!"),
            ).cls("container")))
    return page

routes.register(home)

app = WebApp(routes=routes)
asgi = app.asgi
                """.strip()
            )
    print(f"Project created in {name}")
    return 0


def cmd_routes(args: argparse.Namespace) -> int:
    print("Routes inspection is minimal in MVP.")
    return 0


def cmd_dev(args: argparse.Namespace) -> int:
    print("Dev server not bundled; run with `uvicorn app:asgi --reload` in your project.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("weblib")
    sub = p.add_subparsers(dest="cmd")

    p_new = sub.add_parser("new", help="Create a new project")
    p_new.add_argument("name")
    p_new.set_defaults(func=cmd_new)

    p_dev = sub.add_parser("dev", help="Run dev server (hint)")
    p_dev.set_defaults(func=cmd_dev)

    p_routes = sub.add_parser("routes", help="Show routes (placeholder)")
    p_routes.set_defaults(func=cmd_routes)

    return p


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    p = build_parser()
    args = p.parse_args(argv)
    if not hasattr(args, "func"):
        p.print_help()
        return 1
    return int(args.func(args) or 0)


if __name__ == "__main__":
    raise SystemExit(main())

