from typing import Any, Dict, List, Optional

"""
Authentication and Authorization for GraphQL Federation.

This module provides comprehensive security features for the federated
GraphQL API including JWT authentication, role-based access control,
and API key management.

API Team Implementation - Task 13
Author: API Team Lead
"""

import logging
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

# JWT and security
try:
    import jwt
    from passlib.context import CryptContext

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

# FastAPI security
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security.api_key import APIKeyHeader, APIKeyQuery

# Caching
try:
    from core.infrastructure.caching import ContentType, MultiLayerCache

    CACHING_AVAILABLE = True
except ImportError:
    CACHING_AVAILABLE = False

logger = logging.getLogger(__name__)


class UserRole(Enum):
    """User roles for access control."""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    PARENT = "parent"
    CHILD = "child"
    GUEST = "guest"
    SERVICE = "service"  # For microservice-to-microservice communication


class Permission(Enum):
    """System permissions."""

    # Child management
    READ_CHILD = "read_child"
    WRITE_CHILD = "write_child"
    DELETE_CHILD = "delete_child"

    # Conversation access
    READ_CONVERSATION = "read_conversation"
    WRITE_CONVERSATION = "write_conversation"
    DELETE_CONVERSATION = "delete_conversation"

    # AI profile management
    READ_AI_PROFILE = "read_ai_profile"
    WRITE_AI_PROFILE = "write_ai_profile"

    # Safety and monitoring
    READ_SAFETY = "read_safety"
    WRITE_SAFETY = "write_safety"
    READ_MONITORING = "read_monitoring"

    # System administration
    ADMIN_USERS = "admin_users"
    ADMIN_SYSTEM = "admin_system"
    VIEW_METRICS = "view_metrics"


@dataclass
class AuthConfig:
    """Authentication configuration."""

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    refresh_token_days: int = 30
    api_key_length: int = 32
    password_min_length: int = 8
    enable_rate_limiting: bool = True
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 15


@dataclass
class User:
    """User model for authentication."""

    id: str
    username: str
    email: str
    role: UserRole
    permissions: Set[Permission]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    parent_id: Optional[str] = None  # For child users
    children_ids: List[str] = None  # For parent users

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.children_ids is None:
            self.children_ids = []


@dataclass
class APIKey:
    """API key model."""

    key: str
    name: str
    user_id: str
    permissions: Set[Permission]
    is_active: bool = True
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    last_used: Optional[datetime] = None
    usage_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class RolePermissions:
    """Default permissions for each role."""

    PERMISSIONS = {
        UserRole.SUPER_ADMIN: {
            Permission.READ_CHILD,
            Permission.WRITE_CHILD,
            Permission.DELETE_CHILD,
            Permission.READ_CONVERSATION,
            Permission.WRITE_CONVERSATION,
            Permission.DELETE_CONVERSATION,
            Permission.READ_AI_PROFILE,
            Permission.WRITE_AI_PROFILE,
            Permission.READ_SAFETY,
            Permission.WRITE_SAFETY,
            Permission.READ_MONITORING,
            Permission.ADMIN_USERS,
            Permission.ADMIN_SYSTEM,
            Permission.VIEW_METRICS,
        },
        UserRole.ADMIN: {
            Permission.READ_CHILD,
            Permission.WRITE_CHILD,
            Permission.READ_CONVERSATION,
            Permission.WRITE_CONVERSATION,
            Permission.READ_AI_PROFILE,
            Permission.WRITE_AI_PROFILE,
            Permission.READ_SAFETY,
            Permission.WRITE_SAFETY,
            Permission.READ_MONITORING,
            Permission.VIEW_METRICS,
        },
        UserRole.PARENT: {
            Permission.READ_CHILD,
            Permission.WRITE_CHILD,
            Permission.READ_CONVERSATION,
            Permission.READ_AI_PROFILE,
            Permission.READ_SAFETY,
            Permission.WRITE_SAFETY,
            Permission.READ_MONITORING,
        },
        UserRole.CHILD: {Permission.READ_CONVERSATION, Permission.WRITE_CONVERSATION},
        UserRole.GUEST: set(),
        UserRole.SERVICE: {
            Permission.READ_CHILD,
            Permission.WRITE_CHILD,
            Permission.READ_CONVERSATION,
            Permission.WRITE_CONVERSATION,
            Permission.READ_AI_PROFILE,
            Permission.WRITE_AI_PROFILE,
            Permission.READ_SAFETY,
            Permission.READ_MONITORING,
        },
    }

    @classmethod
    def get_permissions(cls, role: UserRole) -> Set[Permission]:
        """Get default permissions for role."""
        return cls.PERMISSIONS.get(role, set())


