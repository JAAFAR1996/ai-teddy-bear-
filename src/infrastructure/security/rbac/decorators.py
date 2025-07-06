"""
Decorators for enforcing RBAC policies on functions and methods.
"""
from functools import wraps
from typing import List

from .factory import get_rbac_manager
from .models import AccessContext, AccessRequest, Permission, UserRole


def require_permission(permission: Permission, context: AccessContext = AccessContext.DIRECT_INTERACTION):
    """
    A decorator that requires the user to have a specific permission to execute
    the decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            if not user_id:
                raise ValueError(
                    "A 'user_id' keyword argument is required for permission checks.")

            rbac = get_rbac_manager()
            user = await rbac.get_user_profile(user_id)
            if not user:
                raise PermissionError(f"User with ID '{user_id}' not found.")

            request = AccessRequest(
                user_id=user_id,
                user_role=user.role,
                permission=permission,
                context=context,
                # resource_id might need to be passed in kwargs as well
                resource_id=kwargs.get("resource_id"),
            )

            decision = await rbac.check_access(request)
            if not decision.granted:
                raise PermissionError(f"Access denied: {decision.reason}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(allowed_roles: List[UserRole]):
    """
    A decorator that requires the user to have one of the specified roles to
    execute the decorated function.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            if not user_id:
                raise ValueError(
                    "A 'user_id' keyword argument is required for role checks.")

            rbac = get_rbac_manager()
            user = await rbac.get_user_profile(user_id)
            if not user:
                raise PermissionError(f"User with ID '{user_id}' not found.")

            if user.role not in allowed_roles:
                allowed_names = [r.value for r in allowed_roles]
                raise PermissionError(
                    f"Access denied. User role '{user.role.value}' is not in the allowed list: {allowed_names}")

            return await func(*args, **kwargs)
        return wrapper
    return decorator
