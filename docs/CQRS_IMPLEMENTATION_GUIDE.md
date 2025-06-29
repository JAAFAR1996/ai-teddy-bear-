# 🔄 CQRS Implementation Guide

## Overview

Complete CQRS (Command Query Responsibility Segregation) implementation for the AI Teddy Bear system. CQRS separates read and write operations, optimizing each for their specific use cases.

## 🏗️ Architecture Components

### 1. Command Bus (`command_bus.py`)
**Purpose**: Handles write operations (commands) that change system state

**Features**:
- Command validation and middleware pipeline
- Command handler registration and dispatching
- Logging and performance monitoring
- Integration with Event Sourcing

**Key Classes**:
- `Command` - Protocol for all commands
- `CommandHandler` - Protocol for command handlers  
- `CommandBus` - Central command dispatcher
- `CommandMiddleware` - Pipeline for cross-cutting concerns

### 2. Query Bus (`query_bus.py`)
**Purpose**: Handles read operations (queries) with optimized read models

**Features**:
- Query caching with TTL
- Read model database abstraction
- Performance optimization
- Cache invalidation strategies

**Key Classes**:
- `Query` - Protocol for all queries
- `QueryHandler` - Protocol for query handlers
- `QueryBus` - Central query dispatcher
- `QueryCache` - In-memory result caching

### 3. Commands (`child_commands.py`)
**Purpose**: Specific commands for child-related operations

**Commands Implemented**:
- `RegisterChildCommand` - Register new child
- `UpdateChildProfileCommand` - Update child profile
- `ReportSafetyViolationCommand` - Report safety violations
- `DeactivateChildCommand` - Deactivate child account

### 4. Queries (`child_queries.py`)
**Purpose**: Specific queries for child-related read operations

**Queries Implemented**:
- `GetChildProfileQuery` - Get child profile with enriched data
- `GetChildrenByParentQuery` - Get children for parent with pagination
- `GetChildSafetyReportQuery` - Generate safety reports
- `GetChildAnalyticsQuery` - Get analytics and insights
- `SearchChildrenQuery` - Search children by criteria

### 5. Read Models (`child_read_model.py`)
**Purpose**: Optimized data structures for query operations

**Read Models**:
- `ChildReadModel` - Optimized child data with computed fields
- `ConversationSummaryReadModel` - Conversation summaries
- `SafetyMetricsReadModel` - Safety metrics and trends
- `ChildProjectionManager` - Manages projections from events

### 6. CQRS Service (`cqrs_service.py`)
**Purpose**: High-level API orchestrating commands and queries

**Features**:
- Unified interface for CQRS operations
- Command/query coordination
- Cache invalidation management
- System analytics and health monitoring

## 📋 Implementation Details

### Command Flow
```
Client Request → Command → CommandBus → Middleware → CommandHandler → Domain → Event Store
```

### Query Flow
```
Client Request → Query → QueryBus → Cache Check → QueryHandler → Read Model → Response
```

### Event Projection Flow
```
Domain Events → Projection Manager → Read Models → Query Optimization
```

## 🚀 Usage Examples

### Basic Command Usage

```python
from src.core.application.cqrs_service import get_cqrs_service

# Initialize CQRS service
cqrs = get_cqrs_service()
await cqrs.initialize()

# Register child (Command)
result = await cqrs.register_child(
    parent_id="parent-123",
    device_id="device-456", 
    name="Emma",
    age=7,
    udid="unique-device-emma-001"
)

if result.success:
    child_id = result.data['child_id']
    print(f"Child registered: {child_id}")
```

### Basic Query Usage

```python
# Get child profile (Query)
profile = await cqrs.get_child_profile(
    child_id=child_id,
    user_id="parent-123"
)

if profile.data:
    print(f"Child name: {profile.data['name']}")
    print(f"Safety status: {profile.data['safety_status']}")
    print(f"Conversations: {profile.data['conversation_count']}")
```

### Advanced Operations

```python
# Update profile (Command)
await cqrs.update_child_profile(
    child_id=child_id,
    changes={
        "age": 8,
        "preferences": {
            "favorite_stories": ["dragons", "princesses"],
            "learning_style": "visual"
        }
    }
)

# Get safety report (Query)
safety_report = await cqrs.get_child_safety_report(
    child_id=child_id,
    from_date=datetime.utcnow() - timedelta(days=30)
)

# Search children (Query)
results = await cqrs.search_children(
    search_term="Em",
    age_range=(6, 8),
    parent_id="parent-123"
)
```

## 🎯 Performance Optimizations

### Command Side Optimizations
- **Middleware Pipeline**: Validation, logging, security
- **Event Sourcing Integration**: Efficient event persistence
- **Async Operations**: Non-blocking command processing
- **Error Handling**: Comprehensive validation and error recovery

### Query Side Optimizations
- **Read Model Caching**: 15-minute TTL for profiles, 1-hour for reports
- **Materialized Views**: Pre-computed data for fast queries
- **Pagination Support**: Efficient large dataset handling
- **Cache Invalidation**: Smart cache updates on data changes

### Read Model Benefits
- **Denormalized Data**: Optimized for specific query patterns
- **Computed Fields**: Pre-calculated metrics and scores
- **Event Projections**: Real-time updates from domain events
- **Query Specialization**: Different models for different use cases

