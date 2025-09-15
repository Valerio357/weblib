from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from .routing.core import Router, Routes
from .assets.static import Static
from .runtime.asgi import ASGIApp, Request, Response
from .runtime.adapters import adapt_result
from .runtime.middleware import Middleware, apply_middlewares


@dataclass
class WebAppConfig:
    debug: bool = False
    base_url: str | None = None
    secrets: Dict[str, str] = field(default_factory=dict)
    cors: Dict[str, Any] | None = None
    security_headers: bool = True
    gzip: bool = False
    brotli: bool = False
    etags: bool = True
    max_body_size: int | None = 2 * 1024 * 1024
    logging: bool = True


class WebApp:
    def __init__(
        self,
        routes: "Routes" | None = None,
        orm: Any | None = None,
        static: "Static" | None = None,
        config: WebAppConfig | None = None,
    ) -> None:
        self.config = config or WebAppConfig()
        self._container: Dict[str, Any] = {}
        self._plugins: list[Any] = []
        self.routes = routes or Routes()
        self.router = Router(self.routes)
        self.orm = orm
        self.static = static
        self.middlewares: list[Middleware] = []

        # Compose ASGI app
        async def app(scope, receive, send):
            if scope["type"] != "http":
                # Only basic HTTP supported in MVP
                await Response.text("Not Implemented", status=501)(scope, receive, send)
                return

            # Static handling (very simple mount)
            path = scope.get("path", "")
            if self.static and path.startswith(self.static.mount):
                await self.static.asgi(scope, receive, send)
                return

            req = Request(scope, receive)
            try:
                handler, params, route_mw = self.router.match(req.method, path)
            except LookupError:
                await Response.text("Not Found", status=404)(scope, receive, send)
                return

            # Dependency injection: attach app and container to request
            req.state["app"] = self
            req.state["di"] = self._container

            # Compose middlewares (global + route-level)
            wrapped = apply_middlewares(handler, [*self.middlewares, *route_mw])
            result = await wrapped(req, **params)

            # Normalize result to ASGI response
            resp = adapt_result(result)

            # Security headers baseline
            if self.config.security_headers:
                resp.headers.setdefault("X-Content-Type-Options", "nosniff")
                resp.headers.setdefault("Referrer-Policy", "no-referrer")
                resp.headers.setdefault("X-Frame-Options", "DENY")
                resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

            await resp(scope, receive, send)

        self._asgi = app

    async def on_startup(self) -> None:  # hooks for future use
        pass

    async def on_shutdown(self) -> None:
        pass

    # DI minimal
    def provide(self, key: str, value: object) -> None:
        self._container[key] = value

    def get(self, key: str) -> object:
        return self._container[key]

    # Extension points
    def register_plugin(self, plugin: Any) -> None:
        self._plugins.append(plugin)
        setup = getattr(plugin, "setup", None)
        if callable(setup):
            setup(self)

    # Middleware registration
    def use(self, middleware: Middleware) -> None:
        self.middlewares.append(middleware)

    # ASGI
    @property
    def asgi(self) -> ASGIApp:
        return self._asgi
