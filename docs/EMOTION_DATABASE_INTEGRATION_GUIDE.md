# 🧠💾 Emotion Database Integration Guide
## AI Teddy Bear Project - Advanced Emotion Analysis with Database Storage

### 📖 Overview

The **Emotion Database Integration System** provides comprehensive emotion analysis with intelligent database storage for the AI Teddy Bear project. This system automatically analyzes child emotions from text and audio inputs, stores results in a structured database, and generates detailed parental insights.

---

## 🏗️ Architecture

### Core Components

1. **DatabaseEmotionService**: Main database service for emotion storage and analytics
2. **EnhancedEmotionAnalyzer**: Enhanced analyzer with integrated database functionality  
3. **SimpleEmotionDatabase**: Lightweight SQLite implementation for basic storage
4. **Parental Report Generator**: Comprehensive reporting system
5. **Analytics Engine**: Advanced emotion trend analysis

### Database Schema

```sql
-- Children table
CREATE TABLE children (
    id TEXT PRIMARY KEY,
    name TEXT,
    age INTEGER,
    device_id TEXT,
    total_interactions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP
);

-- Conversations table  
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    child_id TEXT,
    session_id TEXT,
    total_messages INTEGER DEFAULT 0,
    last_emotion TEXT,
    context_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages table
CREATE TABLE messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT,
    sender TEXT,
    content TEXT,
    message_type TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Emotional states table
CREATE TABLE emotional_states (
    id TEXT PRIMARY KEY,
    child_id TEXT,
    conversation_id TEXT,
    message_id TEXT,
    primary_emotion TEXT,
    confidence_score REAL,
    all_emotions TEXT,
    source TEXT,
    behavioral_indicators TEXT,
    recommendations TEXT,
    context_data TEXT,
    audio_features TEXT,
    analysis_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_id TEXT
);
```

---

## 🚀 Quick Start

### Basic Setup

```python
import asyncio
from src.domain.services.advanced_emotion_analyzer import (
    DatabaseEmotionService,
    analyze_and_save_emotion
)

# Initialize database service
db_service = DatabaseEmotionService(
    database_url="sqlite:///teddy_emotions.db",
    enable_analytics=True,
    retention_days=365
)
```

### Simple Usage with Convenience Function

```python
async def quick_example():
    # Analyze and save emotion in one call
    emotion_result, record_id = await analyze_and_save_emotion(
        text_input="I'm so happy today! I love my teddy bear!",
        child_id="child_123",
        session_id="session_456", 
        device_id="device_789",
        context={"activity": "playing", "time_of_day": "afternoon"}
    )
    
    print(f"Emotion: {emotion_result.primary_emotion}")
    print(f"Confidence: {emotion_result.confidence:.2f}")
    print(f"Database record: {record_id}")

# Run example
asyncio.run(quick_example())
```

---

## 🔧 Core Functionality

### 1. Emotion Analysis and Storage

```python
async def analyze_and_store_example():
    db_service = DatabaseEmotionService("sqlite:///emotions.db")
    
    # Analyze text input
    emotion_result, record_id = await db_service.analyze_and_save_emotion(
        text_input="I feel curious about how airplanes fly!",
        child_id="child_001",
        session_id="learning_session_001",
        device_id="teddy_device_001",
        context={
            "activity": "learning",
            "topic": "science",
            "time_of_day": "morning",
            "child_age": 6
        }
    )
    
    print(f"✅ Stored emotion: {emotion_result.primary_emotion}")
    return record_id
```

### 2. Audio Processing Integration

```python
async def analyze_audio_example():
    # With audio data (bytes)
    audio_data = load_audio_file("child_voice.wav")  # Your audio loading function
    
    emotion_result, record_id = await db_service.analyze_and_save_emotion(
        audio_file=audio_data,
        text_input="Why do flowers smell so good?",  # Optional transcription
        child_id="child_002",
        session_id="garden_exploration_001",
        device_id="teddy_device_002",
        context={
            "location": "garden",
            "activity": "exploration",
            "audio_quality": "clear"
        }
    )
    
    print(f"Audio emotion: {emotion_result.primary_emotion}")
    print(f"Confidence: {emotion_result.confidence:.2f}")
```

### 3. Emotion History Retrieval

