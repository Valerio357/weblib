from __future__ import annotations

import time
import uuid
from collections import defaultdict, deque
from typing import Any, Awaitable, Callable, Deque, Dict, Tuple

from .asgi import Response
from .adapters import adapt_result


# A handler takes (req, **params) and returns awaitable Any
Handler = Callable[..., Awaitable[Any]]
Middleware = Callable[[Handler], Handler]


def apply_middlewares(handler: Handler, middlewares: list[Middleware]) -> Handler:
    wrapped = handler
    for mw in reversed(middlewares):
        wrapped = mw(wrapped)
    return wrapped


def security_headers(preset: str = "strict") -> Middleware:
    def mw(next_handler: Handler) -> Handler:
        async def _wrapped(req, **params):
            result = await next_handler(req, **params)
            resp = result if isinstance(result, Response) else adapt_result(result)
            # Set common headers (idempotent)
            resp.headers.setdefault("x-content-type-options", "nosniff")
            resp.headers.setdefault("referrer-policy", "no-referrer")
            resp.headers.setdefault("x-frame-options", "DENY")
            resp.headers.setdefault("strict-transport-security", "max-age=31536000; includeSubDomains")
            if preset == "strict":
                resp.headers.setdefault("content-security-policy", "default-src 'self'")
            return resp

        return _wrapped

    return mw


def request_id(header: str = "x-request-id") -> Middleware:
    def mw(next_handler: Handler) -> Handler:
        async def _wrapped(req, **params):
            rid = req.headers.get(header) or uuid.uuid4().hex
            req.state["request_id"] = rid
            result = await next_handler(req, **params)
            resp = result if isinstance(result, Response) else adapt_result(result)
            resp.headers.setdefault(header, rid)
            return resp

        return _wrapped

    return mw


def logging_middleware() -> Middleware:
    def mw(next_handler: Handler) -> Handler:
        async def _wrapped(req, **params):
            start = time.perf_counter()
            try:
                result = await next_handler(req, **params)
                elapsed = (time.perf_counter() - start) * 1000
                # Very small logger
                print(f"{req.method} {req.path} -> ok in {elapsed:.2f}ms")
                return result
            except Exception as exc:
                elapsed = (time.perf_counter() - start) * 1000
                print(f"{req.method} {req.path} -> error {exc!r} in {elapsed:.2f}ms")
                raise

        return _wrapped

    return mw


def cors(
    origin: str | list[str] = "*",
    methods: list[str] | None = None,
    headers: list[str] | None = None,
    credentials: bool = False,
) -> Middleware:
    allow_methods = ", ".join((methods or ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]))
    allow_headers = ", ".join((headers or ["content-type", "authorization"]))
    allow_origin = ", ".join(origin) if isinstance(origin, list) else origin

    def mw(next_handler: Handler) -> Handler:
        async def _wrapped(req, **params):
            if req.method == "OPTIONS":
                resp = Response(b"", status=204)
            else:
                result = await next_handler(req, **params)
                resp = result if isinstance(result, Response) else adapt_result(result)
            resp.headers.setdefault("access-control-allow-origin", allow_origin)
            resp.headers.setdefault("access-control-allow-methods", allow_methods)
            resp.headers.setdefault("access-control-allow-headers", allow_headers)
            if credentials:
                resp.headers.setdefault("access-control-allow-credentials", "true")
            return resp

        return _wrapped

    return mw


def rate_limit(limit: int, window: float, key_fn: Callable[[Any], str] | None = None) -> Middleware:
    buckets: Dict[str, Deque[float]] = defaultdict(deque)

    def default_key(req) -> str:
        # naive IP-based key
        return req.headers.get("x-forwarded-for") or req.scope.get("client", ("",))[0] or "anon"

    kf = key_fn or default_key

    def mw(next_handler: Handler) -> Handler:
        async def _wrapped(req, **params):
            key = kf(req)
            now = time.monotonic()
            q = buckets[key]
            # drop old
            while q and q[0] <= now - window:
                q.popleft()
            if len(q) >= limit:
                return Response.text("Too Many Requests", status=429)
            q.append(now)
            return await next_handler(req, **params)

        return _wrapped

    return mw


# Minimal in-memory sessions (for dev only)
class MemorySessionStore:
    def __init__(self) -> None:
        self._data: Dict[str, Dict[str, Any]] = {}

    def get(self, sid: str) -> Dict[str, Any]:
        return self._data.setdefault(sid, {})


def sessions(cookie_name: str = "session", same_site: str = "Lax", store: MemorySessionStore | None = None) -> Middleware:
    store = store or MemorySessionStore()

    def mw(next_handler: Handler) -> Handler:
        async def _wrapped(req, **params):
            cookies = {}
            cookie_header = req.headers.get("cookie", "")
            for part in cookie_header.split(";"):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    cookies[k] = v
            sid = cookies.get(cookie_name) or uuid.uuid4().hex
            req.state["session"] = store.get(sid)
            result = await next_handler(req, **params)
            resp = result if isinstance(result, Response) else adapt_result(result)
            # set cookie if new
            if cookies.get(cookie_name) != sid:
                attrs = f"; Path=/; HttpOnly; SameSite={same_site}"
                resp.headers.setdefault("set-cookie", f"{cookie_name}={sid}{attrs}")
            return resp

        return _wrapped

    return mw