## 🔧 Configuration

### Cache Settings
```python
# Query cache configuration
CACHE_SETTINGS = {
    "max_size": 1000,                    # Maximum cached entries
    "child_profile_ttl": 30,             # 30 minutes
    "safety_report_ttl": 60,             # 1 hour
    "parent_children_ttl": 15,           # 15 minutes
    "analytics_ttl": 120                 # 2 hours
}
```

### Middleware Configuration
```python
# Command middleware pipeline
MIDDLEWARE_PIPELINE = [
    ValidationMiddleware(),    # Input validation
    LoggingMiddleware(),      # Request/response logging
    SecurityMiddleware(),     # Authorization checks
    MetricsMiddleware()       # Performance metrics
]
```

## 📊 Integration Points

### With Event Sourcing
- Commands generate domain events
- Events are persisted to event store
- Read models are updated via event projections
- Event replay rebuilds read models

### With Kafka Event Streaming
- Domain events published to Kafka topics
- Real-time event processing for projections
- Event-driven architecture coordination
- Scalable event distribution

### With DDD Architecture
- Commands operate on domain aggregates
- Queries read from optimized projections
- Domain events bridge command/query sides
- Bounded contexts maintained

## 🧪 Testing

### Running Examples
```bash
# Run all CQRS examples
python src/core/application/cqrs_examples.py
```

### Test Scenarios Covered
1. **Child Registration**: Command validation and execution
2. **Profile Queries**: Cached and enriched data retrieval
3. **Profile Updates**: Command processing and cache invalidation
4. **Safety Violations**: Critical event handling and reporting
5. **Parent Dashboard**: Multi-child queries with pagination
6. **Search and Analytics**: Complex queries and system metrics
7. **Health Monitoring**: System status and performance tracking
8. **Error Handling**: Validation failures and edge cases

### Integration Testing
```python
async def test_cqrs_integration():
    cqrs = get_cqrs_service()
    await cqrs.initialize()
    
    # Test command
    result = await cqrs.register_child(...)
    assert result.success
    
    # Test query
    profile = await cqrs.get_child_profile(result.data['child_id'])
    assert profile.data is not None
```

## 🔒 Security Features

### Command Security
- User authentication validation
- Authorization checks per command
- Input sanitization and validation
- Audit trail logging

### Query Security
- Access control per query type
- Data filtering based on user permissions
- Rate limiting for expensive queries
- Sensitive data masking

### Data Protection
- PII encryption in read models
- Secure cache key generation
- Audit logging for all operations
- GDPR compliance features

## 📈 Monitoring and Observability

### Key Metrics
```python
# Health check example
health = await cqrs.get_health_status()

metrics = {
    "command_throughput": "commands/second",
    "query_response_time": "milliseconds", 
    "cache_hit_rate": "percentage",
    "error_rate": "errors/total_requests",
    "read_model_freshness": "seconds_behind"
}
```

### Logging
- Structured logging with correlation IDs
- Performance timing for all operations
- Error logging with stack traces
- Command/query audit trails

### Alerting
- High error rates in commands
- Low cache hit rates
- Slow query performance
- Read model lag behind events

## 🎯 Best Practices

### Command Design
1. **Single Responsibility**: One command per business operation
2. **Immutable**: Commands should be immutable once created
3. **Validation**: Validate all inputs before processing
4. **Idempotent**: Commands should be safe to retry

### Query Design
1. **Specific**: Design queries for specific use cases
2. **Cacheable**: Structure queries to benefit from caching
3. **Efficient**: Optimize for read performance over flexibility
4. **Paginated**: Support pagination for large datasets

### Read Model Design
1. **Denormalized**: Optimize for query patterns
2. **Event-Driven**: Update via domain events
3. **Eventually Consistent**: Accept eventual consistency
4. **Specialized**: Different models for different needs

## 🔄 Event-Driven Updates

### Projection Updates
```python
# Read models updated via events
async def handle_child_registered(event: ChildRegistered):
    read_model = ChildReadModel(
        id=str(event.child_id),
        name=event.name,
        age=event.age,
        # ... computed fields
    )
    await update_read_model(read_model)
```

### Cache Invalidation
```python
# Smart cache invalidation
async def invalidate_after_profile_update(child_id: str):
    await query_bus.invalidate_cache(f"child_profile:{child_id}")
    await query_bus.invalidate_cache(f"parent_children")
    await query_bus.invalidate_cache(f"analytics")
```

## 🚀 Production Deployment

### Scalability Considerations
- **Horizontal Scaling**: Separate command and query services
- **Database Separation**: Different databases for read/write
- **Caching Strategy**: Distributed caching with Redis
- **Load Balancing**: Route commands and queries independently

### Performance Tuning
- **Read Model Optimization**: Index for common query patterns
- **Cache Warming**: Pre-populate frequently accessed data
- **Connection Pooling**: Optimize database connections
- **Async Processing**: Non-blocking operations throughout

### Monitoring in Production
- **APM Integration**: Application performance monitoring
- **Custom Metrics**: Business-specific metrics
- **Health Endpoints**: Service health checks
- **Alerting Rules**: Proactive issue detection

This CQRS implementation provides a robust, scalable foundation for the AI Teddy Bear system with clear separation of concerns, optimized performance, and comprehensive monitoring capabilities. 