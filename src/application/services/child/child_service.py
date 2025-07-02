"""
Child Profile Service - Manages child profiles connected to ESP32 devices
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class InteractionType(str, Enum):
    """Types of child interactions"""
    CONVERSATION = "conversation"
    STORY_REQUEST = "story_request"
    GAME = "game"
    LEARNING = "learning"
    EMOTIONAL_SUPPORT = "emotional_support"


class ChildProfile:
    """Child profile model"""
    
    def __init__(
        self, 
        name: str, 
        age: int, 
        device_id: str, 
        language: str = "Arabic"
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age
        self.device_id = device_id
        self.language = language
        self.created_at = datetime.utcnow()
        self.preferences = {}
        self.conversation_history = []
        self.learning_progress = {}
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "device_id": self.device_id,
            "language": self.language,
            "created_at": self.created_at.isoformat(),
            "preferences": self.preferences,
            "conversation_count": len(self.conversation_history),
            "learning_progress": self.learning_progress
        }


class SessionData:
    """Conversation session data"""
    
    def __init__(self, child_id: str, device_id: str):
        self.session_id = str(uuid.uuid4())
        self.child_id = child_id
        self.device_id = device_id
        self.started_at = datetime.utcnow()
        self.messages = []
        self.interaction_type = InteractionType.CONVERSATION
        
    def add_message(self, message: str, response: str, metadata: Dict[str, Any] = None):
        self.messages.append({
            "timestamp": datetime.utcnow().isoformat(),
            "user_message": message,
            "ai_response": response,
            "metadata": metadata or {}
        })


class CloudChildService:
    """Service for managing child profiles and conversations."""

    def __init__(self):
        self.children: Dict[str, ChildProfile] = {}
        self.device_to_child: Dict[str, str] = {}  # device_id -> child_id
        self.active_sessions: Dict[str, SessionData] = {}
        logger.info("CloudChildService initialized")

    async def create_child(
        self, 
        name: str, 
        age: int, 
        device_id: str, 
        language: str = "Arabic",
        preferences: Dict[str, Any] = None
    ) -> ChildProfile:
        """
        Create a new child profile
        
        Args:
            name: Child's name
            age: Child's age  
            device_id: Associated ESP32 device ID
            language: Preferred language
            preferences: Child preferences
            
        Returns:
            Created child profile
        """
        try:
            # Check if device already has a child
            if device_id in self.device_to_child:
                existing_child_id = self.device_to_child[device_id]
                existing_child = self.children[existing_child_id]
                logger.warning(f"Device {device_id} already linked to child {existing_child.name}")
                return existing_child
            
            # Create new child
            child = ChildProfile(name, age, device_id, language)
            if preferences:
                child.preferences.update(preferences)
            
            # Store child
            self.children[child.id] = child
            self.device_to_child[device_id] = child.id
            
            logger.info(f"Child profile created: {name} (age {age}) for device {device_id}")
            return child
            
        except Exception as e:
            logger.error(f"Child creation failed: {str(e)}")
            raise

    async def get_by_device_id(self, device_id: str) -> Optional[ChildProfile]:
        """Get child profile by device ID"""
        try:
            child_id = self.device_to_child.get(device_id)
            if child_id:
                return self.children.get(child_id)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get child for device {device_id}: {str(e)}")
            return None

    async def get_child(self, child_id: str) -> Optional[ChildProfile]:
        """Get child profile by ID"""
        return self.children.get(child_id)

    async def update_child_preferences(
        self, 
        child_id: str, 
        preferences: Dict[str, Any]
    ) -> bool:
        """Update child preferences"""
        try:
            child = self.children.get(child_id)
            if not child:
                return False
                
            child.preferences.update(preferences)
            logger.info(f"Updated preferences for child {child.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update preferences: {str(e)}")
            return False

    async def start_session(
        self, 
        device_id: str, 
        interaction_type: InteractionType = InteractionType.CONVERSATION
    ) -> Optional[str]:
        """Start a new conversation session"""
        try:
            child = await self.get_by_device_id(device_id)
            if not child:
                logger.warning(f"No child found for device {device_id}")
                return None
            
            session = SessionData(child.id, device_id)
            session.interaction_type = interaction_type
            
            self.active_sessions[session.session_id] = session
            
            logger.info(f"Started session {session.session_id} for child {child.name}")
            return session.session_id
            
        except Exception as e:
            logger.error(f"Failed to start session: {str(e)}")
            return None

    async def save_conversation(
        self, 
        device_id: str, 
        message: str, 
        response: str, 
        session_id: str = None,
        metadata: Dict[str, Any] = None
    ) -> bool:
        """Save conversation exchange"""
        try:
            child = await self.get_by_device_id(device_id)
            if not child:
                return False
            
            # Add to child's history
            conversation_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                "response": response,
                "session_id": session_id,
                "metadata": metadata or {}
            }
            
            child.conversation_history.append(conversation_entry)
            
            # Update active session if exists
            if session_id and session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                session.add_message(message, response, metadata)
            
            logger.info(f"Saved conversation for child {child.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save conversation: {str(e)}")
            return False

    async def register_device(
        self, 
        device_id: str, 
        firmware_version: str, 
        hardware_info: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Register device and prepare for child linking"""
        try:
            # This is a placeholder for device registration
            # In a real system, this would integrate with device registry
            
            logger.info(f"Device registration prepared: {device_id}")
            return {
                "registration_id": f"REG_{device_id}_{datetime.utcnow().timestamp()}",
                "status": "ready_for_child_profile"
            }
            
        except Exception as e:
            logger.error(f"Device registration failed: {str(e)}")
            raise

    async def get_child_stats(self, child_id: str) -> Dict[str, Any]:
        """Get child interaction statistics"""
        try:
            child = self.children.get(child_id)
            if not child:
                return {}
            
            total_conversations = len(child.conversation_history)
            
            # Analyze conversation types
            interaction_types = {}
            for conv in child.conversation_history[-50:]:  # Last 50 conversations
                conv_type = conv.get("metadata", {}).get("category", "general")
                interaction_types[conv_type] = interaction_types.get(conv_type, 0) + 1
            
            return {
                "total_conversations": total_conversations,
                "interaction_types": interaction_types,
                "account_age_days": (datetime.utcnow() - child.created_at).days,
                "preferred_language": child.language,
                "learning_progress": child.learning_progress
            }
            
        except Exception as e:
            logger.error(f"Failed to get child stats: {str(e)}")
            return {}

    async def end_session(self, session_id: str) -> bool:
        """End an active session"""
        try:
            if session_id in self.active_sessions:
                session = self.active_sessions[session_id]
                del self.active_sessions[session_id]
                
                logger.info(f"Ended session {session_id} with {len(session.messages)} messages")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to end session: {str(e)}")
            return False

    async def get_all_children(self) -> List[ChildProfile]:
        """Get all child profiles"""
        return list(self.children.values())

    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics"""
        return {
            "total_children": len(self.children),
            "active_sessions": len(self.active_sessions),
            "total_conversations": sum(
                len(child.conversation_history) for child in self.children.values()
            )
        }
