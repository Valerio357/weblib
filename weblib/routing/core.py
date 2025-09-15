from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Pattern, Tuple

from ..runtime.asgi import Request

Handler = Callable[..., Awaitable[Any]]
Middleware = Callable[[Handler], Handler]


@dataclass
class Route:
    method: str
    path_template: str
    pattern: Pattern[str]
    param_converters: Dict[str, Callable[[str], Any]]
    handler: Handler
    name: Optional[str] = None
    middlewares: List[Middleware] | None = None


class Router:
    def __init__(self, routes: "Routes") -> None:
        self._routes: List[Route] = routes._routes

    def match(self, method: str, path: str) -> tuple[Handler, dict[str, Any], List[Middleware]]:
        method = method.upper()
        for r in self._routes:
            if r.method != method:
                continue
            m = r.pattern.fullmatch(path)
            if not m:
                continue
            params = {k: r.param_converters.get(k, lambda s: s)(v) for k, v in m.groupdict().items()}
            return r.handler, params, (r.middlewares or [])
        raise LookupError("No route matched")


class route:
    @staticmethod
    def _make(method: str, path: str, *, name: str | None = None):
        def decorator(func: Handler) -> Handler:
            # attach route spec to function for later registration
            specs: list[tuple[str, str, str | None]] = getattr(func, "_route_specs", [])
            specs.append((method.upper(), path, name))
            setattr(func, "_route_specs", specs)
            return func
        return decorator

    @staticmethod
    def get(path: str, *, name: str | None = None):
        return route._make("GET", path, name=name)

    @staticmethod
    def post(path: str, *, name: str | None = None):
        return route._make("POST", path, name=name)

    @staticmethod
    def put(path: str, *, name: str | None = None):
        return route._make("PUT", path, name=name)

    @staticmethod
    def patch(path: str, *, name: str | None = None):
        return route._make("PATCH", path, name=name)

    @staticmethod
    def delete(path: str, *, name: str | None = None):
        return route._make("DELETE", path, name=name)

    @staticmethod
    def websocket(path: str, *, name: str | None = None):
        # placeholder for future ws support
        return route._make("WEBSOCKET", path, name=name)


CONVERTERS: dict[str, Callable[[str], Any]] = {
    "int": int,
    "str": str,
    "bool": lambda s: s.lower() in {"1", "true", "yes", "on"},
}


def compile_path(path: str) -> tuple[Pattern[str], Dict[str, Callable[[str], Any]]]:
    # Convert /users/{id:int}/posts/{slug:str} -> regex with named groups
    param_converters: Dict[str, Callable[[str], Any]] = {}

    def repl(match: re.Match[str]) -> str:
        name = match.group("name")
        conv = match.group("conv") or "str"
        param_converters[name] = CONVERTERS.get(conv, str)
        if conv == "int":
            return fr"(?P<{name}>\d+)"
        # default str: accept anything until next /
        return fr"(?P<{name}>[^/]+)"

    pattern_str = re.sub(r"\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\:(?P<conv>[a-z]+)\}", repl, path)
    pattern_str = re.sub(r"\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\}", lambda m: fr"(?P<{m.group('name')}>[^/]+)", pattern_str)
    pattern = re.compile("^" + pattern_str.rstrip("/") + "/*$")
    return pattern, param_converters


class Routes:
    def __init__(self, prefix: str = "", middlewares: list[Callable] | None = None) -> None:
        self.prefix = prefix.rstrip("/")
        self.middlewares: List[Middleware] = middlewares or []
        self._routes: List[Route] = []

    def include(self, other: "Routes") -> None:
        for r in other._routes:
            self._routes.append(r)

    def use(self, middleware: Middleware) -> None:
        self.middlewares.append(middleware)

    def register(self, *handlers: Handler) -> None:
        for h in handlers:
            specs = getattr(h, "_route_specs", None)
            if not specs:
                raise ValueError(f"Handler {h.__name__} has no @route decorator")
            for method, path, name in specs:
                full_path = f"{self.prefix}{path if path.startswith('/') else '/' + path}"
                pattern, converters = compile_path(full_path)
                self._routes.append(Route(method, full_path, pattern, converters, h, name=name, middlewares=list(self.middlewares)))
