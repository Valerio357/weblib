from __future__ import annotations

from typing import Any

from .asgi import Response
from ..page.page import Page


def adapt_result(result: Any) -> Response:
    if isinstance(result, Response):
        return result
    if isinstance(result, Page):
        return Response.html(result.render())
    if isinstance(result, (dict, list)):
        return Response.json(result)
    if isinstance(result, str):
        return Response.html(result)
    if result is None:
        return Response.text("")
    return Response.text(str(result))

