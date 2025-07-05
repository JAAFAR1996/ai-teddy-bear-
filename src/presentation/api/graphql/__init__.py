# GraphQL Federation module exports for AI Teddy Bear project

try:
    from .federation_gateway import (
        FederationConfig,
        GraphQLFederationGateway,
        ServiceConfig,
        create_default_federation_config,
        create_federation_gateway,
    )

    FEDERATION_GATEWAY_AVAILABLE = True
except ImportError:
    FEDERATION_GATEWAY_AVAILABLE = False

try:
    from .authentication import (
        APIKey,
        AuthConfig,
        AuthenticationService,
        GraphQLAuthenticator,
        Permission,
        User,
        UserRole,
        create_auth_config,
        create_auth_service,
    )

    AUTHENTICATION_AVAILABLE = True
except ImportError:
    AUTHENTICATION_AVAILABLE = False

try:
    from .service_resolvers import (
        AIProfile,
        AIServiceResolvers,
        Child,
        ChildServiceResolvers,
        Conversation,
        EmotionSnapshot,
        EntityResolver,
        LearningProgress,
        MonitoringServiceResolvers,
        SafetyServiceResolvers,
        schema,
    )

    SERVICE_RESOLVERS_AVAILABLE = True
except ImportError:
    SERVICE_RESOLVERS_AVAILABLE = False

try:
    from .performance_monitor import (
        GraphQLPerformanceMonitor,
        PerformanceAlert,
        QueryComplexityAnalyzer,
        QueryMetrics,
        ServiceMetrics,
        create_performance_monitor,
    )

    PERFORMANCE_MONITOR_AVAILABLE = True
except ImportError:
    PERFORMANCE_MONITOR_AVAILABLE = False

__all__ = [
    # Federation Gateway
    "GraphQLFederationGateway",
    "FederationConfig",
    "ServiceConfig",
    "create_default_federation_config",
    "create_federation_gateway",
    # Authentication
    "AuthenticationService",
    "AuthConfig",
    "User",
    "UserRole",
    "Permission",
    "APIKey",
    "GraphQLAuthenticator",
    "create_auth_config",
    "create_auth_service",
    # Service Resolvers
    "Child",
    "Conversation",
    "AIProfile",
    "EmotionSnapshot",
    "LearningProgress",
    "ChildServiceResolvers",
    "AIServiceResolvers",
    "MonitoringServiceResolvers",
    "SafetyServiceResolvers",
    "EntityResolver",
    "schema",
    # Performance Monitoring
    "GraphQLPerformanceMonitor",
    "QueryMetrics",
    "ServiceMetrics",
    "PerformanceAlert",
    "QueryComplexityAnalyzer",
    "create_performance_monitor",
    # Availability flags
    "FEDERATION_GATEWAY_AVAILABLE",
    "AUTHENTICATION_AVAILABLE",
    "SERVICE_RESOLVERS_AVAILABLE",
    "PERFORMANCE_MONITOR_AVAILABLE",
]
