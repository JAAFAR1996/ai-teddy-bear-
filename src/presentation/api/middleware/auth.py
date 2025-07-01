from functools import wraps
from typing import Any, Dict, List, Optional

import jwt
from flask import jsonify, request


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
            # Mock token validation - replace with actual JWT decode
            # payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # request.parent_id = payload.get('parent_id')

            # Mock parent ID for testing
            request.parent_id = "parent_123"

        except Exception as e:
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
            # Mock token validation - replace with actual JWT decode
            request.child_id = "child_123"

        except Exception as e:
            return jsonify({"error": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function