class AuthenticationService:
    """Authentication service for GraphQL Federation."""

    def __init__(self, config: AuthConfig, cache: Optional[MultiLayerCache] = None):
        self.config = config
        self.cache = cache

        # Password hashing
        if JWT_AVAILABLE:
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        # In-memory stores (replace with database in production)
        self.users: Dict[str, User] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.refresh_tokens: Dict[str, str] = {}  # token -> user_id
        self.login_attempts: Dict[str, List[datetime]] = {}

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Initialize default users
        self._initialize_default_users()

    def _initialize_default_users(self) -> Any:
        """Initialize default system users."""
        # Super admin
        admin_user = User(
            id="admin-001",
            username="admin",
            email="admin@teddy-bear.ai",
            role=UserRole.SUPER_ADMIN,
            permissions=RolePermissions.get_permissions(UserRole.SUPER_ADMIN),
        )
        self.users[admin_user.id] = admin_user

        # Test parent
        parent_user = User(
            id="parent-001",
            username="parent_test",
            email="parent@example.com",
            role=UserRole.PARENT,
            permissions=RolePermissions.get_permissions(UserRole.PARENT),
            children_ids=["child-001", "child-002"],
        )
        self.users[parent_user.id] = parent_user

        # Test child
        child_user = User(
            id="child-001",
            username="child_test",
            email="child@example.com",
            role=UserRole.CHILD,
            permissions=RolePermissions.get_permissions(UserRole.CHILD),
            parent_id="parent-001",
        )
        self.users[child_user.id] = child_user

        self.logger.info("Default users initialized")

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: UserRole,
        parent_id: Optional[str] = None,
    ) -> User:
        """Create new user."""
        if not JWT_AVAILABLE:
            raise HTTPException(status_code=500, detail="JWT library not available")

        # Validate password
        if len(password) < self.config.password_min_length:
            raise HTTPException(
                status_code=400,
                detail=f"Password must be at least {self.config.password_min_length} characters",
            )

        # Check if username exists
        existing_user = next(
            (u for u in self.users.values() if u.username == username), None
        )
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        # Create user
        user_id = f"user-{secrets.token_urlsafe(8)}"
        hashed_password = self.pwd_context.hash(password)

        user = User(
            id=user_id,
            username=username,
            email=email,
            role=role,
            permissions=RolePermissions.get_permissions(role),
            parent_id=parent_id,
        )

        self.users[user_id] = user

        # Store hashed password separately (would be in database)
        # For demo purposes, we'll store in memory
        self._store_password(user_id, hashed_password)

        self.logger.info(f"Created user: {username} with role: {role.value}")
        return user

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/password."""
        if not JWT_AVAILABLE:
            return None

        # Check rate limiting
        if await self._is_rate_limited(username):
            raise HTTPException(
                status_code=429,
                detail="Too many login attempts. Please try again later.",
            )

        # Find user
        user = next((u for u in self.users.values() if u.username == username), None)

        if not user or not user.is_active:
            await self._record_login_attempt(username, False)
            return None

        # Verify password
        stored_password = self._get_stored_password(user.id)
        if not stored_password or not self.pwd_context.verify(
            password, stored_password
        ):
            await self._record_login_attempt(username, False)
            return None

        # Update last login
        user.last_login = datetime.now()
        await self._record_login_attempt(username, True)

        self.logger.info(f"User authenticated: {username}")
        return user

    async def create_access_token(self, user: User) -> str:
        """Create JWT access token."""
        if not JWT_AVAILABLE:
            raise HTTPException(status_code=500, detail="JWT library not available")

        payload = {
            "sub": user.id,
            "username": user.username,
            "role": user.role.value,
            "permissions": [p.value for p in user.permissions],
            "exp": datetime.utcnow()
            + timedelta(hours=self.config.jwt_expiration_hours),
            "iat": datetime.utcnow(),
            "type": "access",
        }

        token = jwt.encode(
            payload, self.config.jwt_secret_key, algorithm=self.config.jwt_algorithm
        )

        # Cache token for quick validation
        if self.cache:
            await self.cache.set_multi_layer(
                f"token:{user.id}", token, ContentType.USER_SESSION
            )

        return token

    async def create_refresh_token(self, user: User) -> str:
        """Create refresh token."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=self.config.refresh_token_days)

        # Store refresh token
        self.refresh_tokens[token] = user.id

        # Cache with expiration
        if self.cache:
            await self.cache.set_multi_layer(
                f"refresh:{token}", user.id, ContentType.USER_SESSION
            )

        return token

    async def verify_token(self, token: str) -> Optional[User]:
        """Verify JWT access token."""
        if not JWT_AVAILABLE:
            return None

        try:
            # Check cache first
            if self.cache:
                cached_user_id = await self.cache.get_with_fallback(
                    f"token_user:{token}", ContentType.USER_SESSION
                )
                if cached_user_id:
                    return self.users.get(cached_user_id)

            # Decode token
            payload = jwt.decode(
                token,
                self.config.jwt_secret_key,
                algorithms=[self.config.jwt_algorithm],
            )

            user_id = payload.get("sub")
            token_type = payload.get("type")

            if token_type != "access":
                return None

            user = self.users.get(user_id)
            if not user or not user.is_active:
                return None

            # Cache successful verification
            if self.cache:
                await self.cache.set_multi_layer(
                    f"token_user:{token}", user_id, ContentType.USER_SESSION
                )

            return user

        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token")
            return None

    async def create_api_key(
        self,
        user_id: str,
        name: str,
        permissions: Set[Permission],
        expires_at: Optional[datetime] = None,
    ) -> APIKey:
        """Create API key for user."""
        key = secrets.token_urlsafe(self.config.api_key_length)

        api_key = APIKey(
            key=key,
            name=name,
            user_id=user_id,
            permissions=permissions,
            expires_at=expires_at,
        )

        self.api_keys[key] = api_key

        self.logger.info(f"Created API key: {name} for user: {user_id}")
        return api_key

    async def verify_api_key(self, key: str) -> Optional[APIKey]:
        """Verify API key."""
        api_key = self.api_keys.get(key)

        if not api_key or not api_key.is_active:
            return None

        # Check expiration
        if api_key.expires_at and datetime.now() > api_key.expires_at:
            api_key.is_active = False
            return None

        # Update usage
        api_key.last_used = datetime.now()
        api_key.usage_count += 1

        return api_key

    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has permission."""
        return permission in user.permissions

    def check_child_access(self, user: User, child_id: str) -> bool:
        """Check if user can access specific child."""
        if user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]:
            return True

        if user.role == UserRole.PARENT:
            return child_id in user.children_ids

        if user.role == UserRole.CHILD:
            return user.id == child_id or user.parent_id

        return False

    async def _is_rate_limited(self, username: str) -> bool:
        """Check if user is rate limited."""
        if not self.config.enable_rate_limiting:
            return False

        now = datetime.now()
        attempts = self.login_attempts.get(username, [])

        # Remove old attempts
        cutoff = now - timedelta(minutes=self.config.lockout_duration_minutes)
        recent_attempts = [attempt for attempt in attempts if attempt > cutoff]

        return len(recent_attempts) >= self.config.max_login_attempts

    async def _record_login_attempt(self, username: str, success: bool):
        """Record login attempt."""
        if username not in self.login_attempts:
            self.login_attempts[username] = []

        if not success:
            self.login_attempts[username].append(datetime.now())
        else:
            # Clear attempts on successful login
            self.login_attempts[username] = []

    def _store_password(str) -> None:
        """Store hashed password (mock implementation)."""
        # In production, store in secure database
        setattr(self, f"_pwd_{user_id}", hashed_password)

    def _get_stored_password(self, user_id: str) -> Optional[str]:
        """Get stored hashed password."""
        return getattr(self, f"_pwd_{user_id}", None)


class GraphQLAuthenticator:
    """Authentication middleware for GraphQL."""

    def __init__(self, auth_service: AuthenticationService):
        self.auth_service = auth_service
        self.security = HTTPBearer()
        self.api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
        self.api_key_query = APIKeyQuery(name="api_key", auto_error=False)

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def authenticate_request(
        self,
        request: Request,
        credentials: Optional[HTTPAuthorizationCredentials] = None,
        api_key_header: Optional[str] = None,
        api_key_query: Optional[str] = None,
    ) -> Optional[User]:
        """Authenticate GraphQL request."""
        user = None

        # Try JWT token authentication
        if credentials:
            user = await self.auth_service.verify_token(credentials.credentials)

        # Try API key authentication
        if not user:
            api_key = api_key_header or api_key_query
            if api_key:
                api_key_obj = await self.auth_service.verify_api_key(api_key)
                if api_key_obj:
                    user = self.auth_service.users.get(api_key_obj.user_id)

        if user:
            # Add user to request state
            request.state.user = user
            self.logger.debug(f"Authenticated user: {user.username}")

        return user

    def require_permission(Permission) -> None:
        """Decorator to require specific permission."""

        def decorator(func) -> Any:
            async def wrapper(*args, **kwargs):
                # Get user from context (implementation depends on GraphQL library)
                user = getattr(wrapper, "_current_user", None)

                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

                if not self.auth_service.check_permission(user, permission):
                    raise HTTPException(
                        status_code=403,
                        detail=f"Permission required: {permission.value}",
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator

    def require_child_access(str="child_id") -> None:
        """Decorator to require access to specific child."""

        def decorator(func) -> Any:
            async def wrapper(*args, **kwargs):
                user = getattr(wrapper, "_current_user", None)
                child_id = kwargs.get(child_id_param)

                if not user:
                    raise HTTPException(
                        status_code=401, detail="Authentication required"
                    )

                if not self.auth_service.check_child_access(user, child_id):
                    raise HTTPException(
                        status_code=403, detail="Access denied to child resource"
                    )

                return await func(*args, **kwargs)

            return wrapper

        return decorator


# Factory functions
def create_auth_config(jwt_secret_key: Optional[str] = None) -> AuthConfig:
    """Create authentication configuration."""
    if not jwt_secret_key:
        jwt_secret_key = secrets.token_urlsafe(32)

    return AuthConfig(
        jwt_secret_key=jwt_secret_key,
        jwt_expiration_hours=24,
        refresh_token_days=30,
        enable_rate_limiting=True,
    )


async def create_auth_service(
    config: Optional[AuthConfig] = None, cache: Optional[MultiLayerCache] = None
) -> AuthenticationService:
    """Create authentication service."""
    if config is None:
        config = create_auth_config()

    return AuthenticationService(config, cache)
