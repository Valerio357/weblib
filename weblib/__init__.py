"""
WebLib v2 — Minimal MVP scaffold.

Public API re-exports for ergonomics as per spec.
"""

from .app import WebApp, WebAppConfig
from .routing.core import Routes, route
from .routing.responses import HTTP
from .page.page import Page
from .elements.core import E, Element, Component, Var
from .css.css import CSS, css
from .assets.static import Static

__all__ = [
    "WebApp",
    "WebAppConfig",
    "Routes",
    "route",
    "HTTP",
    "Page",
    "E",
    "Element",
    "Component",
    "Var",
    "CSS",
    "css",
    "Static",
]

