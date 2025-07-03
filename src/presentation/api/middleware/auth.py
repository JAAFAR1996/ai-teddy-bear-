"""Simple authentication middleware (Flask).

تم تحديث الملف لإزالة التعامل العام مع الاستثناءات (``except Exception``) واستبداله
بمعالجات دقيقة وفق معايير المشروع الأمنية.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Dict

import jwt
from flask import jsonify, request

from domain.exceptions import (
    AuthenticationException,
    TokenExpiredException,
)


def require_api_key(f) -> Any:
    """Require API key for endpoint access"""

    @wraps(f)
    def decorated_function(*args, **kwargs) -> Any:
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return jsonify({"error": "API key required"}), 401

        # Mock API key validation - replace with actual validation
        if api_key != "test_api_key_123":
            return jsonify({"error": "Invalid API key"}), 401

        return f(*args, **kwargs)

    return decorated_function


def require_parent_auth(f) -> Any:
    """Require parent authentication for endpoint access"""

    @wraps(f)
    def decorated_function(*args, **kwargs) -> Any:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication required"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = _decode_token(token)
            request.parent_id = payload.get("parent_id", "parent_123")
        except TokenExpiredException:
            return jsonify({"error": "Token expired"}), 401
        except AuthenticationException:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function


def require_child_auth(f) -> Any:
    """Require child authentication for endpoint access"""

    @wraps(f)
    def decorated_function(*args, **kwargs) -> Any:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication required"}), 401

        token = auth_header.split(" ")[1]

        try:
            payload = _decode_token(token)
            request.child_id = payload.get("child_id", "child_123")
        except TokenExpiredException:
            return jsonify({"error": "Token expired"}), 401
        except AuthenticationException:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _decode_token(token: str) -> Dict[str, Any]:
    """Decode JWT and return payload or raise specific exceptions."""

    secret = "test_secret_change_me"  # TODO: Inject via config/ENV
    algorithms = ["HS256"]

    try:
        return jwt.decode(token, secret, algorithms=algorithms)
    except jwt.ExpiredSignatureError as exc:  # pragma: no cover – runtime dependent
        raise TokenExpiredException() from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationException(reason="invalid token") from exc
