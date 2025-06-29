#!/usr/bin/env python3
"""
📨 Message Broker System
Lead Architect: جعفر أديب (Jaafar Adeeb)
Event-driven messaging with Redis pub/sub
"""

import asyncio
import json
from typing import Dict, Any, Callable, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import redis.asyncio as redis
import structlog

logger = structlog.get_logger()


@dataclass
class Message:
    """Event message"""
    topic: str
    payload: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    message_id: str = field(default_factory=lambda: str(id(object())))
    headers: Dict[str, str] = field(default_factory=dict)


MessageHandler = Callable[[Message], None]


class MessageBroker:
    """
    🏗️ Enterprise Message Broker
    Features:
    - Redis pub/sub messaging
    - Topic-based routing
    - Message handlers registration
    - Dead letter queue
    - Message persistence
    """
    
    def __init__(self, broker_url: str = "redis://localhost:6379/1"):
        self.broker_url = broker_url
        self.client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        
        # Message handlers
        self.handlers: Dict[str, List[MessageHandler]] = {}
        
        # Background tasks
        self._subscriber_task: Optional[asyncio.Task] = None
        self._running = False
        self._initialized = False
    
    async def initialize(self):
        """Initialize message broker"""
        if self._initialized:
            return
        
        logger.info("📨 Initializing message broker", url=self._mask_url())
        
        try:
            # Create Redis client
            self.client = redis.from_url(self.broker_url)
            
            # Test connection
            await self.client.ping()
            
            # Create pub/sub client
            self.pubsub = self.client.pubsub()
            
            self._initialized = True
            logger.info("✅ Message broker initialized successfully")
            
        except Exception as e:
            logger.error("❌ Failed to initialize message broker", error=str(e))
            raise
    
    async def start(self):
        """Start message broker services"""
        if not self._initialized:
            await self.initialize()
        
        if self._running:
            return
        
        logger.info("🚀 Starting message broker services...")
        
        self._running = True
        
        # Start subscriber task
        self._subscriber_task = asyncio.create_task(self._message_subscriber())
        
        logger.info("✅ Message broker services started")
    
    async def stop(self):
        """Stop message broker services"""
        logger.info("🛑 Stopping message broker services...")
        
        self._running = False
        
        # Cancel subscriber task
        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Message broker services stopped")
    
    async def publish(self, topic: str, payload: Dict[str, Any], headers: Optional[Dict[str, str]] = None):
        """Publish message to topic"""
        if not self._initialized:
            raise RuntimeError("Message broker not initialized")
        
        message = Message(
            topic=topic,
            payload=payload,
            headers=headers or {}
        )
        
        try:
            # Serialize message
            message_data = {
                "topic": message.topic,
                "payload": message.payload,
                "timestamp": message.timestamp.isoformat(),
                "message_id": message.message_id,
                "headers": message.headers
            }
            
            serialized_message = json.dumps(message_data)
            
            # Publish to Redis
            await self.client.publish(topic, serialized_message)
            
            # Also store in stream for persistence
            await self.client.xadd(
                f"stream:{topic}",
                message_data,
                maxlen=1000  # Keep last 1000 messages
            )
            
            logger.info("📤 Message published", 
                       topic=topic, message_id=message.message_id)
            
        except Exception as e:
            logger.error("❌ Failed to publish message", 
                        topic=topic, error=str(e))
            raise
    
    def subscribe(self, topic: str, handler: MessageHandler):
        """Subscribe to topic with message handler"""
        if topic not in self.handlers:
            self.handlers[topic] = []
        
        self.handlers[topic].append(handler)
        
        logger.info("📥 Subscribed to topic", 
                   topic=topic, handler=handler.__name__)
    
    def unsubscribe(self, topic: str, handler: MessageHandler):
        """Unsubscribe from topic"""
        if topic in self.handlers and handler in self.handlers[topic]:
            self.handlers[topic].remove(handler)
            
            if not self.handlers[topic]:
                del self.handlers[topic]
            
            logger.info("📤 Unsubscribed from topic", 
                       topic=topic, handler=handler.__name__)
    
    async def _message_subscriber(self):
        """Background task for message subscription"""
        logger.info("👂 Starting message subscriber...")
        
        try:
            # Subscribe to all topics with handlers
            for topic in self.handlers.keys():
                await self.pubsub.subscribe(topic)
            
            while self._running:
                try:
                    # Get message with timeout
                    message = await asyncio.wait_for(
                        self.pubsub.get_message(ignore_subscribe_messages=True),
                        timeout=1.0
                    )
                    
                    if message and message["type"] == "message":
                        await self._handle_message(message)
                        
                except asyncio.TimeoutError:
                    # Normal timeout, continue loop
                    continue
                    
                except Exception as e:
                    logger.error("Error in message subscriber", error=str(e))
                    await asyncio.sleep(1)  # Brief pause before retry
                    
        except Exception as e:
            logger.error("Message subscriber crashed", error=str(e))
        finally:
            logger.info("👋 Message subscriber stopped")
    
    async def _handle_message(self, redis_message):
        """Handle incoming message"""
        try:
            # Deserialize message
            message_data = json.loads(redis_message["data"])
            
            message = Message(
                topic=message_data["topic"],
                payload=message_data["payload"],
                timestamp=datetime.fromisoformat(message_data["timestamp"]),
                message_id=message_data["message_id"],
                headers=message_data.get("headers", {})
            )
            
            # Get handlers for topic
            topic = redis_message["channel"].decode("utf-8")
            handlers = self.handlers.get(topic, [])
            
            # Execute handlers concurrently
            if handlers:
                tasks = []
                for handler in handlers:
                    task = asyncio.create_task(
                        self._execute_handler(handler, message)
                    )
                    tasks.append(task)
                
                await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error("Error handling message", 
                        channel=redis_message.get("channel"), error=str(e))
    
    async def _execute_handler(self, handler: MessageHandler, message: Message):
        """Execute message handler with error handling"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(message)
            else:
                handler(message)
                
            logger.debug("✅ Message handler executed", 
                        handler=handler.__name__, topic=message.topic)
            
        except Exception as e:
            logger.error("❌ Message handler failed", 
                        handler=handler.__name__, topic=message.topic, error=str(e))
            
            # Send to dead letter queue
            await self._send_to_dlq(message, handler.__name__, str(e))
    
    async def _send_to_dlq(self, message: Message, handler_name: str, error: str):
        """Send failed message to dead letter queue"""
        try:
            dlq_data = {
                "original_message": {
                    "topic": message.topic,
                    "payload": message.payload,
                    "timestamp": message.timestamp.isoformat(),
                    "message_id": message.message_id,
                    "headers": message.headers
                },
                "failure_info": {
                    "handler": handler_name,
                    "error": error,
                    "failed_at": datetime.utcnow().isoformat()
                }
            }
            
            await self.client.xadd("dlq:failed_messages", dlq_data)
            
            logger.warning("📮 Message sent to DLQ", 
                          message_id=message.message_id, handler=handler_name)
            
        except Exception as e:
            logger.error("Failed to send message to DLQ", error=str(e))
    
    async def health_check(self) -> Dict[str, Any]:
        """Check message broker health"""
        try:
            if not self._initialized:
                return {"healthy": False, "error": "Message broker not initialized"}
            
            # Test Redis connection
            start_time = asyncio.get_event_loop().time()
            await self.client.ping()
            response_time = asyncio.get_event_loop().time() - start_time
            
            # Get broker stats
            info = await self.client.info()
            
            return {
                "healthy": True,
                "response_time": response_time,
                "subscriber_running": self._running and self._subscriber_task and not self._subscriber_task.done(),
                "subscribed_topics": list(self.handlers.keys()),
                "total_handlers": sum(len(handlers) for handlers in self.handlers.values()),
                "redis_info": {
                    "connected_clients": info.get("connected_clients"),
                    "used_memory": info.get("used_memory_human"),
                    "total_commands_processed": info.get("total_commands_processed")
                }
            }
            
        except Exception as e:
            return {"healthy": False, "error": str(e)}
    
    async def close(self):
        """Close message broker"""
        logger.info("🔒 Closing message broker...")
        
        try:
            await self.stop()
            
            if self.pubsub:
                await self.pubsub.close()
            
            if self.client:
                await self.client.close()
            
            self._initialized = False
            logger.info("✅ Message broker closed")
            
        except Exception as e:
            logger.error("❌ Error closing message broker", error=str(e))
    
    def _mask_url(self) -> str:
        """Mask sensitive information in URL"""
        if "@" in self.broker_url:
            parts = self.broker_url.split("@")
            if ":" in parts[0]:
                scheme_auth = parts[0].split(":")
                if len(scheme_auth) >= 3:
                    masked_auth = ":".join(scheme_auth[:-1]) + ":***"
                    return masked_auth + "@" + parts[1]
        return self.broker_url 