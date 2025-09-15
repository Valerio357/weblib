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
from .auth import (
    hash_password,
    verify_password,
    login_user,
    logout_user,
    current_user_id,
    require_login,
)

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
    "hash_password",
    "verify_password",
    "login_user",
    "logout_user",
    "current_user_id",
    "require_login",
]
