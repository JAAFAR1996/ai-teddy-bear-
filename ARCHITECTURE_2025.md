# 🏗️ AI Teddy Bear System Architecture 2025

**Version:** 2.0  
**Last Updated:** January 2025  
**Architecture Pattern:** Clean Architecture + DDD + Event-Driven  
**Status:** Post-Restructure - Clean Implementation

---

## 📐 System Overview

The AI Teddy Bear system is a cloud-native interactive educational platform that creates meaningful emotional connections between children and AI through voice interactions, while ensuring privacy, safety, and developmental appropriateness.

### Key Capabilities
- 🗣️ **Natural Voice Interaction** - Real-time speech processing with emotion recognition
- 🧠 **Adaptive AI Responses** - Context-aware, age-appropriate conversations  
- 👶 **Child Development Focus** - Educational content and progress tracking
- 🔒 **Privacy-First Design** - COPPA-compliant with parental controls
- 🌐 **Multi-Device Support** - ESP32 hardware + mobile/web interfaces

## 🗺️ High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Edge Devices Layer                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐    │
│  │  ESP32 Bear │    │ Mobile App  │    │   Parent Dashboard  │    │
│  └──────┬──────┘    └──────┬──────┘    └──────────┬──────────┘    │
└─────────┼───────────────────┼───────────────────────┼───────────────┘
          │                   │                       │
          ▼                   ▼                       ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                             │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │ FastAPI Gateway │  │WebSocket Mgr │  │ Load Balancer      │    │
│  └────────┬────────┘  └──────┬───────┘  └─────────┬──────────┘    │
└───────────┼───────────────────┼─────────────────────┼───────────────┘
            │                   │                     │
            ▼                   ▼                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Application Services Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │Auth Service  │  │Audio Service │  │Child Service │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
│         │                  │                  │                     │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐            │
│  │AI Orchestrator│ │Content Engine│  │Safety Filter │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
└─────────┼───────────────────┼─────────────────┼─────────────────────┘
          │                   │                 │
          ▼                   ▼                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      External AI Services                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │OpenAI GPT-4 │  │ Hume AI     │  │Whisper ASR  │  │ElevenLabs│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────────┘
          │                   │                 │                │
          ▼                   ▼                 ▼                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         Data Layer                                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ PostgreSQL  │  │Redis Cache  │  │ S3 Storage  │  │Event Store│ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow Sequence

```
1. Child speaks to Teddy Bear
   └─> ESP32 captures audio
       └─> Audio streamed via WebSocket
           └─> Audio Service processes stream
               └─> Whisper transcribes to text
                   └─> Child Service fetches context
                       └─> AI Orchestrator generates response
                           ├─> Content filtered for safety
                           ├─> Emotion analysis via Hume
                           └─> Text converted to speech (ElevenLabs)
                               └─> Audio streamed back to ESP32
                                   └─> Teddy speaks to child
```

## 📦 Clean Architecture Layers

### 1. Domain Layer (Core Business Logic)
```
domain/
├── entities/
│   ├── child.py          # Child aggregate root
│   ├── conversation.py   # Conversation entity
│   ├── message.py        # Message value object
│   └── emotion.py        # Emotion value object
├── services/
│   ├── emotion_analyzer.py
│   ├── content_moderator.py
│   └── educational_advisor.py
└── repositories/
    ├── child_repository.py
    └── conversation_repository.py
```

### 2. Application Layer (Use Cases)
```
application/
├── use_cases/
│   ├── start_conversation.py
│   ├── process_child_input.py
│   ├── generate_response.py
│   └── end_conversation.py
├── services/
│   ├── ai_orchestrator.py
│   ├── audio_processor.py
│   └── notification_service.py
└── interfaces/
    ├── ai_service_interface.py
    └── storage_interface.py
```

### 3. Infrastructure Layer (External Services)
```
infrastructure/
├── persistence/
│   ├── postgres_child_repository.py
│   ├── redis_cache_service.py
│   └── s3_file_storage.py
├── ai_services/
│   ├── openai_adapter.py
│   ├── hume_adapter.py
│   └── elevenlabs_adapter.py
└── security/
    ├── jwt_service.py
    └── encryption_service.py
```

### 4. Presentation Layer (API)
```
api/
├── endpoints/
│   ├── auth.py
│   ├── children.py
│   ├── audio.py
│   └── dashboard.py
├── websocket/
│   ├── audio_stream_handler.py
│   └── real_time_updates.py
└── middleware/
    ├── authentication.py
    ├── rate_limiting.py
    └── error_handling.py
```

## 🗄️ Database Schema

