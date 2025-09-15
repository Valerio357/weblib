from __future__ import annotations

import mimetypes
import os
from typing import Any, Dict

from ..runtime.asgi import Response


class Static:
    def __init__(self, directory: str, mount: str = "/static", versioned: bool = True) -> None:
        self.directory = os.path.abspath(directory)
        self.mount = mount.rstrip("/") or "/static"
        self.versioned = versioned

    async def asgi(self, scope, receive, send):
        path = scope.get("path", "")
        rel = path[len(self.mount) :].lstrip("/")
        # prevent path traversal
        full = os.path.abspath(os.path.join(self.directory, rel))
        if not full.startswith(self.directory) or not os.path.isfile(full):
            await Response.text("Not Found", status=404)(scope, receive, send)
            return
        mime, _ = mimetypes.guess_type(full)
        with open(full, "rb") as f:
            data = f.read()
        headers = {"cache-control": "public, max-age=3600"}
        await Response(data, status=200, content_type=mime or "application/octet-stream", headers=headers)(scope, receive, send)

