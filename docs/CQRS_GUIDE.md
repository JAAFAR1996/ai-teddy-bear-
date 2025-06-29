# 🔄 CQRS Implementation Guide

## Overview

Complete CQRS (Command Query Responsibility Segregation) implementation for AI Teddy Bear system, separating read and write operations for optimal performance.

## 🏗️ Core Components

### 1. Command Bus (`command_bus.py`)
- Handles write operations that change system state
- Command validation and middleware pipeline
- Integration with Event Sourcing
- Logging and performance monitoring

### 2. Query Bus (`query_bus.py`)
- Handles read operations with optimized read models
- Query caching with configurable TTL
- Read model database abstraction
- Cache invalidation strategies

### 3. Child Commands (`child_commands.py`)
- `RegisterChildCommand` - Register new child
- `UpdateChildProfileCommand` - Update child profile  
- `ReportSafetyViolationCommand` - Report safety violations
- Command handlers with validation

### 4. Child Queries (`child_queries.py`)
- `GetChildProfileQuery` - Get enriched child profile
- `GetChildrenByParentQuery` - Get children with pagination
- `GetChildSafetyReportQuery` - Generate safety reports
- Query handlers with caching

### 5. Read Models (`child_read_model.py`)
- `ChildReadModel` - Optimized child data with computed fields
- `ConversationSummaryReadModel` - Conversation summaries
- `SafetyMetricsReadModel` - Safety metrics and trends
- Event projection management

### 6. CQRS Service (`cqrs_service.py`)
- High-level API orchestrating commands and queries
- Cache invalidation management
- System analytics and health monitoring

## 🚀 Usage Examples

### Basic Operations

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

# Get child profile (Query)
profile = await cqrs.get_child_profile(
    child_id=result.data['child_id'],
    user_id="parent-123"
)

# Update profile (Command)
await cqrs.update_child_profile(
    child_id=child_id,
    changes={"age": 8, "preferences": {"favorite_stories": ["dragons"]}}
)
```

### Advanced Queries

```python
# Get children for parent with pagination
children = await cqrs.get_children_by_parent(
    parent_id="parent-123",
    page=1,
    page_size=10
)

# Generate safety report
safety_report = await cqrs.get_child_safety_report(
    child_id=child_id,
    from_date=datetime.utcnow() - timedelta(days=30)
)

# Search children by criteria
results = await cqrs.search_children(
    search_term="Em",
    age_range=(6, 8),
    parent_id="parent-123"
)
```

## 📊 Architecture Flow

### Command Flow
```
Client → Command → CommandBus → Validation → Handler → Domain → Events
```

### Query Flow  
```
Client → Query → QueryBus → Cache Check → Handler → Read Model → Response
```

### Event Projection
```
Domain Events → Projection Manager → Read Models → Query Optimization
```

## 🎯 Performance Features

### Command Side
- Middleware pipeline for validation and logging
- Async operations for non-blocking processing
- Event Sourcing integration
- Comprehensive error handling

### Query Side
- Read model caching (15min-2hour TTL)
- Materialized views for fast queries
- Pagination support
- Smart cache invalidation

### Read Model Benefits
- Denormalized data optimized for queries
- Pre-computed metrics and scores
- Real-time updates from domain events
- Specialized models for different use cases

## 🔧 Configuration

### Cache Settings
```python
CACHE_SETTINGS = {
    "child_profile_ttl": 30,      # 30 minutes
    "safety_report_ttl": 60,      # 1 hour
    "parent_children_ttl": 15,    # 15 minutes
    "max_size": 1000              # Max cached entries
}
```

### Integration Points
- **Event Sourcing**: Commands generate events, queries use projections
- **Kafka Streaming**: Real-time event processing for read models
- **DDD Architecture**: Commands on aggregates, queries on projections

## 🧪 Testing

Run comprehensive examples:
```bash
python src/core/application/cqrs_examples.py
```

### Test Scenarios
1. Child registration and profile queries
2. Profile updates with cache invalidation
3. Safety violation reporting and analysis
4. Parent dashboard with multiple children
5. Search and analytics operations
6. Health monitoring and error handling

## 🔒 Security Features

- User authentication and authorization
- Input validation and sanitization
- Audit trail logging
- Data filtering based on permissions
- Rate limiting for expensive queries

## 📈 Monitoring

### Key Metrics
- Command throughput (commands/second)
- Query response time (milliseconds)
- Cache hit rate (percentage)
- Error rate (errors/total requests)

### Health Check
```python
health = await cqrs.get_health_status()
# Returns status of command bus, query bus, and projection manager
```

## 🎯 Best Practices

### Commands
1. Single responsibility per command
2. Immutable command objects
3. Comprehensive input validation
4. Idempotent operations

### Queries
1. Specific queries for use cases
2. Cache-friendly design
3. Efficient read model access
4. Paginated large datasets

### Read Models
1. Denormalized for query patterns
2. Event-driven updates
3. Eventually consistent
4. Specialized for different needs

## 🚀 Production Ready

**Features**:
- Horizontal scaling support
- Database separation (read/write)
- Distributed caching ready
- Comprehensive monitoring
- Error handling and recovery

**Benefits for AI Teddy Bear**:
- Fast child profile access
- Efficient safety reporting
- Scalable parent dashboards
- Real-time analytics
- Optimized conversation queries

This CQRS implementation provides enterprise-grade separation of concerns with optimized performance for both command and query operations in the AI Teddy Bear system. 