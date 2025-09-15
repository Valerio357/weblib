from __future__ import annotations

import json
from typing import Any, Awaitable, Callable, Dict, Iterable, Mapping, MutableMapping, Optional

Scope = Dict[str, Any]
Receive = Callable[[], Awaitable[Dict[str, Any]]]
Send = Callable[[Dict[str, Any]], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


class Request:
    def __init__(self, scope: Scope, receive: Receive) -> None:
        self.scope = scope
        self._receive = receive
        self.state: Dict[str, Any] = {}
        self._body: Optional[bytes] = None

    @property
    def method(self) -> str:
        return self.scope.get("method", "GET").upper()

    @property
    def path(self) -> str:
        return self.scope.get("path", "/")

    @property
    def headers(self) -> Mapping[str, str]:
        raw = self.scope.get("headers", [])
        # ASGI headers are list[tuple[bytes, bytes]]
        return {k.decode().lower(): v.decode() for k, v in raw}

    @property
    def query_string(self) -> str:
        return (self.scope.get("query_string") or b"").decode()

    async def body(self) -> bytes:
        if self._body is None:
            chunks: list[bytes] = []
            more = True
            while more:
                event = await self._receive()
                assert event["type"] == "http.request"
                if event.get("body"):
                    chunks.append(event["body"])
                more = event.get("more_body", False)
            self._body = b"".join(chunks)
        return self._body

    async def json(self) -> Any:
        return json.loads((await self.body()).decode() or "null")


class Response:
    def __init__(
        self,
        body: bytes | Iterable[bytes] | None = None,
        *,
        status: int = 200,
        content_type: str | None = None,
        headers: Optional[MutableMapping[str, str]] = None,
    ) -> None:
        self.status = status
        self.body = body if body is not None else b""
        self.headers: MutableMapping[str, str] = {k.lower(): v for k, v in (headers or {}).items()}
        if content_type:
            self.headers.setdefault("content-type", content_type)

    def __call__(self, scope: Scope, receive: Receive, send: Send):
        return self._send(scope, receive, send)

    async def _send(self, scope: Scope, receive: Receive, send: Send):
        await send(
            {
                "type": "http.response.start",
                "status": self.status,
                "headers": [(k.encode(), v.encode()) for k, v in self.headers.items()],
            }
        )
        if isinstance(self.body, (bytes, bytearray)):
            await send({"type": "http.response.body", "body": bytes(self.body), "more_body": False})
        else:
            # iterable streaming
            async def _aiter():
                for chunk in self.body:  # type: ignore[attr-defined]
                    yield chunk

            async for chunk in _aiter():
                await send({"type": "http.response.body", "body": chunk, "more_body": True})
            await send({"type": "http.response.body", "body": b"", "more_body": False})

    # Helpers
    @staticmethod
    def html(markup: str, *, status: int = 200, headers: Optional[Mapping[str, str]] = None) -> "Response":
        return Response(markup.encode("utf-8"), status=status, content_type="text/html; charset=utf-8", headers=dict(headers or {}))

    @staticmethod
    def json(data: Any, *, status: int = 200, headers: Optional[Mapping[str, str]] = None) -> "Response":
        return Response(json.dumps(data, separators=(",", ":")).encode("utf-8"), status=status, content_type="application/json", headers=dict(headers or {}))

    @staticmethod
    def text(text: str, *, status: int = 200, headers: Optional[Mapping[str, str]] = None) -> "Response":
        return Response(text.encode("utf-8"), status=status, content_type="text/plain; charset=utf-8", headers=dict(headers or {}))