```python
async def get_emotion_history_example():
    # Get last 24 hours of emotions
    history = await db_service.get_emotion_history(
        child_id="child_001",
        hours=24,
        limit=50,
        emotion_filter="happy"  # Optional filter
    )
    
    print(f"Found {len(history)} emotion records")
    
    for emotion in history[:5]:  # Show recent 5
        print(f"- {emotion.primary_emotion} "
              f"(confidence: {emotion.confidence:.2f}) "
              f"at {emotion.timestamp}")
```

### 4. Comprehensive Analytics

```python
async def get_analytics_example():
    # Get 7-day analytics
    analytics = await db_service.get_emotion_analytics(
        child_id="child_001",
        days=7
    )
    
    print("📊 Emotion Analytics:")
    print(f"Total interactions: {analytics['total_interactions']}")
    print(f"Most common emotion: {analytics['most_common_emotion']['emotion']}")
    print(f"Average confidence: {analytics['average_confidence']:.2f}")
    
    # Emotion distribution
    print("\nEmotion Distribution:")
    for emotion, percentage in analytics['emotion_distribution'].items():
        print(f"  {emotion}: {percentage:.1f}%")
    
    # Risk indicators
    if analytics['risk_indicators']:
        print("\n⚠️ Risk Indicators:")
        for indicator in analytics['risk_indicators']:
            print(f"  - {indicator}")
    
    # Recommendations
    print("\n💡 Recommendations:")
    for rec in analytics['recommendations']:
        print(f"  - {rec}")
```

---

## 📋 Parental Reporting

### Generate Comprehensive Reports

```python
async def generate_parental_report_example():
    # Generate weekly report
    report = await db_service.generate_parental_report(
        child_id="child_001",
        report_type="weekly",  # daily, weekly, monthly, quarterly
        include_recommendations=True
    )
    
    # Report structure
    header = report['report_header']
    print(f"📋 Report for {header['child_name']} (Age: {header['child_age']})")
    print(f"Period: {header['report_type']} ({header['period_days']} days)")
    
    # Emotion summary
    summary = report['emotion_summary']
    print(f"\n📊 Summary: {summary['total_interactions']} interactions")
    print(f"Most common emotion: {summary['most_common_emotion']['emotion']}")
    
    # Conversation insights
    conversations = report['conversation_insights']
    print(f"\n💬 Conversations: {conversations['total_conversations']}")
    print(f"Average messages per conversation: {conversations['avg_messages_per_conversation']}")
    
    # Recommendations for parents
    print("\n👨‍👩‍👧‍👦 Parental Recommendations:")
    for rec in report['parental_recommendations']:
        print(f"  - {rec}")
    
    # Action items
    print("\n✅ Action Items:")
    for action in report['action_items']:
        print(f"  - {action}")
```

### Real-time Emotion Monitoring

```python
async def real_time_monitoring_example():
    # Monitor child emotions in real-time
    child_id = "child_001"
    
    while True:
        # Get recent emotions (last hour)
        recent_emotions = await db_service.get_emotion_history(
            child_id=child_id,
            hours=1
        )
        
        if recent_emotions:
            latest_emotion = recent_emotions[0]
            
            # Check for concerning patterns
            if latest_emotion.primary_emotion in ['sad', 'angry', 'scared']:
                print(f"⚠️ Alert: Child showing {latest_emotion.primary_emotion} emotion")
                
                # Get context for intervention
                analytics = await db_service.get_emotion_analytics(child_id, days=1)
                
                if analytics['risk_indicators']:
                    print("🚨 Risk indicators detected:")
                    for indicator in analytics['risk_indicators']:
                        print(f"  - {indicator}")
        
        # Wait before next check
        await asyncio.sleep(300)  # Check every 5 minutes
```

---

## 📈 Advanced Analytics

### Emotion Trends Analysis

```python
async def analyze_emotion_trends():
    # Get detailed trends
    trends = await db_service.get_emotion_trends(
        child_id="child_001",
        days=30,
        granularity="daily"  # daily, weekly, monthly
    )
    
    print("📈 Emotion Trends (Last 30 days):")
    
    for date, data in trends['trends'].items():
        print(f"\n{date}:")
        print(f"  Total interactions: {data['total_interactions']}")
        print(f"  Average confidence: {data['avg_confidence']:.2f}")
        
        # Most common emotion for the day
        emotions = data['emotions']
        if emotions:
            top_emotion = max(emotions.items(), key=lambda x: x[1])
            print(f"  Top emotion: {top_emotion[0]} ({top_emotion[1]} times)")
```

