# API Documentation

## Overview

The Smart Teddy Bear application provides several internal APIs for managing child interactions, conversations, and audio processing.

## Core APIs

### Child Management API

#### Create Child Profile
```python
async def create_child(name: str, age: int, preferences: Optional[ChildPreferences] = None) -> Child
```
- Creates a new child profile
- Requires parental consent before allowing interactions
- Returns the created Child entity

#### Update Child Preferences
```python
async def update_preferences(child_id: UUID, preferences: dict) -> Child
```
- Updates a child's preferences
- Returns the updated Child entity

#### Grant Consent
```python
async def grant_consent(child_id: UUID, parent_id: UUID, consent_data: dict) -> Child
```
- Grants parental consent for specific activities
- Required for COPPA compliance
- Returns the updated Child entity

### Conversation API

#### Start Conversation
```python
async def start_conversation(child: Child, initial_message: Optional[str] = None) -> Conversation
```
- Starts a new conversation session
- Requires valid child profile with consent
- Returns the created Conversation entity

#### Add Child Message
```python
async def add_child_message(
    conversation_id: UUID,
    content: str,
    content_type: ContentType,
    emotion: Optional[str] = None
) -> Conversation
```
- Adds a child's message to the conversation
- Supports text and audio content types
- Optional emotion tracking
- Returns the updated Conversation

#### Get AI Response
```python
async def get_response(conversation: Conversation, child: Child) -> AIResponse
```
- Generates AI response based on conversation context
- Applies content moderation
- Returns structured AI response

### Audio Processing API

#### Record Audio
```python
async def record_audio(duration: int = 5) -> bytes
```
- Records audio input for specified duration
- Returns raw audio data

#### Text to Speech
```python
async def text_to_speech(text: str, voice_name: str = "en-US-JennyNeural") -> bytes
```
- Converts text to speech using Azure services
- Returns audio data for playback

## Data Models

### Child Entity
```python
class Child:
    id: UUID
    name: str
    age: int
    preferences: ChildPreferences
    parental_consent: ParentalConsent
    created_at: datetime
```

### Conversation Entity
```python
class Conversation:
    id: UUID
    child_id: UUID
    messages: List[Message]
    metadata: dict
    created_at: datetime
```

### Message Entity
```python
class Message:
    content: Content
    interaction_type: InteractionType
    timestamp: datetime
    emotion: Optional[str]
    processed: bool
```

## Error Handling

All APIs follow consistent error handling patterns:

```python
class APIError(Exception):
    """Base class for API errors"""
    pass

class ValidationError(APIError):
    """Invalid input data"""
    pass

class ConsentError(APIError):
    """Missing or invalid consent"""
    pass

class ContentModerationError(APIError):
    """Content violates moderation rules"""
    pass
```

## Security Considerations

1. All API calls require proper authentication
2. Child data is encrypted at rest
3. Content moderation is applied to all interactions
4. Parental consent is strictly enforced
5. All operations are logged for audit purposes

## Rate Limiting

- OpenAI API: 60 requests per minute
- Azure Speech: 100 requests per minute
- Database operations: 1000 per minute

## Best Practices

1. Always validate input data
2. Handle errors gracefully
3. Log important operations
4. Check consent before interactions
5. Use type hints for better code quality

## Examples

### Creating a Child Profile

```python
# Initialize services
child_service = container.child_service

# Create child profile
child = await child_service.create_child(
    name="John Doe",
    age=5,
    preferences=ChildPreferences(
        language="en-US",
        voice_type="friendly",
        interaction_style="playful"
    )
)

# Grant consent
await child_service.grant_consent(
    child_id=child.id,
    parent_id=parent_id,
    consent_data={
        "data_collection": True,
        "audio_recording": True,
        "ai_interaction": True
    }
)
```

### Starting a Conversation

```python
# Initialize services
conversation_service = container.conversation_service

# Start conversation
conversation = await conversation_service.start_conversation(child)

# Add child message
await conversation_service.add_child_message(
    conversation_id=conversation.id,
    content="Hello teddy!",
    content_type=ContentType.TEXT
)

# Get AI response
response = await ai_service.get_response(conversation, child)
print(f"AI: {response.content}")
