"""
Unit tests for GraphQL Federation System.

API Team Implementation - Task 13
Author: API Team Lead
"""

import os

try:
    from unittest.mock import AsyncMock, MagicMock
except ImportError:
    # Python < 3.8 fallback
    import sys

    if sys.version_info < (3, 8):
        import asyncio
        from unittest.mock import MagicMock

        class AsyncMock(MagicMock):
            async def __call__(self, *args, **kwargs):
                return super().__call__(*args, **kwargs)

    else:
        raise

import pytest

# Test imports
try:
    from src.infrastructure.graphql.authentication import (
        AuthConfig,
        AuthenticationService,
        Permission,
        User,
        UserRole,
        create_auth_config,
    )
    from src.infrastructure.graphql.federation_gateway import (
        FederationConfig,
        GraphQLFederationGateway,
        ServiceConfig,
        create_default_federation_config,
    )
    from src.infrastructure.graphql.service_resolvers import (
        AIServiceResolvers,
        ChildServiceResolvers,
        MonitoringServiceResolvers,
        SafetyServiceResolvers,
    )

    FEDERATION_AVAILABLE = True
except ImportError:
    FEDERATION_AVAILABLE = False


@pytest.fixture
def federation_config():
    """Test federation configuration."""
    return FederationConfig(
        services=[
            ServiceConfig(
                name="child_service", url="http://localhost:8001", schema_path="/schema"
            ),
            ServiceConfig(
                name="ai_service", url="http://localhost:8002", schema_path="/schema"
            ),
        ],
        enable_authentication=True,
        enable_caching=True,
        enable_rate_limiting=True,
    )


@pytest.fixture
def auth_config():
    """Test authentication configuration."""
    return create_auth_config("test-secret-key")


@pytest.fixture
async def auth_service(auth_config):
    """Authentication service fixture."""
    from src.infrastructure.graphql.authentication import create_auth_service

    return await create_auth_service(auth_config)


@pytest.fixture
async def federation_gateway(federation_config):
    """Federation gateway fixture."""
    if not FEDERATION_AVAILABLE:
        pytest.skip("GraphQL Federation not available")

    gateway = GraphQLFederationGateway(federation_config)

    # Mock HTTP client to avoid actual network calls
    gateway.http_client = AsyncMock()
    gateway.http_client.get = AsyncMock()
    gateway.http_client.post = AsyncMock()

    await gateway.initialize()
    yield gateway
    await gateway.cleanup()


