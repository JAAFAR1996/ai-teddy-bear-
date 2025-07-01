from typing import Dict, List, Any, Optional

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

def custom_openapi(FastAPI) -> None:
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="AI Teddy Bear API",
        version="2.0.0",
        description="""
        # AI Teddy Bear API Documentation
        
        ## Overview
        The AI Teddy Bear API provides a secure, scalable interface for 
        interactive AI-powered conversations with children.
        
        ## Authentication
        All endpoints require JWT authentication. Obtain a token via `/auth/login`.
        
        ## Rate Limiting
        - 60 requests per minute per user
        - 10 concurrent connections per user
        
        ## Supported Languages
        - Arabic (ar)
        - English (en)
        - Spanish (es)
        - French (fr)
        
        ## Error Codes
        - 400: Bad Request
        - 401: Unauthorized
        - 403: Forbidden
        - 429: Rate Limited
        - 500: Internal Server Error
        """,
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Add example schemas
    openapi_schema["components"]["schemas"]["ConversationStartedEvent"] = {
        "type": "object",
        "properties": {
            "event_type": {"type": "string", "example": "conversation.started"},
            "child_id": {"type": "string", "example": "child-123"},
            "session_id": {"type": "string", "example": "session-456"},
            "timestamp": {"type": "string", "format": "date-time"}
        }
    }
    
    # Add webhook documentation
    openapi_schema["webhooks"] = {
        "conversation.started": {
            "post": {
                "summary": "Conversation started webhook",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "$ref": "#/components/schemas/ConversationStartedEvent"
                            }
                        }
                    }
                }
            }
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Example endpoint documentation
def get_conversation_docs() -> Any:
    return {
        "summary": "Start a new conversation",
        "description": """
        Start a new conversation session for a child.
        
        **Requirements:**
        - Valid JWT token
        - Child must exist and belong to authenticated parent
        - Child cannot have active session
        
        **Response:**
        Returns session details and welcome message.
        """,
        "responses": {
            200: {
                "description": "Conversation started successfully",
                "content": {
                    "application/json": {
                        "example": {
                            "session_id": "session-123",
                            "welcome_message": "مرحبا بك يا صديقي!",
                            "voice_url": "/audio/welcome-123.mp3"
                        }
                    }
                }
            },
            400: {"description": "Invalid request"},
            401: {"description": "Authentication required"},
            403: {"description": "Child access denied"}
        }
    }