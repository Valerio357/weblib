from __future__ import annotations

from typing import Any, AsyncIterable, Mapping, Optional

from ..runtime.asgi import Response


class HTTP:
    @staticmethod
    def ok(body: Any, *, headers: Mapping[str, str] | None = None):
        if isinstance(body, (dict, list)):
            return Response.json(body, status=200, headers=headers)
        if isinstance(body, str):
            return Response.html(body, status=200, headers=headers)
        return Response(str(body).encode("utf-8"), status=200, headers=dict(headers or {}))

    @staticmethod
    def created(body: Any, *, location: str | None = None):
        headers = {}
        if location:
            headers["location"] = location
        if isinstance(body, (dict, list)):
            return Response.json(body, status=201, headers=headers)
        if isinstance(body, str):
            return Response.html(body, status=201, headers=headers)
        return Response(str(body).encode("utf-8"), status=201, headers=headers)

    @staticmethod
    def redirect(location: str, status: int = 302):
        return Response(b"", status=status, headers={"location": location})

    @staticmethod
    def html(markup: str, status: int = 200):
        return Response.html(markup, status=status)

    @staticmethod
    def stream(iterator: AsyncIterable[bytes], *, content_type: str):
        # Minimal streaming support via iterable; for simplicity treat as iterable
        return Response(iterator, status=200, content_type=content_type)

    @staticmethod
    def file(path: str, *, filename: str | None = None):
        # Simple file responder for development use only
        import os
        import mimetypes

        if not os.path.exists(path) or not os.path.isfile(path):
            return Response.text("Not Found", status=404)
        mime, _ = mimetypes.guess_type(path)
        with open(path, "rb") as f:
            data = f.read()
        headers = {}
        if filename:
            headers["content-disposition"] = f"attachment; filename=\"{filename}\""
        return Response(data, status=200, content_type=mime or "application/octet-stream", headers=headers)

