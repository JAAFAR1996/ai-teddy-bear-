# GraphQL Federation module exports for AI Teddy Bear project

try:
    from .federation_gateway import (
        GraphQLFederationGateway,
        FederationConfig,
        ServiceConfig,
        create_default_federation_config,
        create_federation_gateway
    )
    FEDERATION_GATEWAY_AVAILABLE = True
except ImportError:
    FEDERATION_GATEWAY_AVAILABLE = False

try:
    from .authentication import (
        AuthenticationService,
        AuthConfig,
        User,
        UserRole,
        Permission,
        APIKey,
        GraphQLAuthenticator,
        create_auth_config,
        create_auth_service
    )
    AUTHENTICATION_AVAILABLE = True
except ImportError:
    AUTHENTICATION_AVAILABLE = False

try:
    from .service_resolvers import (
        Child,
        Conversation,
        AIProfile,
        EmotionSnapshot,
        LearningProgress,
        ChildServiceResolvers,
        AIServiceResolvers,
        MonitoringServiceResolvers,
        SafetyServiceResolvers,
        EntityResolver,
        schema
    )
    SERVICE_RESOLVERS_AVAILABLE = True
except ImportError:
    SERVICE_RESOLVERS_AVAILABLE = False

try:
    from .performance_monitor import (
        GraphQLPerformanceMonitor,
        QueryMetrics,
        ServiceMetrics,
        PerformanceAlert,
        QueryComplexityAnalyzer,
        create_performance_monitor
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
    "PERFORMANCE_MONITOR_AVAILABLE"
] 