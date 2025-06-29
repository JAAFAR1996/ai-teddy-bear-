# AI Teddy Bear Project Structure

## Overview
```
ai-teddy-bear/
│
├── config/                     # Configuration files
│   ├── default_config.json     # Default application configuration
│   └── default_schema.json     # JSON schema for configuration validation
│
├── src/                        # Main source code
│   ├── main.py                 # Application entry point
│   │
│   ├── application/            # Application services layer
│   │   ├── services/           # Core service implementations
│   │   │   ├── ai_service.py
│   │   │   ├── streaming_service.py
│   │   │   ├── llm_service_factory.py
│   │   │   ├── moderation_service.py
│   │   │   ├── memory_service.py
│   │   │   ├── parent_dashboard_service.py
│   │   │   └── voice_interaction_service.py
│   │   │
│   │   └── [REMOVED] system_orchestrator.py  # Replaced with clean SessionManager
│   │
│   ├── domain/                 # Domain models and business logic
│   │   ├── entities/           # Domain entity definitions
│   │   │   ├── child.py
│   │   │   ├── conversation.py
│   │   │   └── audio_stream.py
│   │   │
│   │   └── repositories/       # Repository interfaces
│   │       ├── base.py
│   │       ├── child_repository.py
│   │       └── conversation_repository.py
│   │
│   ├── infrastructure/         # Infrastructure and technical implementations
│   │   ├── config_manager.py
│   │   ├── container.py        # Dependency injection container
│   │   │
│   │   └── persistence/        # Database implementations
│   │       ├── base_sqlite_repository.py
│   │       ├── child_sqlite_repository.py
│   │       └── conversation_sqlite_repository.py
│   │
│   └── audio/                  # Audio processing modules
│       ├── audio_io.py
│       ├── audio_manager.py
│       ├── audio_processing.py
│       └── tts_playback.py
│
├── tests/                      # Test suite
│   ├── application/
│   ├── domain/
│   ├── infrastructure/
│   └── integration/
│
├── scripts/                    # Utility and management scripts
│   ├── health_check.py
│   ├── initialize_db.py
│   ├── backup_database.py
│   ├── generate_encryption_key.py
│   └── system_diagnostics.py
│
├── logs/                       # Log files
├── data/                       # Local data storage
├── uploads/                    # User uploaded content
├── exports/                    # Exported data and reports
│
├── monitoring/                 # Monitoring configuration
│   ├── prometheus.yml
│   ├── alert_rules.yml
│   └── alertmanager.yml
│
├── docs/                       # Project documentation
│   ├── ARCHITECTURE.md
│   ├── DEPLOYMENT.md
│   └── SECURITY.md
│
├── config/                     # Configuration files
│   ├── default_config.json
│   └── default_schema.json
│
├── .env.example                # Environment variable template
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── Dockerfile                  # Docker configuration
├── docker-compose.yml          # Docker compose configuration
├── Makefile                    # Development task automation
└── README.md                   # Project overview and quick start guide
```

## Key Components Breakdown

### 1. Domain Layer
- **Entities**: Represent core business objects
  - `Child`: Manages child profile information
  - `Conversation`: Tracks interaction details
  - `AudioStream`: Handles audio streaming metadata

- **Repositories**: Abstract data access interfaces
  - Define contract for data persistence
  - Support CRUD operations
  - Provide domain-specific query methods

### 2. Application Layer
- **Services**: Implement business logic
  - `StreamingService`: Real-time audio processing
  - `LLMServiceFactory`: AI language model interactions
  - `ModerationService`: Content safety filtering
  - `ParentDashboardService`: Analytics and controls

- **System Orchestrator**: Coordinates between different services
  - Manages complex interaction workflows
  - Handles cross-cutting concerns

### 3. Infrastructure Layer
- **Persistence**: Database implementations
  - SQLite-based repositories
  - Generic and specific repository implementations
  - Support for different data storage strategies

- **Configuration Management**
  - Dynamic configuration loading
  - Environment-based configuration
  - JSON schema validation

### 4. Audio Processing
- Dedicated audio-related modules
- Support for various audio operations
- Text-to-speech and speech-to-text capabilities

### 5. Monitoring and Logging
- Prometheus configuration
- Alert rules
- Performance monitoring setup

## Development Workflow
1. Configuration Management
2. Dependency Injection
3. Service Coordination
4. Data Persistence
5. Safety and Moderation
6. Logging and Monitoring

## Key Design Principles
- Clean Architecture
- Dependency Inversion
- Single Responsibility
- Open/Closed Principle
- Asynchronous Programming

## Technology Stack
- Python 3.9+
- SQLite
- Redis (optional)
- Docker
- Prometheus
- Multiple AI Providers (OpenAI, Anthropic, Google)

## Security Considerations
- COPPA Compliance
- GDPR Considerations
- Content Moderation
- Encryption
- Secure Configuration Management

## Extensibility
- Modular Design
- Plugin-based Architecture
- Multiple LLM Support
- Configurable Safety Controls
