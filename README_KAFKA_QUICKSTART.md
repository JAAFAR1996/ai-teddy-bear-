# 🚀 AI Teddy Bear Kafka Event Streaming - Quick Start

## 📋 Prerequisites

- Docker and Docker Compose installed
- Python 3.9+ with required dependencies
- 8GB+ RAM available for Kafka cluster

## ⚡ Quick Start (5 minutes)

### 1. Start Kafka Infrastructure

**Windows:**
```powershell
# Start all services
docker-compose -f docker-compose.kafka.yml up -d

# Check status
docker-compose -f docker-compose.kafka.yml ps
```

**Linux/Mac:**
```bash
# Make script executable
chmod +x scripts/start_kafka_services.sh

# Start all services
./scripts/start_kafka_services.sh

# Start with test event
./scripts/start_kafka_services.sh --test
```

### 2. Verify Services

Wait 2-3 minutes for services to start, then check:

- **Kafka Broker**: `localhost:9092`
- **Control Center**: http://localhost:9021
- **Schema Registry**: http://localhost:8081
- **Kafka Connect**: http://localhost:8083

### 3. Run Complete Example

```bash
# Install dependencies
pip install kafka-python asyncio

# Run comprehensive example
python scripts/kafka_example_usage.py
```

## 🎯 What You'll See

The example demonstrates:

✅ **Child Registration** with automatic event publishing  
✅ **Conversation Lifecycle** with emotion detection  
✅ **Safety Violation Handling** with immediate escalation  
✅ **Voice Profile Optimization** based on usage patterns  
✅ **Real-time Analytics** and metrics collection  
✅ **Event Processing** with multiple handlers  

## 📊 Monitoring

### Control Center (Recommended)
- Open http://localhost:9021
- View topics, messages, and performance metrics
- Monitor consumer lag and throughput

### Command Line Tools
```bash
# List topics
docker exec teddy-kafka kafka-topics --list --bootstrap-server localhost:9092

# View messages
docker exec teddy-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic child.registered \
  --from-beginning

# Check consumer groups
docker exec teddy-kafka kafka-consumer-groups \
  --bootstrap-server localhost:9092 \
  --list
```

## 🛑 Stop Services

```bash
# Stop all services
docker-compose -f docker-compose.kafka.yml down

# Remove volumes (clean slate)
docker-compose -f docker-compose.kafka.yml down --volumes
```

## 🔧 Troubleshooting

### Services won't start
- Ensure Docker has enough memory (8GB+)
- Check port conflicts (9092, 8081, 9021)
- Wait longer - first startup takes 3-5 minutes

### Can't connect to Kafka
```bash
# Test connectivity
telnet localhost 9092

# Check service logs
docker-compose -f docker-compose.kafka.yml logs kafka
```

### Topics not created
```bash
# Manual topic creation
docker exec teddy-kafka kafka-topics \
  --create --bootstrap-server localhost:9092 \
  --topic test-topic --partitions 3 --replication-factor 1
```

## 📚 Next Steps

1. **Read the Complete Guide**: `docs/KAFKA_EVENT_STREAMING_GUIDE.md`
2. **Explore Event Handlers**: `src/infrastructure/messaging/event_handlers.py`
3. **Customize Configuration**: `src/infrastructure/messaging/kafka_config.py`
4. **Integrate with Your Code**: Use `EventDispatchContext` for automatic event publishing

## 🎉 Success!

If you see "🎉 Complete Kafka Event Streaming Example Finished!" then everything is working perfectly!

---

**Backend Team Implementation**  
**Apache Kafka Event Streaming for AI Teddy Bear** 