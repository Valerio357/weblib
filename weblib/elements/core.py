from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Generic, Iterable, Tuple, TypeVar

from ..utils import escape_html


Node = Any  # str | Element | Component


@dataclass(frozen=True)
class Element:
    tag: str
    attrs: dict[str, Any]
    children: Tuple[Node, ...]

    def attr(self, **attrs) -> "Element":
        new_attrs = dict(self.attrs)
        for k, v in attrs.items():
            if k == "cls":
                key = "class"
            elif k.endswith("_"):
                key = k[:-1]
            else:
                key = k.replace("_", "-")
            new_attrs[key] = v
        return replace(self, attrs=new_attrs)

    def cls(self, value: str) -> "Element":
        current = self.attrs.get("class")
        new = f"{current} {value}".strip() if current else value
        return self.attr(class_=new)  # type: ignore[call-arg]


def render_attr(k: str, v: Any) -> str:
    if isinstance(v, bool):
        return k if v else ""
    return f"{k}=\"{escape_html(str(v))}\""


def render_node(n: Node) -> str:
    if n is None:
        return ""
    if isinstance(n, Element):
        attrs = " ".join(filter(None, (render_attr(k, v) for k, v in n.attrs.items())))
        opening = f"<{n.tag}{(' ' + attrs) if attrs else ''}>"
        children = "".join(render_node(c) for c in n.children)
        return f"{opening}{children}</{n.tag}>"
    if isinstance(n, Component):
        return render_node(n.render())
    return escape_html(str(n))


class _EFactory:
    def __getattr__(self, tag: str):
        def factory(*children: Node, **attrs):
            norm: dict[str, Any] = {}
            for k, v in attrs.items():
                if k == "cls":
                    key = "class"
                elif k.endswith("_"):
                    key = k[:-1]
                else:
                    key = k.replace("_", "-")
                norm[key] = v
            return Element(tag=tag, attrs=norm, children=tuple(children))

        return factory


E = _EFactory()


T = TypeVar("T")


class Var(Generic[T]):
    pass


class Component:
    def __init__(self, **props):
        for k, v in props.items():
            setattr(self, k, v)

    def render(self) -> Element | str:
        return ""
