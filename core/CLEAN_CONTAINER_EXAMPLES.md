# 🏗️ Clean Container Usage Examples

## 🎯 Basic Usage

### Simple Configuration
```python
from core.infrastructure.container import container, configure_container

# Configure container
configure_container(
    database_url="sqlite+aiosqlite:///data/teddy.db",
    openai_api_key="sk-...",
    debug=False
)

# Get services
ai_service = container.ai_service()
voice_service = container.voice_service()
```

### Environment Configuration
```python
from core.infrastructure.container import container

# Configure from environment variables
# TEDDY_DATABASE_URL=sqlite+aiosqlite:///data/teddy.db
# TEDDY_OPENAI_API_KEY=sk-...
# TEDDY_DEBUG=false

container.config.from_env("TEDDY", delimiter="_")

# Services are automatically configured
ai_service = container.ai_service()
```

## 🚀 FastAPI Integration

### Clean Dependency Injection
```python
from fastapi import FastAPI, Depends
from core.infrastructure.container import (
    get_ai_service, 
    get_voice_service,
    get_child_service,
    initialize_container,
    shutdown_container
)

app = FastAPI()

@app.on_event("startup")
async def startup():
    await initialize_container()

@app.on_event("shutdown") 
async def shutdown():
    await shutdown_container()

@app.post("/api/chat")
async def chat(
    message: str,
    ai_service: AIService = Depends(get_ai_service),
    child_service: ChildService = Depends(get_child_service)
):
    child = await child_service.get_current_child()
    response = await ai_service.generate_response(message, child)
    return response
```

### Using Provider Injection
```python
from dependency_injector.wiring import Provide, inject
from core.infrastructure.container import Container

@inject
async def process_audio(
    audio_data: bytes,
    ai_service: AIService = Provide[Container.ai_service],
    voice_service: VoiceService = Provide[Container.voice_service]
):
    # Transcribe audio
    text = await voice_service.transcribe_audio(audio_data)
    
    # Generate response
    response = await ai_service.generate_response(text)
    
    return response
```

## 🧪 Testing with Mocks

### Simple Override
```python
import pytest
from core.infrastructure.container import container

@pytest.fixture
def mock_ai_service():
    class MockAI:
        async def generate_response(self, text):
            return {"text": "Mock response", "emotion": "happy"}
    return MockAI()

@pytest.fixture
def override_container(mock_ai_service):
    container.ai_service.override(mock_ai_service)
    yield
    container.ai_service.reset_override()

def test_something(override_container):
    ai_service = container.ai_service()
    # Will return mock
    assert isinstance(ai_service, MockAI)
```

### Test Container Helper
```python
from core.infrastructure.container import TestContainer

def test_with_helper():
    mock_ai = Mock()
    mock_voice = Mock()
    
    with TestContainer() as test_container:
        test_container.override_ai_service(mock_ai)
        test_container.override_voice_service(mock_voice) 
        
        # Use mocked services
        ai_service = container.ai_service()
        voice_service = container.voice_service()
        
        assert ai_service is mock_ai
        assert voice_service is mock_voice
    
    # Overrides automatically reset
```

## 🔧 Advanced Configuration

### Custom Configuration Source
```python
from core.infrastructure.container import container

# From dictionary
config_dict = {
    "database_url": "postgresql+asyncpg://user:pass@localhost/db",
    "redis_url": "redis://localhost:6379/0",
    "openai_api_key": "sk-...",
    "debug": True
}

container.config.from_dict(config_dict)
```

### Multiple Environment Sources
```python
# Load from multiple sources
container.config.from_env("APP")  # APP_DATABASE_URL, etc.
container.config.from_env("TEDDY")  # TEDDY_OPENAI_API_KEY, etc.

# Override specific values
container.config.override({
    "debug": True,
    "log_level": "DEBUG"
})
```

## 🌐 Application Lifecycle