class TestFederationConfig:
    """Test federation configuration."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = create_default_federation_config()

        pytest.assume(len(config.services) == 4)
        pytest.assume(config.enable_introspection is True)
        pytest.assume(config.enable_caching is True)
        pytest.assume(config.cors_origins == ["*"])

    def test_custom_config(self):
        """Test custom configuration."""
        services = [ServiceConfig("test_service", "http://test:8000", "/schema")]

        config = FederationConfig(
            services=services, enable_authentication=False, rate_limit_requests=200
        )

        pytest.assume(len(config.services) == 1)
        pytest.assume(config.enable_authentication is False)
        pytest.assume(config.rate_limit_requests == 200)


class TestServiceConfig:
    """Test service configuration."""

    def test_service_config_creation(self):
        """Test service configuration creation."""
        config = ServiceConfig(
            name="test_service",
            url="http://localhost:8000",
            schema_path="/graphql",
            timeout=60,
            retry_attempts=5,
        )

        pytest.assume(config.name == "test_service")
        pytest.assume(config.url == "http://localhost:8000")
        pytest.assume(config.timeout == 60)
        pytest.assume(config.retry_attempts == 5)


@pytest.mark.skipif(not FEDERATION_AVAILABLE, reason="Federation not available")
class TestGraphQLFederationGateway:
    """Test GraphQL Federation Gateway."""

    @pytest.mark.asyncio
    async def test_gateway_initialization(self, federation_config):
        """Test gateway initialization."""
        gateway = GraphQLFederationGateway(federation_config)

        # Mock dependencies
        gateway.http_client = AsyncMock()
        gateway.http_client.get.return_value.__aenter__.return_value.status_code = 200

        result = await gateway.initialize()
        pytest.assume(result is True)

        await gateway.cleanup()

    @pytest.mark.asyncio
    async def test_service_health_check(self, federation_gateway):
        """Test service health checking."""
        # Mock successful health check
        federation_gateway.http_client.get.return_value.__aenter__.return_value.status_code = 200

        config = federation_gateway.services["child_service"]
        healthy = await federation_gateway._check_single_service_health(config)

        pytest.assume(healthy is True)

    @pytest.mark.asyncio
    async def test_query_service_analysis(self, federation_gateway):
        """Test query service analysis."""
        # Test child service detection
        query = 'query { child(id: "123") { name age } }'
        services = federation_gateway._analyze_query_services(query)
        pytest.assume("child_service" in services)

        # Test AI service detection
        query = 'query { child(id: "123") { aiProfile { personalityTraits } } }'
        services = federation_gateway._analyze_query_services(query)
        pytest.assume("ai_service" in services)

    @pytest.mark.asyncio
    async def test_federated_query_execution(self, federation_gateway):
        """Test federated query execution."""
        # Mock service responses
        federation_gateway.http_client.post.return_value.__aenter__.return_value.status_code = 200
        federation_gateway.http_client.post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={"data": {"child": {"name": "Test Child", "age": 7}}}
        )

        query = 'query { child(id: "123") { name age } }'
        result = await federation_gateway._execute_federated_query(query, {})

        pytest.assume("data" in result)
        pytest.assume(result["data"] is not None)


class TestAuthentication:
    """Test authentication system."""

    @pytest.mark.asyncio
    async def test_user_creation(self, auth_service):
        """Test user creation."""
        user = await auth_service.create_user(
            username="testuser",
            email="test@example.com",
            password=os.environ.get("TEST_PASSWORD", "test_secure_password_2025"),
            role=UserRole.PARENT,
        )

        pytest.assume(user.username == "testuser")
        pytest.assume(user.role == UserRole.PARENT)
        pytest.assume(Permission.READ_CHILD in user.permissions)

    @pytest.mark.asyncio
    async def test_user_authentication(self, auth_service):
        """Test user authentication."""
        # Create user first
        await auth_service.create_user(
            "authuser", "auth@example.com", "password123", UserRole.PARENT
        )

        # Test successful authentication
        user = await auth_service.authenticate_user("authuser", "password123")
        pytest.assume(user is not None)
        pytest.assume(user.username == "authuser")

        # Test failed authentication
        user = await auth_service.authenticate_user("authuser", "wrongpassword")
        pytest.assume(user is None)

    @pytest.mark.asyncio
    async def test_jwt_token_creation(self, auth_service):
        """Test JWT token creation and verification."""
        user = await auth_service.create_user(
            "tokenuser", "token@example.com", "password123", UserRole.PARENT
        )

        # Create token
        token = await auth_service.create_access_token(user)
        pytest.assume(token is not None)
        pytest.assume(isinstance(token, str))

        # Verify token
        verified_user = await auth_service.verify_token(token)
        pytest.assume(verified_user is not None)
        pytest.assume(verified_user.id == user.id)

    @pytest.mark.asyncio
    async def test_api_key_creation(self, auth_service):
        """Test API key creation and verification."""
        user = await auth_service.create_user(
            "apikeyuser", "apikey@example.com", "password123", UserRole.SERVICE
        )

        permissions = {Permission.READ_CHILD, Permission.WRITE_CHILD}

        # Create API key
        api_key = await auth_service.create_api_key(
            user.id, "Test API Key", permissions
        )

        pytest.assume(api_key.name == "Test API Key")
        pytest.assume(api_key.permissions == permissions)

        # Verify API key
        verified_key = await auth_service.verify_api_key(api_key.key)
        pytest.assume(verified_key is not None)
        pytest.assume(verified_key.user_id == user.id)

    def test_permission_checking(self, auth_service):
        """Test permission checking."""
        # Create users with different roles
        admin_user = User(
            id="admin-test",
            username="admin",
            email="admin@test.com",
            role=UserRole.ADMIN,
            permissions=auth_service.RolePermissions.get_permissions(UserRole.ADMIN),
        )

        parent_user = User(
            id="parent-test",
            username="parent",
            email="parent@test.com",
            role=UserRole.PARENT,
            permissions=auth_service.RolePermissions.get_permissions(UserRole.PARENT),
            children_ids=["child-123"],
        )

        # Test admin permissions
        pytest.assume(
            auth_service.check_permission(admin_user, Permission.READ_CHILD) is True
        )
        pytest.assume(
            auth_service.check_permission(admin_user, Permission.ADMIN_SYSTEM) is False
        )

        # Test parent permissions
        pytest.assume(
            auth_service.check_permission(parent_user, Permission.READ_CHILD) is True
        )
        pytest.assume(
            auth_service.check_permission(parent_user, Permission.DELETE_CHILD) is False
        )

        # Test child access
        pytest.assume(auth_service.check_child_access(parent_user, "child-123") is True)
        pytest.assume(
            auth_service.check_child_access(parent_user, "child-456") is False
        )


class TestServiceResolvers:
    """Test service resolvers."""

    @pytest.mark.asyncio
    async def test_child_service_resolvers(self):
        """Test child service resolvers."""
        # Test get_child
        child = await ChildServiceResolvers.get_child("test-child-id")
        pytest.assume(child is not None)
        pytest.assume(child.id == "test-child-id")
        pytest.assume(child.name == "Ahmed")

        # Test get_children
        children = await ChildServiceResolvers.get_children("parent-123")
        pytest.assume(len(children) == 2)
        pytest.assume(all(child.parent_id == "parent-123" for child in children))

    @pytest.mark.asyncio
    async def test_ai_service_resolvers(self):
        """Test AI service resolvers."""
        ai_profile = await AIServiceResolvers.get_ai_profile("child-123")
        pytest.assume(ai_profile is not None)
        pytest.assume(len(ai_profile.personality_traits) > 0)

    @pytest.mark.asyncio
    async def test_monitoring_service_resolvers(self):
        """Test monitoring service resolvers."""
        usage_stats = await MonitoringServiceResolvers.get_usage_statistics(
            "child-123", "daily"
        )
        pytest.assume(usage_stats is not None)
        pytest.assume(usage_stats.total_session_time > 0)

    @pytest.mark.asyncio
    async def test_safety_service_resolvers(self):
        """Test safety service resolvers."""
        safety_profile = await SafetyServiceResolvers.get_safety_profile("child-123")
        pytest.assume(safety_profile is not None)
        pytest.assume(safety_profile.safety_score > 0)


class TestPerformanceMonitoring:
    """Test performance monitoring."""

    @pytest.mark.asyncio
    async def test_query_monitoring(self):
        """Test query performance monitoring."""
        try:
            from src.infrastructure.graphql.performance_monitor import (
                create_performance_monitor,
            )

            monitor = create_performance_monitor(enable_prometheus=False)

            # Start monitoring
            query = 'query { child(id: "123") { name } }'
            query_hash = await monitor.start_query_monitoring(query, {}, "getChild")

            pytest.assume(query_hash is not None)
            pytest.assume(monitor.current_queries == 1)

            # Finish monitoring
            await monitor.finish_query_monitoring(
                query_hash=query_hash,
                query=query,
                variables={},
                operation_name="getChild",
                execution_time_ms=150.5,
                fields_requested=["name"],
                services_involved=["child_service"],
                cache_hit=False,
                error_count=0,
            )

            pytest.assume(monitor.current_queries == 0)

            # Check metrics
            summary = monitor.get_performance_summary()
            pytest.assume(summary["summary"]["total_queries"] > 0)

        except ImportError:
            pytest.skip("Performance monitoring not available")

    @pytest.mark.asyncio
    async def test_service_call_recording(self):
        """Test service call metrics recording."""
        try:
            from src.infrastructure.graphql.performance_monitor import (
                create_performance_monitor,
            )

            monitor = create_performance_monitor(enable_prometheus=False)

            await monitor.record_service_call(
                service_name="child_service",
                query_hash="test-hash",
                execution_time_ms=75.2,
                response_size_bytes=1024,
                success=True,
            )

            # Check that metrics were recorded
            pytest.assume(len(monitor.service_metrics) > 0)

        except ImportError:
            pytest.skip("Performance monitoring not available")


class TestRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiting(self, federation_gateway):
        """Test rate limiting middleware."""
        # Mock cache for rate limiting
        if hasattr(federation_gateway, "cache") and federation_gateway.cache:
            # Simulate rate limit exceeded
            federation_gateway.cache.get_with_fallback = AsyncMock(
                return_value=federation_gateway.config.rate_limit_requests + 1
            )

            # Test rate limiting logic
            # This would be tested in integration tests with actual HTTP requests


class TestErrorHandling:
    """Test error handling in federation."""

    @pytest.mark.asyncio
    async def test_service_error_handling(self, federation_gateway):
        """Test handling of service errors."""
        # Mock service error
        federation_gateway.http_client.post.return_value.__aenter__.return_value.status_code = 500
        federation_gateway.http_client.post.return_value.__aenter__.return_value.text = AsyncMock(
            return_value="Internal Server Error"
        )

        # Test error handling in service query
        config = federation_gateway.services["child_service"]

        with pytest.raises(Exception):
            await federation_gateway._query_service(
                config, "query { child { name } }", {}, None
            )

    @pytest.mark.asyncio
    async def test_authentication_errors(self, auth_service):
        """Test authentication error handling."""
        # Test invalid token
        invalid_user = await auth_service.verify_token("invalid-token")
        pytest.assume(invalid_user is None)

        # Test rate limiting
        # Simulate multiple failed login attempts
        for _ in range(6):  # Exceed max attempts
            await auth_service.authenticate_user("nonexistent", "wrong")

        # Should be rate limited now
        with pytest.raises(Exception):  # Should raise HTTP 429
            await auth_service.authenticate_user("nonexistent", "wrong")


class TestCacheIntegration:
    """Test cache integration with federation."""

    @pytest.mark.asyncio
    async def test_query_caching(self, federation_gateway):
        """Test GraphQL query caching."""
        if not federation_gateway.cache:
            pytest.skip("Cache not available")

        # Mock cache hit
        federation_gateway.cache.get_with_fallback = AsyncMock(
            return_value={"data": {"child": {"name": "Cached Child"}}}
        )

        query = 'query { child(id: "123") { name } }'
        result = await federation_gateway._execute_federated_query(query, {})

        pytest.assume(result["data"]["child"]["name"] == "Cached Child")

    @pytest.mark.asyncio
    async def test_authentication_caching(self, auth_service):
        """Test authentication token caching."""
        if not auth_service.cache:
            pytest.skip("Cache not available")

        user = await auth_service.create_user(
            "cacheuser", "cache@example.com", "password123", UserRole.PARENT
        )

        token = await auth_service.create_access_token(user)

        # First verification should cache the result
        verified_user = await auth_service.verify_token(token)
        pytest.assume(verified_user.id == user.id)

        # Second verification should use cache
        verified_user = await auth_service.verify_token(token)
        pytest.assume(verified_user.id == user.id)


@pytest.mark.integration
class TestFederationIntegration:
    """Integration tests for federation system."""

    @pytest.mark.asyncio
    async def test_full_query_flow(self, federation_gateway):
        """Test complete query flow through federation."""
        # Mock all service responses
        federation_gateway.http_client.post.return_value.__aenter__.return_value.status_code = 200
        federation_gateway.http_client.post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value={
                "data": {
                    "child": {
                        "id": "123",
                        "name": "Test Child",
                        "age": 7,
                        "aiProfile": {
                            "personalityTraits": [{"name": "Curious", "score": 0.85}]
                        },
                    }
                }
            }
        )

        # Execute federated query
        query = """
        query {
            child(id: "123") {
                id
                name
                age
                aiProfile {
                    personalityTraits {
                        name
                        score
                    }
                }
            }
        }
        """

        result = await federation_gateway._execute_federated_query(query, {})

        pytest.assume("data" in result)
        pytest.assume(result["data"]["child"]["name"] == "Test Child")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
