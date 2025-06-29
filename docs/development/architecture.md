# AI Teddy Bear Architecture

## Overview
The system follows Clean Architecture principles with clear separation of concerns.

## Layers

### 1. Domain Layer (Core)
- **Entities**: Core business objects (Child, Conversation, Message)
- **Value Objects**: Immutable objects (EmotionResult, AudioMetrics)
- **Domain Services**: Business logic (EmotionAnalyzer, ContentModerator)
- **Domain Events**: Business events (SessionStarted, MessageReceived)

### 2. Application Layer
- **Use Cases**: Application-specific business rules
- **DTOs**: Data Transfer Objects
- **Application Services**: Orchestration logic
- **Interfaces**: Port definitions for external services

### 3. Infrastructure Layer
- **Repositories**: Data persistence implementations
- **External Services**: Third-party integrations
- **Framework**: Web framework specific code

### 4. Presentation Layer
- **API Controllers**: HTTP endpoints
- **GraphQL Resolvers**: GraphQL endpoints
- **WebSocket Handlers**: Real-time communication
- **Background Jobs**: Async task handlers

## Data Flow
1. Request → Controller
2. Controller → Use Case
3. Use Case → Domain Services/Repositories
4. Domain → Events → Event Handlers
5. Response ← Controller

## Key Design Decisions

### Event-Driven Architecture
All state changes emit domain events for loose coupling and extensibility.

```python
# Example: Child starts session
child.start_session(session_id)  # Emits SessionStarted event
await event_bus.publish(SessionStarted(child_id, session_id))
```

### CQRS Pattern
Separate read and write models for performance optimization.

```python
# Write Model
await conversation_service.send_message(message)

# Read Model
conversations = await conversation_query.get_history(child_id)
```

### Repository Pattern
Abstract data access for testability and flexibility.

```python
class IChildRepository(ABC):
    async def get(self, id: str) -> Optional[Child]: pass
    async def save(self, child: Child) -> None: pass
```

### Dependency Injection
Loose coupling between components using DI container.

```python
@inject
def __init__(self, child_repo: IChildRepository, ai_service: IAIService):
    self.child_repo = child_repo
    self.ai_service = ai_service
```

## Performance Considerations

### Caching Strategy
- **L1**: In-memory cache for frequently accessed data
- **L2**: Redis for distributed caching
- **L3**: Database query optimization

### Async Processing
- Non-blocking I/O for all external calls
- Background job processing for heavy tasks
- Connection pooling for database access

### Edge Computing
- Local processing for latency-sensitive operations
- Cloud fallback for complex AI tasks
- Smart routing based on device capabilities