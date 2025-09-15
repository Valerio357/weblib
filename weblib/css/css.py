from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class Rule:
    selector: str
    declarations: Dict[str, str]


def css(selector: str, decls: Dict[str, str]) -> Rule:
    return Rule(selector=selector, declarations=dict(decls))


class CSS:
    def __init__(self, scope_name: str | None = None, rules: Tuple[Rule, ...] = ()) -> None:
        self.scope_name = scope_name
        self._rules = tuple(rules)

    @staticmethod
    def scope(name: str) -> "CSS":
        return CSS(scope_name=name)

    def add(self, *rules: Rule) -> "CSS":
        return CSS(self.scope_name, self._rules + tuple(rules))

    def merge(self, *others: "CSS") -> "CSS":
        rules = list(self._rules)
        for o in others:
            rules.extend(o._rules)
        return CSS(self.scope_name, tuple(rules))

    def minify(self) -> "CSS":
        # No-op minimalist minify (render uses compact format)
        return self

    def render(self) -> str:
        # very compact serializer
        parts: List[str] = []
        for r in self._rules:
            sel = r.selector
            decls = ";".join(f"{k}:{v}" for k, v in r.declarations.items())
            parts.append(f"{sel}{{{decls}}}")
        return "".join(parts)