```sql
-- Core Tables
CREATE TABLE children (
    id UUID PRIMARY KEY,
    udid VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    preferences JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(id),
    started_at TIMESTAMP DEFAULT NOW(),
    ended_at TIMESTAMP,
    context JSONB,
    summary TEXT
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    audio_url VARCHAR(500),
    emotion_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics Tables
CREATE TABLE emotion_logs (
    id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(id),
    emotion VARCHAR(50),
    confidence FLOAT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE learning_progress (
    id UUID PRIMARY KEY,
    child_id UUID REFERENCES children(id),
    skill VARCHAR(100),
    level INTEGER,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_conversations_child_id ON conversations(child_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_emotion_logs_child_timestamp ON emotion_logs(child_id, timestamp);
```

## 🚀 Deployment Architecture

### Production Environment (AWS)
```
┌─────────────────────────────────────────────────────────────────┐
│                        AWS Cloud                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                    VPC (10.0.0.0/16)                     │  │
│  │  ┌─────────────────────────────────────────────────┐   │  │
│  │  │          Public Subnet (10.0.1.0/24)            │   │  │
│  │  │  ┌────────────┐  ┌────────────┐  ┌──────────┐  │   │  │
│  │  │  │   ALB      │  │   NAT GW   │  │  Bastion │  │   │  │
│  │  │  └────┬───────┘  └──────┬─────┘  └──────────┘  │   │  │
│  │  └───────┼──────────────────┼──────────────────────┘   │  │
│  │          │                  │                           │  │
│  │  ┌───────▼──────────────────▼──────────────────────┐   │  │
│  │  │        Private Subnet (10.0.2.0/24)             │   │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │   │  │
│  │  │  │ ECS Fargate │  │ ECS Fargate │  │   RDS   │ │   │  │
│  │  │  │  (API)      │  │  (Workers)  │  │PostgreSQL│ │   │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────┘ │   │  │
│  │  │                                                  │   │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │   │  │
│  │  │  │ ElastiCache │  │   S3        │  │   SQS   │ │   │  │
│  │  │  │   (Redis)   │  │  Buckets    │  │  Queue  │ │   │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────┘ │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                │
│  ┌─────────────────┐  ┌─────────────┐  ┌───────────────┐    │
│  │   CloudWatch    │  │   X-Ray     │  │   WAF         │    │
│  │   Monitoring    │  │   Tracing   │  │   Firewall    │    │
│  └─────────────────┘  └─────────────┘  └───────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## 🔐 Security Architecture

### Security Layers
1. **Network Security**
   - AWS WAF for DDoS protection
   - VPC with private subnets
   - Security groups with least privilege

2. **Application Security**
   - JWT tokens with short expiry
   - Rate limiting per UDID
   - Input validation & sanitization

3. **Data Security**
   - Encryption at rest (AES-256)
   - TLS 1.3 for all communications
   - PII data anonymization

### Authentication Flow
```
1. Device Registration
   ESP32 → Generate UDID → Register with Backend → Store in DB

2. Session Management
   Mobile App → Login → JWT Token → Redis Session → API Access

3. Child Profile Access
   Parent Auth → Child Selection → Scoped Access → Limited Operations
```

## 📊 Monitoring & Observability

### Metrics Collection
```
Application Metrics → Prometheus → Grafana Dashboards
                  ↓
            Alert Manager → PagerDuty/Slack

Logs → CloudWatch → ElasticSearch → Kibana
    ↓
Log Analysis → Anomaly Detection → Auto Alerts

Traces → AWS X-Ray → Distributed Tracing → Performance Analysis
```

### Key Metrics
- Response time (p50, p95, p99)
- Error rates by endpoint
- Active conversations
- AI service latencies
- WebSocket connection stability

## 🎯 Design Principles

1. **Domain-Driven Design (DDD)**
   - Clear bounded contexts
   - Aggregate roots for consistency
   - Domain events for decoupling

2. **SOLID Principles**
   - Single Responsibility
   - Open/Closed
   - Liskov Substitution
   - Interface Segregation
   - Dependency Inversion

3. **12-Factor App**
   - Environment-based config
   - Stateless processes
   - Port binding
   - Disposability

4. **Security by Design**
   - Least privilege access
   - Defense in depth
   - Zero trust architecture

## 🔮 Future Roadmap

### Phase 1: Current (Q1 2025)
- Monolithic clean architecture
- Basic AI integration
- WebSocket streaming

### Phase 2: Scaling (Q2 2025)
- Extract audio service
- Implement event sourcing
- Add GraphQL API

### Phase 3: Advanced (Q3 2025)
- Full microservices
- Edge AI capabilities
- Multi-region deployment

### Phase 4: Innovation (Q4 2025)
- Federated learning
- Blockchain for data integrity
- AR/VR integration

---

## 🧱 Clean Architecture Implementation Details

### Domain Layer Implementation (`src/teddy_bear/domain/`)

```python
# Entities - Business objects with identity and behavior
class Child(AggregateRoot):
    def __init__(self, udid: DeviceID, name: ChildName, age: ChildAge):
        self._udid = udid
        self._name = name  
        self._age = age
        self._conversations: List[Conversation] = []
        self._events: List[DomainEvent] = []
    
    def start_conversation(self, session_type: SessionType) -> Conversation:
        """Business rule: Child can only have one active conversation"""
        if self.has_active_conversation():
            raise DomainException("Child already has active conversation")
        
        conversation = Conversation.create(self.id, session_type)
        self._conversations.append(conversation)
        self._events.append(ConversationStartedEvent(self.id, conversation.id))
        return conversation

