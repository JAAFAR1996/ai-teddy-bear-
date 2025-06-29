# Coding Standards

## Python Code Style

### General Guidelines
- Follow PEP 8 style guide
- Use type hints for all functions
- Maximum line length: 88 characters (Black formatter)
- Use descriptive variable and function names

### Naming Conventions
```python
# Classes: PascalCase
class ConversationService:
    pass

# Functions/Variables: snake_case
def process_audio_message():
    user_input = "hello"

# Constants: UPPER_SNAKE_CASE
MAX_MESSAGE_LENGTH = 500

# Private methods: _leading_underscore
def _internal_helper():
    pass
```

### Type Hints
```python
from typing import Optional, List, Dict, Any

async def generate_response(
    message: str,
    context: Dict[str, Any],
    max_tokens: int = 150
) -> Optional[str]:
    """Generate AI response with proper typing."""
    pass
```

### Docstrings
Use Google-style docstrings:

```python
def analyze_emotion(text: str, confidence_threshold: float = 0.7) -> EmotionResult:
    """
    Analyze emotion from text input.
    
    Args:
        text: Input text to analyze
        confidence_threshold: Minimum confidence for emotion detection
        
    Returns:
        EmotionResult containing primary emotion and confidence scores
        
    Raises:
        ValueError: If text is empty or invalid
        
    Example:
        >>> result = analyze_emotion("I'm so happy today!")
        >>> print(result.primary_emotion)  # "happy"
    """
    pass
```

### Error Handling
```python
# Use specific exceptions
class ConversationError(Exception):
    """Base exception for conversation-related errors."""
    pass

class SessionNotFoundError(ConversationError):
    """Raised when session cannot be found."""
    pass

# Proper exception handling
try:
    session = await get_session(session_id)
except SessionNotFoundError:
    logger.warning(f"Session {session_id} not found")
    raise HTTPException(status_code=404, detail="Session not found")
```

### Async/Await Best Practices
```python
# Good: Use async/await consistently
async def process_request():
    result = await external_api_call()
    await save_to_database(result)
    return result

# Bad: Mixing sync and async
def bad_function():
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_function())
```

## Code Organization

### File Structure
```
src/
├── core/
│   ├── domain/          # Business logic
│   ├── application/     # Use cases
│   └── infrastructure/  # External concerns
├── api/                 # Web layer
├── services/           # External services
└── tests/              # Test files
```

### Import Organization
```python
# Standard library imports
import asyncio
from datetime import datetime
from typing import Optional, List

# Third-party imports
from fastapi import FastAPI, HTTPException
from sqlalchemy import Column, String

# Local imports
from src.core.domain.entities import Child
from src.core.application.services import ConversationService
```

## Testing Standards

### Test Structure
```python
class TestConversationService:
    """Test conversation service functionality."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.service = ConversationService()
    
    async def test_start_conversation_success(self):
        """Test successful conversation start."""
        # Arrange
        child_id = "test-child-123"
        
        # Act
        result = await self.service.start_conversation(child_id)
        
        # Assert
        assert result.session_id is not None
        assert result.welcome_message is not None
```

### Mock Usage
```python
from unittest.mock import AsyncMock, patch

@patch('src.services.ai_service.OpenAIService')
async def test_ai_response_generation(mock_ai_service):
    # Setup mock
    mock_ai_service.return_value.generate.return_value = "Test response"
    
    # Test
    response = await generate_ai_response("Hello")
    assert response == "Test response"
```

## Performance Guidelines

### Database Queries
```python
# Good: Use async and proper indexing
async def get_conversations(child_id: str) -> List[Conversation]:
    query = select(Conversation).where(
        Conversation.child_id == child_id
    ).order_by(Conversation.created_at.desc())
    
    result = await session.execute(query)
    return result.scalars().all()

# Bad: N+1 queries
for conversation in conversations:
    messages = await get_messages(conversation.id)  # N+1 problem
```

### Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(input_data: str) -> str:
    """Cache expensive computations."""
    return complex_calculation(input_data)
```

### Memory Management
```python
# Good: Use generators for large datasets
def process_large_dataset():
    for item in large_dataset:
        yield process_item(item)

# Bad: Loading everything into memory
def bad_processing():
    all_items = list(large_dataset)  # Memory intensive
    return [process_item(item) for item in all_items]
```