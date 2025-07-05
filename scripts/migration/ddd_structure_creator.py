import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)
"""
🏗️ DDD Structure Creator
Lead Architect: جعفر أديب
Creates complete Domain-Driven Design structure with base classes
"""


class DDDStructureCreator:
    """Creates the complete DDD directory structure and base classes"""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)

    def create_complete_structure(self):
        """Create the complete DDD structure"""
        logger.info("🏗️ Creating DDD Structure...")
        self._create_directories()
        self._create_domain_base_classes()
        self._create_application_base_classes()
        self._create_infrastructure_base_classes()
        self._create_presentation_base_classes()
        self._create_config_files()
        logger.info("✅ DDD Structure created successfully!")

    def _get_core_source_directories(self) -> List[str]:
        """Get core source code directories."""
        return [
            "src",
            "src/domain",
            "src/domain/entities",
            "src/domain/value_objects",
            "src/domain/services",
            "src/domain/repositories",
            "src/domain/events",
            "src/domain/exceptions",
            "src/application",
            "src/application/commands",
            "src/application/queries",
            "src/application/handlers",
            "src/application/dto",
            "src/application/ports",
            "src/application/ports/inbound",
            "src/application/ports/outbound",
            "src/infrastructure",
            "src/infrastructure/persistence",
            "src/infrastructure/persistence/repositories",
            "src/infrastructure/persistence/models",
            "src/infrastructure/ai",
            "src/infrastructure/messaging",
            "src/infrastructure/external_services",
            "src/infrastructure/config",
            "src/presentation",
            "src/presentation/api",
            "src/presentation/api/rest",
            "src/presentation/api/graphql",
            "src/presentation/websocket",
            "src/presentation/grpc",
            "src/shared",
            "src/shared/kernel",
            "src/shared/types",
            "src/shared/utils",
        ]

    def _get_test_directories(self) -> List[str]:
        """Get test directories."""
        return [
            "tests",
            "tests/unit",
            "tests/unit/domain",
            "tests/unit/application",
            "tests/unit/infrastructure",
            "tests/integration",
            "tests/e2e",
            "tests/performance",
        ]

    def _get_deployment_directories(self) -> List[str]:
        """Get deployment and operations directories."""
        return [
            "scripts",
            "scripts/migration",
            "scripts/deployment",
            "docker",
            "kubernetes",
            "kubernetes/base",
            "kubernetes/overlays",
            "kubernetes/overlays/development",
            "kubernetes/overlays/staging",
            "kubernetes/overlays/production",
        ]

    def _create_directory_group(self, directories: List[str]) -> None:
        """Create a group of directories with init files."""
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            if directory.startswith("src/") and not directory.endswith(".py"):
                init_file = dir_path / "__init__.py"
                if not init_file.exists():
                    init_content = self._get_init_content(directory)
                    init_file.write_text(init_content)

    def _create_directories(self):
        """Create all DDD directories"""
        all_directory_groups = [
            self._get_core_source_directories(),
            self._get_test_directories(),
            self._get_deployment_directories(),
        ]

        for directory_group in all_directory_groups:
            self._create_directory_group(directory_group)

    def _get_init_content(self, directory: str) -> str:
        """Get appropriate __init__.py content for directory"""
        layer_docs = {
            "src/domain": '"""Domain Layer - Pure Business Logic"""',
            "src/application": '"""Application Layer - Use Cases and Orchestration"""',
            "src/infrastructure": '"""Infrastructure Layer - External Dependencies"""',
            "src/presentation": '"""Presentation Layer - API and User Interface"""',
            "src/shared": '"""Shared Kernel - Common Components"""',
        }
        for layer, doc in layer_docs.items():
            if directory.startswith(layer):
                return f"{doc}\n"
        return '"""AI Teddy Bear - DDD Module"""\n'

    def _create_entity_base_classes(self) -> None:
        """Create domain entity base classes."""
        entity_content = """""\"
🎯 Domain Entity Base Classes
Lead Architect: جعفر أديب
""\"

from abc import ABC
from datetime import datetime
from typing import List, Any, Optional
from uuid import UUID, uuid4
from dataclasses import dataclass, field

@dataclass
class DomainEvent:
    ""\"Base class for all domain events""\"
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)
    event_type: str = field(init=False)
    
    def __post_init__(self):
        self.event_type = self.__class__.__name__

class Entity(ABC):
    ""\"Base entity class with identity and domain events""\"
    
    def __init__(self, entity_id: Optional[UUID] = None):
        self.id = entity_id or uuid4()
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self._domain_events: List[DomainEvent] = []
    
    def add_domain_event(self, event: DomainEvent) -> None:
        ""\"Add domain event to be published""\"
        self._domain_events.append(event)
    
    def clear_domain_events(self) -> List[DomainEvent]:
        ""\"Clear and return domain events""\"
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    def mark_as_modified(self) -> None:
        ""\"Mark entity as modified""\"
        self.updated_at = datetime.utcnow()
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)

class AggregateRoot(Entity):
    ""\"Base aggregate root with additional capabilities""\"
    
    def __init__(self, entity_id: Optional[UUID] = None):
        super().__init__(entity_id)
        self.version = 1
    
    def increment_version(self) -> None:
        ""\"Increment aggregate version for optimistic locking""\"
        self.version += 1
        self.mark_as_modified()
"""
        entity_file = self.project_root / "src/domain/entities/base.py"
        entity_file.write_text(entity_content)

    def _create_value_object_classes(self) -> None:
        """Create domain value object classes."""
        value_object_content = """""\"
💎 Domain Value Objects
Lead Architect: جعفر أديب
""\"

from abc import ABC
from dataclasses import dataclass
from typing import Any
from uuid import UUID

class ValueObject(ABC):
    ""\"Base class for value objects""\"
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__
    
    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))

@dataclass(frozen=True)
class ChildId(ValueObject):
    ""\"Strong-typed Child identifier""\"
    value: UUID
    
    @classmethod
    def generate(cls) -> 'ChildId':
        from uuid import uuid4
        return cls(uuid4())
    
    def __str__(self) -> str:
        return str(self.value)

@dataclass(frozen=True) 
class DeviceId(ValueObject):
    ""\"Strong-typed Device identifier""\"
    value: str
    
    def __post_init__(self):
        if not self.value or len(self.value) < 10:
            raise ValueError("DeviceId must be at least 10 characters")

@dataclass(frozen=True)
class AgeGroup(ValueObject):
    ""\"Child age group value object""\"
    min_age: int
    max_age: int
    name: str
    
    def __post_init__(self):
        if self.min_age < 0 or self.max_age < 0:
            raise ValueError("Ages must be positive")
        if self.min_age > self.max_age:
            raise ValueError("Min age cannot be greater than max age")
    
    def contains_age(self, age: int) -> bool:
        ""\"Check if age falls within this group""\"
        return self.min_age <= age <= self.max_age

@dataclass(frozen=True)
class Language(ValueObject):
    ""\"Language value object""\"
    code: str  # ISO 639-1 code
    name: str
    
    def __post_init__(self):
        if len(self.code) != 2:
            raise ValueError("Language code must be 2 characters")
"""
        vo_file = self.project_root / "src/domain/value_objects/__init__.py"
        vo_file.write_text(value_object_content)

    def _create_domain_service_classes(self) -> None:
        """Create domain service classes."""
        service_content = """""\"
⚙️ Domain Services
Lead Architect: جعفر أديب
""\"

from abc import ABC, abstractmethod
from typing import Protocol

class DomainService(ABC):
    ""\"Base class for domain services""\"
    pass

class IChildDomainService(Protocol):
    ""\"Interface for child-related domain operations""\"
    
    def can_interact_safely(self, child_id: str, content: str) -> bool:
        ""\"Check if child can safely interact with content""\"
        ...
    
    def calculate_learning_level(self, child_id: str) -> str:
        ""\"Calculate appropriate learning level""\"
        ...

class IAIInteractionService(Protocol):
    ""\"Interface for AI interaction domain logic""\"
    
    def should_escalate_to_parent(self, conversation_data: dict) -> bool:
        ""\"Determine if conversation should be escalated""\"
        ...
    
    def calculate_emotional_state(self, audio_data: bytes) -> dict:
        ""\"Calculate child's emotional state from audio""\"
        ...
"""
        service_file = self.project_root / "src/domain/services/__init__.py"
        service_file.write_text(service_content)

    def _create_domain_base_classes(self):
        """Create domain layer base classes"""
        self._create_entity_base_classes()
        self._create_value_object_classes()
        self._create_domain_service_classes()

    def _create_cqrs_classes(self) -> None:
        """Create CQRS command and query classes."""
        cqrs_content = """""\"
📋 CQRS Commands and Queries
Lead Architect: جعفر أديب
""\"

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar, Any, Optional
from uuid import UUID

# Type variables for generic handlers
TCommand = TypeVar('TCommand')
TQuery = TypeVar('TQuery')
TResult = TypeVar('TResult')

@dataclass
class Command(ABC):
    ""\"Base class for all commands""\"
    correlation_id: Optional[UUID] = None

@dataclass  
class Query(ABC):
    ""\"Base class for all queries""\"
    correlation_id: Optional[UUID] = None

class CommandHandler(ABC, Generic[TCommand, TResult]):
    ""\"Base command handler""\"
    
    @abstractmethod
    async def handle(self, command: TCommand) -> TResult:
        ""\"Handle the command""\"
        pass

class QueryHandler(ABC, Generic[TQuery, TResult]):
    ""\"Base query handler""\"
    
    @abstractmethod
    async def handle(self, query: TQuery) -> TResult:
        ""\"Handle the query""\"
        pass

# Child-specific commands
@dataclass
class RegisterChildCommand(Command):
    ""\"Command to register a new child""\"
    name: str
    age: int
    parent_id: UUID
    device_id: str
    language_preference: str = "en"

@dataclass
class StartConversationCommand(Command):
    ""\"Command to start a conversation""\"
    child_id: UUID
    initial_message: str
    audio_data: Optional[bytes] = None

# Child-specific queries
@dataclass
class GetChildProfileQuery(Query):
    ""\"Query to get child profile""\"
    child_id: UUID

@dataclass
class GetConversationHistoryQuery(Query):
    ""\"Query to get conversation history""\"
    child_id: UUID
    limit: int = 50
"""
        cqrs_file = self.project_root / "src/application/commands/__init__.py"
        cqrs_file.write_text(cqrs_content)

    def _create_dto_classes(self) -> None:
        """Create Data Transfer Object classes."""
        dto_content = """""\"
📦 Data Transfer Objects
Lead Architect: جعفر أديب
""\"

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

@dataclass
class ChildProfileDto:
    ""\"Child profile data transfer object""\"
    id: UUID
    name: str
    age: int
    language_preference: str
    created_at: datetime
    safety_settings: Dict[str, Any]
    learning_progress: Optional[Dict[str, Any]] = None

@dataclass
class ConversationDto:
    ""\"Conversation data transfer object""\"
    id: UUID
    child_id: UUID
    started_at: datetime
    ended_at: Optional[datetime]
    message_count: int
    emotional_summary: Dict[str, float]

@dataclass
class MessageDto:
    ""\"Message data transfer object""\"
    id: UUID
    conversation_id: UUID
    content: str
    sender: str  # 'child' or 'teddy'
    timestamp: datetime
    emotion_detected: Optional[Dict[str, float]] = None
    audio_url: Optional[str] = None

@dataclass
class AIResponseDto:
    ""\"AI response data transfer object""\"
    text: str
    audio_url: str
    emotion_adjustment: Dict[str, Any]
    processing_time_ms: int
    confidence_score: float
"""
        dto_file = self.project_root / "src/application/dto/__init__.py"
        dto_file.write_text(dto_content)

    def _create_application_base_classes(self):
        """Create application layer base classes"""
        self._create_cqrs_classes()
        self._create_dto_classes()

    def _create_infrastructure_base_classes(self):
        """Create infrastructure layer base classes"""
        repo_content = """""\"
🗄️ Repository Interfaces and Implementations
Lead Architect: جعفر أديب
""\"

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from uuid import UUID

T = TypeVar('T')
ID = TypeVar('ID')

class Repository(ABC, Generic[T, ID]):
    ""\"Base repository interface""\"
    
    @abstractmethod
    async def get_by_id(self, entity_id: ID) -> Optional[T]:
        ""\"Get entity by ID""\"
        pass
    
    @abstractmethod
    async def save(self, entity: T) -> T:
        ""\"Save entity""\"
        pass
    
    @abstractmethod
    async def delete(self, entity_id: ID) -> bool:
        ""\"Delete entity""\"
        pass
    
    @abstractmethod
    async def list_all(self) -> List[T]:
        ""\"List all entities""\"
        pass

class IChildRepository(Repository):
    ""\"Child repository interface""\"
    
    @abstractmethod
    async def get_by_device_id(self, device_id: str) -> Optional[object]:
        ""\"Get child by device ID""\"
        pass
    
    @abstractmethod
    async def get_children_by_parent(self, parent_id: UUID) -> List[object]:
        ""\"Get children by parent ID""\"
        pass

class IConversationRepository(Repository):
    ""\"Conversation repository interface""\"
    
    @abstractmethod
    async def get_active_conversation(self, child_id: UUID) -> Optional[object]:
        ""\"Get active conversation for child""\"
        pass
    
    @abstractmethod
    async def get_recent_conversations(self, child_id: UUID, limit: int) -> List[object]:
        ""\"Get recent conversations""\"
        pass
"""
        repo_file = (
            self.project_root
            / "src/infrastructure/persistence/repositories/__init__.py"
        )
        repo_file.write_text(repo_content)
        ai_content = """""\"
🤖 AI Service Interfaces
Lead Architect: جعفر أديب
""\"

from abc import ABC, abstractmethod
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AIRequest:
    ""\"AI processing request""\"
    text: str
    audio_data: Optional[bytes]
    child_context: Dict[str, Any]
    conversation_context: Dict[str, Any]

@dataclass
class AIResponse:
    ""\"AI processing response""\"
    text: str
    audio_url: str
    emotion_detected: Dict[str, float]
    safety_score: float
    processing_time_ms: int

class IOpenAIService(Protocol):
    ""\"OpenAI service interface""\"
    
    async def generate_response(self, request: AIRequest) -> str:
        ""\"Generate text response""\"
        ...

class ISpeechService(Protocol):
    ""\"Speech processing service interface""\"
    
    async def transcribe_audio(self, audio_data: bytes) -> str:
        ""\"Transcribe audio to text""\"
        ...
    
    async def synthesize_speech(self, text: str, voice_settings: Dict[str, Any]) -> str:
        ""\"Synthesize speech from text""\"
        ...

class IEmotionService(Protocol):
    ""\"Emotion detection service interface""\"
    
    async def analyze_emotion(self, audio_data: bytes) -> Dict[str, float]:
        ""\"Analyze emotion from audio""\"
        ...
    
    async def analyze_text_emotion(self, text: str) -> Dict[str, float]:
        ""\"Analyze emotion from text""\"
        ...
"""
        ai_file = self.project_root / "src/infrastructure/ai/__init__.py"
        ai_file.write_text(ai_content)

    def _create_presentation_base_classes(self):
        """Create presentation layer base classes"""
        api_content = """""\"
🌐 API Base Classes
Lead Architect: جعفر أديب
""\"

from abc import ABC
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class APIResponse:
    ""\"Standard API response format""\"
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = None
    request_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class BaseController(ABC):
    ""\"Base controller for API endpoints""\"
    
    def __init__(self):
        self.request_count = 0
    
    def success_response(self, data: Any = None) -> APIResponse:
        ""\"Create success response""\"
        return APIResponse(success=True, data=data)
    
    def error_response(self, error: str) -> APIResponse:
        ""\"Create error response""\"
        return APIResponse(success=False, error=error)

@dataclass
class WebSocketMessage:
    ""\"WebSocket message format""\"
    type: str
    data: Any
    timestamp: datetime = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

class BaseWebSocketHandler(ABC):
    ""\"Base WebSocket handler""\"
    
    def __init__(self):
        self.connected_clients: Dict[str, Any] = {}
    
    async def on_connect(self, websocket, session_id: str):
        ""\"Handle client connection""\"
        self.connected_clients[session_id] = websocket
    
    async def on_disconnect(self, session_id: str):
        ""\"Handle client disconnection""\"
        if session_id in self.connected_clients:
            del self.connected_clients[session_id]
    
    async def broadcast(self, message: WebSocketMessage):
        ""\"Broadcast message to all clients""\"
        for client in self.connected_clients.values():
            await client.send_json(message.__dict__)
"""
        api_file = self.project_root / "src/presentation/api/__init__.py"
        api_file.write_text(api_content)

    def _create_config_files(self):
        """Create configuration files"""
        dockerfile_content = """# AI Teddy Bear - Production Dockerfile
# Lead Architect: جعفر أديب

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/

# Create non-root user
RUN useradd --create-home --shell /bin/bash teddy
USER teddy

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Expose port
EXPOSE 8000

# Start application
CMD ["python", "-m", "src.main"]
"""
        dockerfile = self.project_root / "docker/Dockerfile"
        dockerfile.parent.mkdir(exist_ok=True)
        dockerfile.write_text(dockerfile_content)
        compose_content = """version: '3.8'

services:
  ai-teddy:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8000:8000"
      - "8765:8765"
    environment:
      - TEDDY_ENV=development
      - TEDDY_DEBUG=true
    volumes:
      - ../src:/app/src
      - teddy-data:/app/data
    depends_on:
      - redis
      - postgres
    networks:
      - teddy-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    networks:
      - teddy-network

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ai_teddy
      POSTGRES_USER: teddy
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - teddy-network

volumes:
  teddy-data:
  redis-data:
  postgres-data:

networks:
  teddy-network:
    driver: bridge
"""
        compose_file = self.project_root / "docker/docker-compose.yml"
        compose_file.write_text(compose_content)
        workflow_content = """name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        flake8 src/ tests/
        mypy src/
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src/ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image
      run: |
        docker build -f docker/Dockerfile -t ai-teddy:latest .
    
    - name: Push to registry
      run: |
        echo "Would push to container registry\"
"""
        workflow_dir = self.project_root / ".github/workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)
        workflow_file = workflow_dir / "ci.yml"
        workflow_file.write_text(workflow_content)


def main():
    """Main execution"""
    logger.info("🏗️ DDD Structure Creator")
    logger.info("Lead Architect: جعفر أديب")
    logger.info("=" * 40)
    creator = DDDStructureCreator()
    creator.create_complete_structure()
    logger.info("\n✅ Complete DDD structure created!")
    logger.info("\n📁 Created directories:")
    logger.info("  - src/domain (entities, value objects, services)")
    logger.info("  - src/application (commands, queries, handlers)")
    logger.info("  - src/infrastructure (persistence, AI, messaging)")
    logger.info("  - src/presentation (API, WebSocket, GraphQL)")
    logger.info("  - tests/ (unit, integration, e2e)")
    logger.info("  - docker/ (containerization)")
    logger.info("  - kubernetes/ (orchestration)")


if __name__ == "__main__":
    main()