### Behavioral Pattern Recognition

```python
async def analyze_behavioral_patterns():
    child_id = "child_001"
    
    # Get behavioral insights
    analytics = await db_service.get_emotion_analytics(child_id, days=14)
    
    # Analyze patterns
    emotion_counts = analytics['emotion_counts']
    total_interactions = analytics['total_interactions']
    
    # Calculate emotional stability
    emotion_variance = len(emotion_counts)
    dominant_emotion_ratio = max(emotion_counts.values()) / total_interactions
    
    print("🧠 Behavioral Analysis:")
    print(f"Emotional range: {emotion_variance} different emotions")
    print(f"Dominant emotion ratio: {dominant_emotion_ratio:.1%}")
    
    if dominant_emotion_ratio > 0.7:
        print("  → High emotional consistency")
    elif emotion_variance >= 5:
        print("  → Good emotional range and adaptability")
    else:
        print("  → Limited emotional expression range")
```

---

## 🔍 Enhanced Features

### Context-Aware Analysis

```python
async def context_aware_analysis():
    # Analyze emotions with rich context
    contexts = [
        {
            "text": "I love playing with blocks!",
            "context": {
                "activity": "building",
                "toy_type": "blocks", 
                "duration_minutes": 45,
                "social_setting": "alone",
                "time_of_day": "afternoon"
            }
        },
        {
            "text": "This puzzle is too hard!",
            "context": {
                "activity": "puzzle_solving",
                "difficulty": "challenging",
                "previous_attempts": 3,
                "assistance_needed": True,
                "frustration_level": "medium"
            }
        }
    ]
    
    for i, item in enumerate(contexts):
        emotion_result, record_id = await db_service.analyze_and_save_emotion(
            text_input=item["text"],
            child_id="child_context",
            session_id=f"context_session_{i}",
            device_id="context_device",
            context=item["context"]
        )
        
        print(f"Text: {item['text']}")
        print(f"Emotion: {emotion_result.primary_emotion}")
        print(f"Context-aware confidence: {emotion_result.confidence:.2f}")
        print(f"Behavioral indicators: {emotion_result.behavioral_indicators}")
        print()
```

### Multi-Child Family Analysis

```python
async def family_analysis_example():
    # Analyze multiple children in a family
    children = ["child_001", "child_002", "child_003"]
    
    family_report = {}
    
    for child_id in children:
        analytics = await db_service.get_emotion_analytics(child_id, days=7)
        
        family_report[child_id] = {
            "total_interactions": analytics.get('total_interactions', 0),
            "dominant_emotion": analytics.get('most_common_emotion', {}).get('emotion', 'unknown'),
            "average_confidence": analytics.get('average_confidence', 0),
            "risk_indicators": analytics.get('risk_indicators', [])
        }
    
    print("👨‍👩‍👧‍👦 Family Emotional Overview:")
    
    for child_id, data in family_report.items():
        print(f"\n{child_id}:")
        print(f"  Interactions: {data['total_interactions']}")
        print(f"  Dominant emotion: {data['dominant_emotion']}")
        print(f"  Average confidence: {data['average_confidence']:.2f}")
        
        if data['risk_indicators']:
            print(f"  ⚠️ Risk indicators: {len(data['risk_indicators'])}")
```

---

## 🛠️ Production Configuration

### Database Setup for Production

```python
# PostgreSQL configuration for production
DATABASE_CONFIG = {
    "production": {
        "database_url": "postgresql://user:password@localhost:5432/teddy_emotions",
        "pool_size": 20,
        "max_overflow": 30,
        "pool_recycle": 3600,
        "echo": False  # Set to True for SQL debugging
    },
    "staging": {
        "database_url": "postgresql://user:password@staging:5432/teddy_emotions_staging",
        "pool_size": 10,
        "max_overflow": 15,
        "pool_recycle": 1800,
        "echo": False
    },
    "development": {
        "database_url": "sqlite:///teddy_emotions_dev.db",
        "echo": True  # Enable SQL logging in development
    }
}

# Initialize service for production
db_service = DatabaseEmotionService(
    database_url=DATABASE_CONFIG["production"]["database_url"],
    enable_analytics=True,
    retention_days=730  # 2 years retention for production
)
```

