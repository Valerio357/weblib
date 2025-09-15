from __future__ import annotations

import secrets
from hashlib import pbkdf2_hmac
from typing import Any, Callable, Optional

from .routing.responses import HTTP


def hash_password(password: str, *, iterations: int = 200_000) -> str:
    """Hash password con PBKDF2-HMAC-SHA256 e salt casuale.

    Ritorna formato: "pbkdf2$<iterations>$<salt_hex>$<digest_hex>"
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password non valida")
    salt = secrets.token_bytes(16)
    digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iters, salt_hex, hash_hex = stored.split("$")
        if algo != "pbkdf2":
            return False
        iterations = int(iters)
        salt = bytes.fromhex(salt_hex)
        digest = pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return secrets.compare_digest(digest.hex(), hash_hex)
    except Exception:
        return False


def login_user(req, user_id: Any, *, session_key: str = "user_id") -> None:
    s = req.state.get("session")
    if s is None:
        raise RuntimeError("Sessioni non abilitate: aggiungi middleware sessions()")
    s[session_key] = user_id


def logout_user(req, *, session_key: str = "user_id") -> None:
    s = req.state.get("session")
    if s is None:
        return
    s.pop(session_key, None)


def current_user_id(req, *, session_key: str = "user_id") -> Optional[Any]:
    s = req.state.get("session") or {}
    return s.get(session_key)


def require_login(redirect_to: str = "/login", *, session_key: str = "user_id"):
    """Middleware di route: richiede che l'utente sia autenticato.

    Se assente, esegue un redirect a `redirect_to`.
    """

    def mw(next_handler):
        async def _wrapped(req, **params):
            user = current_user_id(req, session_key=session_key)
            if user is None:
                return HTTP.redirect(redirect_to)
            return await next_handler(req, **params)

        return _wrapped

    return mw

