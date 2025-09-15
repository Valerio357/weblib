from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Protocol, Any, Tuple

from ..elements.core import Element, render_node


class Layout(Protocol):
    def __call__(self, page: "Page") -> "Page": ...


@dataclass(frozen=True)
class Page:
    title: str = ""
    layout: type[Layout] | None = None
    lang: str = "en"
    _meta: dict[str, str] = None  # type: ignore[assignment]
    _head: Tuple[Element, ...] = ()
    _body: Tuple[Element, ...] = ()
    _scripts: Tuple[Element, ...] = ()
    _css: Tuple[Any, ...] = ()  # CSS objects with render()

    def __post_init__(self):
        if self._meta is None:
            object.__setattr__(self, "_meta", {})

    def meta(self, **tags) -> "Page":
        new = dict(self._meta)
        new.update({k.replace("_", "-"): str(v) for k, v in tags.items()})
        return replace(self, _meta=new)

    def head(self, *nodes: Element) -> "Page":
        return replace(self, _head=tuple(self._head) + tuple(nodes))

    def body(self, *nodes: Element) -> "Page":
        return replace(self, _body=tuple(self._body) + tuple(nodes))

    def scripts(self, *nodes: Element) -> "Page":
        return replace(self, _scripts=tuple(self._scripts) + tuple(nodes))

    def use_css(self, *sheets: Any) -> "Page":
        return replace(self, _css=tuple(self._css) + tuple(sheets))

    def render(self) -> str:
        # Apply layout if provided
        page: Page = self
        if self.layout:
            page = self.layout(self)  # type: ignore[misc]

        head_parts = [f"<meta charset=\"utf-8\">", f"<title>{page.title}</title>"]
        for k, v in page._meta.items():
            head_parts.append(f"<meta name=\"{k}\" content=\"{v}\">")
        # CSS
        for sheet in page._css:
            try:
                css_text = sheet.render()
            except Exception:
                css_text = str(sheet)
            head_parts.append(f"<style>{css_text}</style>")
        # Additional head nodes
        head_parts.extend(render_node(n) for n in page._head)
        body_html = "".join(render_node(n) for n in page._body)
        scripts_html = "".join(render_node(n) for n in page._scripts)

        return (
            f"<!doctype html><html lang=\"{page.lang}\">"
            f"<head>{''.join(head_parts)}</head>"
            f"<body>{body_html}{scripts_html}</body>"
            f"</html>"
        )