### Performance Optimization

```python
# Performance optimization settings
class OptimizedEmotionService:
    def __init__(self):
        self.db_service = DatabaseEmotionService(
            database_url="postgresql://...",
            enable_analytics=True,
            retention_days=365
        )
        
        # Enable connection pooling
        self.db_service.engine = create_engine(
            "postgresql://...",
            pool_size=20,
            max_overflow=30,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    async def batch_process_emotions(self, emotion_batch):
        """Process multiple emotions efficiently"""
        results = []
        
        # Process in batches for better performance
        batch_size = 10
        for i in range(0, len(emotion_batch), batch_size):
            batch = emotion_batch[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [
                self.db_service.analyze_and_save_emotion(**emotion_data)
                for emotion_data in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            results.extend(batch_results)
        
        return results
```

---

## 📊 Monitoring and Alerting

### Health Monitoring

```python
async def health_check():
    """System health check for monitoring"""
    try:
        # Test database connection
        test_child = "health_check_child"
        
        # Quick emotion analysis test
        emotion_result, record_id = await db_service.analyze_and_save_emotion(
            text_input="Health check test",
            child_id=test_child,
            session_id="health_check_session",
            device_id="health_check_device"
        )
        
        # Test analytics generation
        analytics = await db_service.get_emotion_analytics(test_child, days=1)
        
        # Test cleanup (optional)
        await db_service.cleanup_old_data(days_to_keep=1)
        
        return {
            "status": "healthy",
            "database": "connected",
            "emotion_analysis": "functional",
            "analytics": "operational",
            "last_check": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.utcnow().isoformat()
        }

# Run health check
health_status = await health_check()
print(f"System health: {health_status['status']}")
```

### Automated Alerts

```python
class EmotionAlertSystem:
    def __init__(self, db_service):
        self.db_service = db_service
        self.alert_thresholds = {
            "high_negative_emotions": 0.4,  # 40% negative emotions
            "low_interaction_frequency": 0.2,  # Less than 20% of expected interactions
            "concerning_emotion_persistence": 3  # Same concerning emotion for 3+ hours
        }
    
    async def check_alerts(self, child_id: str):
        """Check for emotional alerts"""
        alerts = []
        
        # Get recent analytics
        analytics = await self.db_service.get_emotion_analytics(child_id, days=1)
        
        # Check negative emotion percentage
        negative_emotions = ['sad', 'angry', 'scared']
        negative_percentage = sum(
            analytics['emotion_distribution'].get(emotion, 0) 
            for emotion in negative_emotions
        ) / 100
        
        if negative_percentage > self.alert_thresholds["high_negative_emotions"]:
            alerts.append({
                "type": "high_negative_emotions",
                "severity": "high",
                "message": f"High negative emotions detected: {negative_percentage:.1%}",
                "recommendation": "Consider increased comfort and support activities"
            })
        
        # Check interaction frequency
        expected_daily_interactions = 10  # Expected interactions per day
        actual_interactions = analytics['total_interactions']
        
        if actual_interactions < expected_daily_interactions * self.alert_thresholds["low_interaction_frequency"]:
            alerts.append({
                "type": "low_interaction",
                "severity": "medium", 
                "message": f"Low interaction frequency: {actual_interactions} interactions today",
                "recommendation": "Encourage more interaction with the teddy bear"
            })
        
        return alerts
    
    async def send_parent_notification(self, child_id: str, alerts: List[Dict]):
        """Send notifications to parents"""
        if not alerts:
            return
        
        # Prepare notification
        notification = {
            "child_id": child_id,
            "alert_count": len(alerts),
            "alerts": alerts,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        # Send notification (implement your notification service)
        print(f"🚨 Parent Alert for {child_id}:")
        for alert in alerts:
            print(f"  - {alert['message']}")
            print(f"    Recommendation: {alert['recommendation']}")
```

---

## 🔒 Data Privacy and Security

### Data Encryption