# Value Objects - Immutable concepts
@dataclass(frozen=True) 
class Emotion:
    type: EmotionType
    confidence: float
    timestamp: datetime
    
    def __post_init__(self):
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0 and 1")
    
    def is_strong_emotion(self) -> bool:
        return self.confidence > 0.7

# Domain Services - Complex business rules
class ContentModerationService:
    def evaluate_content_safety(
        self, 
        content: str, 
        child_age: ChildAge,
        conversation_context: ConversationContext
    ) -> ContentSafetyResult:
        """Pure business logic for content safety evaluation"""
        safety_score = self._calculate_safety_score(content, child_age)
        
        if safety_score < 0.3:
            return ContentSafetyResult.UNSAFE
        elif safety_score < 0.7:
            return ContentSafetyResult.NEEDS_REVIEW
        else:
            return ContentSafetyResult.SAFE
```

### Application Layer Implementation (`src/teddy_bear/application/`)

```python
# Use Cases - Orchestrate business workflows
class ProcessChildInputUseCase:
    def __init__(
        self,
        child_repository: IChildRepository,
        ai_orchestrator: AIOrchestrator,
        conversation_service: ConversationService,
        event_publisher: IEventPublisher
    ):
        self._child_repo = child_repository
        self._ai_orchestrator = ai_orchestrator 
        self._conversation_service = conversation_service
        self._event_publisher = event_publisher
    
    async def execute(self, request: ProcessChildInputRequest) -> ProcessChildInputResponse:
        # 1. Load child aggregate
        child = await self._child_repo.get_by_udid(request.udid)
        
        # 2. Get or create conversation
        conversation = await self._conversation_service.get_active_conversation(child.id)
        
        # 3. Process input through AI orchestrator
        ai_response = await self._ai_orchestrator.process_input(
            audio_data=request.audio_data,
            child_context=ChildContext.from_child(child),
            conversation_context=ConversationContext.from_conversation(conversation)
        )
        
        # 4. Apply business rules
        message = conversation.add_child_message(request.text, ai_response.emotion)
        response_message = conversation.add_teddy_response(ai_response.text)
        
        # 5. Persist changes
        await self._child_repo.save(child)
        
        # 6. Publish domain events
        for event in child.get_uncommitted_events():
            await self._event_publisher.publish(event)
        
        return ProcessChildInputResponse(
            conversation_id=conversation.id,
            response_text=ai_response.text,
            response_audio_url=ai_response.audio_url,
            emotion_detected=ai_response.emotion
        )

# Application Services - Technical orchestration
class AIOrchestrator:
    def __init__(
        self,
        llm_provider: ILLMProvider,
        emotion_analyzer: IEmotionAnalyzer,
        speech_processor: ISpeechProcessor,
        content_moderator: ContentModerationService
    ):
        self._llm_provider = llm_provider
        self._emotion_analyzer = emotion_analyzer
        self._speech_processor = speech_processor
        self._content_moderator = content_moderator
    
    async def process_input(
        self,
        audio_data: AudioData,
        child_context: ChildContext,
        conversation_context: ConversationContext
    ) -> AIResponse:
        # Technical orchestration without business rules
        
        # 1. Speech to text
        text = await self._speech_processor.transcribe(audio_data)
        
        # 2. Emotion analysis
        emotion = await self._emotion_analyzer.analyze(audio_data)
        
        # 3. Generate response
        llm_response = await self._llm_provider.generate_response(
            text, child_context, conversation_context
        )
        
        # 4. Content safety check (business rule)
        safety_result = self._content_moderator.evaluate_content_safety(
            llm_response.text, child_context.age, conversation_context
        )
        
        if safety_result == ContentSafetyResult.UNSAFE:
            llm_response = await self._generate_safe_fallback_response(child_context)
        
        # 5. Text to speech
        audio_url = await self._speech_processor.synthesize(
            llm_response.text, child_context.preferred_voice
        )
        
        return AIResponse(
            text=llm_response.text,
            audio_url=audio_url,
            emotion=emotion,
            confidence=llm_response.confidence
        )
