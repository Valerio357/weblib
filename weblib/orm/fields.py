from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Type


@dataclass
class Field:
    kind: str  # "int" | "str" | "text" | "bool" | "datetime" | "fk"
    pk: bool = False
    default: Any | None = None
    max_length: int | None = None
    unique: bool = False
    to: Optional[Type] = None  # for ForeignKey


class fields:
    @staticmethod
    def Int(pk: bool = False, default: int | None = None) -> Field:
        return Field(kind="int", pk=pk, default=default)

    @staticmethod
    def Str(max_length: int | None = None, unique: bool = False) -> Field:
        return Field(kind="str", max_length=max_length, unique=unique)

    @staticmethod
    def Text() -> Field:
        return Field(kind="text")

    @staticmethod
    def Bool(default: bool = False) -> Field:
        return Field(kind="bool", default=default)

    @staticmethod
    def Datetime(auto_now: bool = False, auto_now_add: bool = False) -> Field:
        # auto_now* non implementati nell'MVP; lasciati come no-op semantici
        return Field(kind="datetime")

    @staticmethod
    def ForeignKey(to: type, on_delete: str = "cascade") -> Field:
        # on_delete non implementato nell'MVP
        return Field(kind="fk", to=to)