```python
from cryptography.fernet import Fernet

class SecureEmotionService:
    def __init__(self, encryption_key: bytes):
        self.cipher = Fernet(encryption_key)
        self.db_service = DatabaseEmotionService("sqlite:///secure_emotions.db")
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data before storage"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt data for processing"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    async def secure_analyze_and_save(self, text_input: str, **kwargs):
        """Analyze and save with encryption"""
        # Encrypt sensitive text
        encrypted_text = self.encrypt_sensitive_data(text_input)
        
        # Store with encryption marker
        kwargs['context'] = kwargs.get('context', {})
        kwargs['context']['encrypted'] = True
        
        return await self.db_service.analyze_and_save_emotion(
            text_input=encrypted_text,
            **kwargs
        )
```

### Data Retention and Cleanup

```python
async def setup_data_retention_policy():
    """Setup automated data cleanup"""
    
    # Define retention policies
    retention_policies = {
        "emotional_states": 365,  # Keep emotion data for 1 year
        "conversations": 730,     # Keep conversations for 2 years  
        "messages": 365,         # Keep messages for 1 year
        "analytics_cache": 30    # Keep cached analytics for 30 days
    }
    
    # Schedule cleanup task
    async def cleanup_task():
        while True:
            try:
                # Run cleanup
                deleted_count = await db_service.cleanup_old_data(
                    days_to_keep=retention_policies["emotional_states"]
                )
                
                print(f"✅ Cleaned up {deleted_count} old emotion records")
                
                # Wait 24 hours before next cleanup
                await asyncio.sleep(86400)
                
            except Exception as e:
                print(f"❌ Cleanup error: {e}")
                await asyncio.sleep(3600)  # Retry in 1 hour
    
    # Start cleanup task
    asyncio.create_task(cleanup_task())
```

---

## 📋 Testing and Validation

### Unit Testing

```python
import pytest
import tempfile

class TestEmotionDatabaseIntegration:
    
    @pytest.fixture
    async def db_service(self):
        """Test database fixture"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_url = f"sqlite:///{tmp.name}"
        
        service = DatabaseEmotionService(db_url)
        yield service
        
        # Cleanup
        os.unlink(tmp.name)
    
    @pytest.mark.asyncio
    async def test_emotion_storage(self, db_service):
        """Test basic emotion storage"""
        emotion_result, record_id = await db_service.analyze_and_save_emotion(
            text_input="I'm happy!",
            child_id="test_child",
            session_id="test_session",
            device_id="test_device"
        )
        
        assert emotion_result.primary_emotion in ['happy', 'calm', 'curious']
        assert 0.0 <= emotion_result.confidence <= 1.0
        assert record_id is not None
    
    @pytest.mark.asyncio
    async def test_emotion_analytics(self, db_service):
        """Test analytics generation"""
        # Add test data
        for i in range(5):
            await db_service.analyze_and_save_emotion(
                text_input=f"Test emotion {i}",
                child_id="analytics_child",
                session_id=f"session_{i}",
                device_id="test_device"
            )
        
        # Get analytics
        analytics = await db_service.get_emotion_analytics("analytics_child", days=1)
        
        assert analytics['total_interactions'] == 5
        assert 'emotion_distribution' in analytics
        assert 'most_common_emotion' in analytics
```

### Integration Testing

```python
async def run_integration_tests():
    """Comprehensive integration test suite"""
    
    print("🧪 Running Emotion Database Integration Tests")
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Happy Child Interaction",
            "inputs": [
                "I love my teddy bear!",
                "This is so much fun!",
                "I'm excited to play!"
            ],
            "expected_emotion": "happy"
        },
        {
            "name": "Curious Learning Session", 
            "inputs": [
                "Why is the sky blue?",
                "How do birds fly?",
                "What makes flowers grow?"
            ],
            "expected_emotion": "curious"
        },
        {
            "name": "Mixed Emotional Session",
            "inputs": [
                "I feel sad today",
                "But playing makes me happy",
                "I wonder why I felt sad"
            ],
            "expected_emotions": ["sad", "happy", "curious"]
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n🔍 Testing: {scenario['name']}")
        
        child_id = f"test_{scenario['name'].lower().replace(' ', '_')}"
        
        # Process all inputs
        for i, text in enumerate(scenario['inputs']):
            emotion_result, record_id = await db_service.analyze_and_save_emotion(
                text_input=text,
                child_id=child_id,
                session_id=f"{child_id}_session",
                device_id="integration_test_device",
                context={"test_scenario": scenario['name']}
            )
            
            print(f"  Input: {text}")
            print(f"  Emotion: {emotion_result.primary_emotion} "
                  f"(confidence: {emotion_result.confidence:.2f})")
        
        # Verify analytics
        analytics = await db_service.get_emotion_analytics(child_id, days=1)
        print(f"  Analytics: {analytics['total_interactions']} interactions")
        print(f"  Top emotion: {analytics['most_common_emotion']['emotion']}")
```