```

### Infrastructure Layer Implementation (`src/teddy_bear/infrastructure/`)

```python
# Repository Implementation - Data access without business logic
class PostgreSQLChildRepository(IChildRepository):
    def __init__(self, db_session: AsyncSession):
        self._session = db_session
    
    async def get_by_udid(self, udid: DeviceID) -> Child:
        """Convert database model to domain entity"""
        child_model = await self._session.get(ChildModel, {"udid": str(udid)})
        if not child_model:
            raise ChildNotFoundError(f"Child with UDID {udid} not found")
        
        return self._to_domain_entity(child_model)
    
    async def save(self, child: Child) -> None:
        """Convert domain entity to database model"""
        child_model = self._to_database_model(child)
        await self._session.merge(child_model)
        await self._session.commit()

# External Service Adapter - API integration without business logic  
class OpenAILLMProvider(ILLMProvider):
    def __init__(self, api_client: OpenAI, config: OpenAIConfig):
        self._client = api_client
        self._config = config
    
    async def generate_response(
        self,
        text: str,
        child_context: ChildContext,
        conversation_context: ConversationContext
    ) -> LLMResponse:
        """Pure API integration - no business rules"""
        
        system_prompt = self._build_system_prompt(child_context)
        conversation_history = self._format_conversation_history(conversation_context)
        
        response = await self._client.chat.completions.create(
            model=self._config.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": text}
            ],
            max_tokens=self._config.max_tokens,
            temperature=self._config.temperature
        )
        
        return LLMResponse(
            text=response.choices[0].message.content,
            confidence=self._calculate_confidence(response),
            tokens_used=response.usage.total_tokens
        )
```

### Presentation Layer Implementation (`src/teddy_bear/presentation/`)

```python
# FastAPI Endpoints - HTTP interface
@router.post("/children/{child_id}/conversations/{conversation_id}/messages")
async def send_message(
    child_id: UUID,
    conversation_id: UUID,
    request: SendMessageRequest,
    use_case: ProcessChildInputUseCase = Depends(get_process_input_use_case)
) -> MessageResponse:
    """HTTP endpoint - framework specific, delegates to use case"""
    
    try:
        result = await use_case.execute(
            ProcessChildInputRequest(
                udid=DeviceID(request.udid),
                audio_data=AudioData.from_base64(request.audio_data),
                text=request.text
            )
        )
        
        return MessageResponse(
            conversation_id=result.conversation_id,
            message_id=result.message_id,
            response_text=result.response_text,
            response_audio_url=result.response_audio_url,
            emotion_detected=result.emotion_detected.type.value
        )
        
    except DomainException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# WebSocket Handler - Real-time communication
class AudioStreamHandler:
    def __init__(self, audio_processor: AudioProcessor):
        self._audio_processor = audio_processor
    
    async def handle_connection(self, websocket: WebSocket):
        await websocket.accept()
        
        try:
            while True:
                # Receive audio chunk
                audio_chunk = await websocket.receive_bytes()
                
                # Process through application layer
                processed_audio = await self._audio_processor.process_chunk(
                    AudioChunk(data=audio_chunk, timestamp=datetime.utcnow())
                )
                
                # Send response back
                if processed_audio.has_response:
                    await websocket.send_bytes(processed_audio.response_data)
                    
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            await websocket.close(code=1011)
```

## 🔄 Dependency Injection Pattern

```python
# Dependency Container - IoC implementation
class TeddyBearContainer:
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        self._services[interface] = (implementation, "singleton")
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        self._services[interface] = (implementation, "transient")
    
    def get(self, interface: Type[T]) -> T:
        if interface not in self._services:
            raise DependencyNotRegisteredError(f"{interface} not registered")
        
        implementation, lifetime = self._services[interface]
        
        if lifetime == "singleton":
            if interface not in self._singletons:
                self._singletons[interface] = self._create_instance(implementation)
            return self._singletons[interface]
        else:
            return self._create_instance(implementation)

# Dependency Registration
def configure_container() -> TeddyBearContainer:
    container = TeddyBearContainer()
    
    # Domain Services
    container.register_singleton(ContentModerationService, ContentModerationService)
    
    # Application Services  
    container.register_transient(ProcessChildInputUseCase, ProcessChildInputUseCase)
    container.register_singleton(AIOrchestrator, AIOrchestrator)
    
    # Infrastructure
    container.register_singleton(IChildRepository, PostgreSQLChildRepository)
    container.register_singleton(ILLMProvider, OpenAILLMProvider)
    container.register_singleton(IEmotionAnalyzer, HumeEmotionAnalyzer)
    
    return container
```

---

**Note:** This architecture prioritizes child safety, data privacy, scalability, and maintainability while delivering magical AI-powered interactions. The Clean Architecture implementation ensures testability, maintainability, and independence from external frameworks. 