### Context Manager Approach
```python
from core.infrastructure.container import ContainerContext

async def main():
    config = {
        "database_url": "sqlite+aiosqlite:///data/teddy.db",
        "openai_api_key": "sk-...",
        "debug": False
    }
    
    async with ContainerContext(**config) as container:
        # Container is initialized
        ai_service = container.ai_service()
        
        # Do work...
        response = await ai_service.generate_response("Hello")
        print(response)
    
    # Container automatically shut down
```

### Manual Lifecycle Management
```python
from core.infrastructure.container import (
    configure_container,
    initialize_container, 
    shutdown_container
)

async def main():
    try:
        # Configure
        configure_container(
            database_url="sqlite+aiosqlite:///data/teddy.db",
            openai_api_key="sk-..."
        )
        
        # Initialize resources
        await initialize_container()
        
        # Use services...
        ai_service = container.ai_service()
        response = await ai_service.generate_response("Hello")
        
    finally:
        # Always cleanup
        await shutdown_container()
```

## 🔍 Debugging & Inspection

### Check Container State
```python
from core.infrastructure.container import container

# Check what providers are available
providers = [
    'settings', 'database_pool', 'cache_service',
    'ai_service', 'voice_service', 'child_service'
]

for provider_name in providers:
    if hasattr(container, provider_name):
        provider = getattr(container, provider_name)
        print(f"✅ {provider_name}: {provider}")
    else:
        print(f"❌ {provider_name}: Missing")
```

### Provider Information
```python
# Check provider type
ai_provider = container.ai_service
print(f"Provider type: {type(ai_provider)}")
print(f"Is singleton: {ai_provider.is_singleton}")

# Check configuration
config = container.config
print(f"Database URL: {config.provided.get('database_url', 'Not set')}")
print(f"Debug mode: {config.provided.get('debug', False)}")
```

## 🚀 Production Deployment

### Docker Environment
```dockerfile
# Dockerfile
ENV TEDDY_DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/teddy
ENV TEDDY_REDIS_URL=redis://redis:6379/0
ENV TEDDY_OPENAI_API_KEY=sk-...
ENV TEDDY_DEBUG=false

CMD ["python", "-m", "core.main"]
```

### Kubernetes ConfigMap
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: teddy-config
data:
  TEDDY_DATABASE_URL: "postgresql+asyncpg://..."
  TEDDY_DEBUG: "false"
---
apiVersion: v1  
kind: Secret
metadata:
  name: teddy-secrets
data:
  TEDDY_OPENAI_API_KEY: "c2stLi4u"  # base64 encoded
```

### Application Startup
```python
# main.py
import asyncio
import logging
from core.infrastructure.container import container, initialize_container
from core.api.production_api import app

async def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Configure container from environment
    container.config.from_env("TEDDY", delimiter="_")
    
    # Initialize
    await initialize_container()
    
    # Start server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📊 Performance Benefits

### Before (Broken Container)
- ❌ Threading locks in async context
- ❌ Manual circular dependency detection
- ❌ Complex singleton management
- ❌ Hard to test and mock

### After (Clean Container)  
- ✅ No threading locks needed
- ✅ Automatic circular dependency detection
- ✅ Built-in singleton/factory patterns
- ✅ Easy testing with provider overrides
- ✅ Clean declarative configuration
- ✅ Type-safe dependency injection

## 🎯 Key Patterns

### Singleton vs Factory
```python
# Singleton - same instance always
settings1 = container.settings()
settings2 = container.settings()
assert settings1 is settings2  # True

# Factory - new instance each time  
session1 = container.session_manager()
session2 = container.session_manager()
assert session1 is not session2  # True
```

### Dependency Chain
```python
# Clean dependency chain:
# child_service -> child_repository -> database_pool
# child_service -> cache_service -> settings

child_service = container.child_service()
# All dependencies automatically injected!
```

### Provider Override for Testing
```python
# Easy mocking without complex setup
container.ai_service.override(lambda: MockAIService())

ai_service = container.ai_service()  # Returns MockAIService
```

**Result: Clean, testable, maintainable dependency injection! 🚀** 