---

## 📚 Best Practices

### 1. **Optimal Performance**
- Use connection pooling for production databases
- Implement batch processing for high-volume scenarios
- Cache frequently accessed analytics
- Monitor database performance metrics

### 2. **Data Quality**
- Validate input data before processing
- Implement confidence thresholds for emotion detection
- Regular data quality audits
- Handle edge cases gracefully

### 3. **Privacy and Security**
- Encrypt sensitive data at rest and in transit
- Implement proper access controls
- Regular security audits
- Data anonymization for analytics

### 4. **Monitoring and Alerting**
- Set up health checks for system components
- Monitor emotion trend anomalies
- Alert on concerning emotional patterns
- Track system performance metrics

### 5. **Scalability**
- Design for horizontal scaling
- Use read replicas for analytics queries
- Implement proper indexing strategies
- Consider data partitioning for large datasets

---

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```python
   # Check database connectivity
   try:
       await db_service.analyze_and_save_emotion(
           text_input="Connection test",
           child_id="test_child",
           session_id="test_session",
           device_id="test_device"
       )
       print("✅ Database connection OK")
   except Exception as e:
       print(f"❌ Database error: {e}")
   ```

2. **Low Emotion Confidence**
   ```python
   # Implement confidence threshold checking
   if emotion_result.confidence < 0.5:
       print(f"⚠️ Low confidence emotion detection: {emotion_result.confidence:.2f}")
       # Consider requesting additional context or manual review
   ```

3. **Performance Issues**
   ```python
   # Monitor processing time
   import time
   
   start_time = time.time()
   emotion_result, record_id = await db_service.analyze_and_save_emotion(...)
   processing_time = time.time() - start_time
   
   if processing_time > 2.0:  # 2 second threshold
       print(f"⚠️ Slow processing detected: {processing_time:.2f}s")
   ```

### Performance Monitoring

```python
async def monitor_system_performance():
    """Monitor system performance metrics"""
    
    # Get database statistics
    with db_service.get_db_session() as session:
        # Check table sizes
        tables = ['children', 'conversations', 'messages', 'emotional_states']
        
        for table in tables:
            result = session.execute(f"SELECT COUNT(*) FROM {table}")
            count = result.scalar()
            print(f"{table}: {count:,} records")
        
        # Check recent activity
        result = session.execute("""
            SELECT COUNT(*) FROM emotional_states 
            WHERE analysis_timestamp > datetime('now', '-1 day')
        """)
        recent_emotions = result.scalar()
        print(f"Recent emotions (24h): {recent_emotions:,}")
    
    # Performance recommendations
    if recent_emotions > 1000:
        print("💡 Consider database optimization for high volume")
    
    if recent_emotions < 10:
        print("💡 Low activity detected - check system health")
```

---

## 🎯 Summary

The **Emotion Database Integration System** provides:

✅ **Comprehensive emotion analysis** with text and audio support  
✅ **Intelligent database storage** with SQLAlchemy integration  
✅ **Advanced analytics** and trend analysis  
✅ **Parental reporting** with actionable insights  
✅ **Real-time monitoring** and alerting  
✅ **Data privacy** and security features  
✅ **Scalable architecture** for production deployment  
✅ **Comprehensive testing** and validation tools  

This system enables the AI Teddy Bear to provide meaningful emotional insights to parents while maintaining child privacy and data security.

---

*This guide covers the complete Emotion Database Integration system for the AI Teddy Bear project. The system is designed for production use with enterprise-grade features and comprehensive monitoring capabilities.* 