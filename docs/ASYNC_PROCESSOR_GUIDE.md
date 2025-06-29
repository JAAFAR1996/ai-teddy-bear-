# 🚀 Advanced Async Processor Guide
## AI Teddy Bear Project - High-Performance Asynchronous Processing

### 📖 Overview

The **AdvancedAsyncProcessor** is a comprehensive asynchronous processing system designed for the AI Teddy Bear project. It provides high-performance, non-blocking task execution with advanced features like:

- **Priority-based task queuing**
- **Task dependencies and cancellation**
- **Multiple execution contexts** (async, thread pool, process pool)
- **Performance monitoring and metrics**
- **Resource-aware scheduling**
- **Graceful shutdown and recovery**

---

## 🏗️ Architecture

### Core Components

1. **AdvancedAsyncProcessor**: Main processor with worker management
2. **TaskManager**: Handles task dependencies and lifecycle
3. **PerformanceMonitor**: Collects metrics and performance data
4. **ProcessingTask**: Enhanced task with metadata and dependencies
5. **TaskResult**: Comprehensive result with execution metrics

### Processing Types

```python
class ProcessingType(Enum):
    AUDIO_TRANSCRIPTION = "audio_transcription"    # Whisper/STT
    AUDIO_ENHANCEMENT = "audio_enhancement"        # Noise reduction
    AI_RESPONSE = "ai_response"                    # OpenAI/Anthropic
    EMOTION_ANALYSIS = "emotion_analysis"          # HUME AI
    IMAGE_GENERATION = "image_generation"          # DALL-E/Stable Diffusion
    IMAGE_PROCESSING = "image_processing"          # PIL/OpenCV
    TEXT_ANALYSIS = "text_analysis"                # NLP/Sentiment
    DATA_ANALYTICS = "data_analytics"              # Analytics/Insights
    DATABASE_OPERATION = "database_operation"      # DB queries
    NOTIFICATION = "notification"                  # Email/SMS/Push
    CUSTOM = "custom"                             # Custom processors
```

### Priority Levels

```python
class TaskPriority(Enum):
    CRITICAL = 1      # System-critical tasks
    HIGH = 2          # High priority (user interactions)
    NORMAL = 3        # Normal priority (background processing)
    LOW = 4           # Low priority (analytics, cleanup)
    BATCH = 5         # Batch processing
```

---

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from src.infrastructure.processing.async_processor import (
    create_processor, create_task, ProcessingType, TaskPriority
)

async def main():
    # Create and start processor
    processor = await create_processor(
        max_workers=5,
        enable_monitoring=True
    )
    
    try:
        # Create a task
        task = create_task(
            ProcessingType.AI_RESPONSE,
            {'prompt': 'Hello, how are you?', 'model': 'gpt-3.5-turbo'},
            TaskPriority.HIGH
        )
        
        # Submit and wait for result
        task_id = await processor.submit_task(task)
        result = await processor.wait_for_task(task_id, timeout=30.0)
        
        print(f"Result: {result.result}")
        
    finally:
        await processor.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
```

### Task Dependencies

```python
async def dependency_example():
    processor = await create_processor(max_workers=3)
    
    try:
        # Create dependent tasks
        task1 = create_task(
            ProcessingType.AUDIO_TRANSCRIPTION,
            {'audio_data': audio_bytes},
            TaskPriority.HIGH
        )
        
        task2 = create_task(
            ProcessingType.EMOTION_ANALYSIS,
            {'audio_data': audio_bytes},
            TaskPriority.HIGH,
            depends_on=[task1.id]  # Depends on task1
        )
        
        task3 = create_task(
            ProcessingType.AI_RESPONSE,
            {'prompt': 'Generate response based on emotion'},
            TaskPriority.NORMAL,
            depends_on=[task1.id, task2.id]  # Depends on both
        )
        
        # Submit all tasks
        await processor.submit_task(task1)
        await processor.submit_task(task2)
        await processor.submit_task(task3)
        
        # Wait for final result
        final_result = await processor.wait_for_task(task3.id)
        
    finally:
        await processor.shutdown()
```

---

## 🔧 Advanced Configuration

### Processor Configuration

```python
processor = AdvancedAsyncProcessor(
    max_workers=10,              # Total async workers
    max_thread_workers=5,        # Thread pool size
    max_process_workers=2,       # Process pool size
    queue_size=1000,            # Max queue size
    enable_monitoring=True,      # Performance monitoring
    enable_profiling=False       # Detailed profiling
)
```

### Task Configuration

```python
task = ProcessingTask(
    task_type=ProcessingType.AUDIO_ENHANCEMENT,
    payload={'audio_data': data, 'sample_rate': 44100},
    priority=TaskPriority.HIGH,
    timeout=30.0,               # Task timeout
    max_retries=3,              # Retry attempts
    cpu_intensive=True,         # Use process pool
    memory_intensive=False,     # Memory usage hint
    io_bound=False,            # I/O bound hint
    tags={'user_session', 'audio'},  # Tags for tracking
    depends_on=['parent_task_id']    # Dependencies
)
```

---

## 📊 Performance Monitoring

### Real-time Metrics

```python
async def monitor_performance():
    metrics = await processor.get_performance_metrics()
    
    print(f"Tasks processed: {metrics['tasks_processed']}")
    print(f"Success rate: {metrics['success_rate']:.1f}%")
    print(f"Average execution time: {metrics['average_execution_time']:.3f}s")
    print(f"Current throughput: {metrics['current_throughput']:.1f} tasks/sec")
    print(f"Queue size: {metrics['queue_size']}")
    print(f"Running tasks: {metrics['running_tasks']}")
    
    # Worker statistics
    for worker_id, stats in metrics['worker_stats'].items():
        print(f"{worker_id}: {stats['tasks_processed']} tasks, "
              f"{stats['status']}")
```

### Performance Optimization

```python
# For CPU-intensive tasks
task = create_task(
    ProcessingType.AUDIO_ENHANCEMENT,
    payload,
    cpu_intensive=True  # Will use process pool
)

# For I/O bound tasks
task = create_task(
    ProcessingType.DATABASE_OPERATION,
    payload,
    io_bound=True  # Will use thread pool
)

# For memory-intensive tasks
task = create_task(
    ProcessingType.IMAGE_PROCESSING,
    payload,
    memory_intensive=True  # Special handling
)
```

---

## 🎯 Specific Processors

### Audio Processing

```python
# Audio transcription
transcription_task = create_task(
    ProcessingType.AUDIO_TRANSCRIPTION,
    {
        'audio_data': audio_bytes,
        'sample_rate': 44100,
        'language': 'en'
    },
    TaskPriority.HIGH,
    timeout=30.0
)

# Audio enhancement
enhancement_task = create_task(
    ProcessingType.AUDIO_ENHANCEMENT,
    {
        'audio_data': audio_bytes,
        'sample_rate': 44100,
        'noise_reduction': True,
        'normalization': True
    },
    cpu_intensive=True
)
```

### AI Response Generation

```python
ai_task = create_task(
    ProcessingType.AI_RESPONSE,
    {
        'prompt': 'Child said: "I am happy today!"',
        'context': {
            'child_age': 5,
            'emotion': 'happy',
            'session_id': 'session_123'
        },
        'model': 'gpt-3.5-turbo',
        'max_tokens': 150
    },
    TaskPriority.HIGH,
    timeout=10.0
)
```

### Emotion Analysis

```python
emotion_task = create_task(
    ProcessingType.EMOTION_ANALYSIS,
    {
        'audio_data': audio_bytes,
        'text': 'I am happy today!',
        'analysis_type': 'comprehensive'
    },
    TaskPriority.HIGH
)
```

---

## 🛠️ Custom Processors

### Registering Custom Processors

```python
async def custom_nlp_processor(task: ProcessingTask):
    """Custom NLP processing"""
    text = task.payload.get('text')
    
    # Your custom processing logic here
    result = {
        'processed_text': text.upper(),
        'word_count': len(text.split()),
        'custom_metric': 42
    }
    
    return result

# Register the custom processor
processor.register_processor(
    ProcessingType.TEXT_ANALYSIS,
    custom_nlp_processor
)
```

### Using Custom Processors

```python
task = create_task(
    ProcessingType.CUSTOM,
    {
        'processor': lambda payload: {'custom_result': payload['input'] * 2},
        'input': 21
    }
)
```

---

## 🔄 Task Lifecycle Management

### Task States

```python
class TaskStatus(Enum):
    PENDING = "pending"      # Waiting to start
    RUNNING = "running"      # Currently executing
    COMPLETED = "completed"  # Successfully finished
    FAILED = "failed"        # Failed with error
    CANCELLED = "cancelled"  # Cancelled by user
    TIMEOUT = "timeout"      # Exceeded timeout
```

### Cancellation

```python
# Cancel a specific task
await processor.cancel_task(task_id)

# Cancel task with dependents (cascading)
cancelled = await processor.cancel_task(parent_task_id)
print(f"Cancelled: {cancelled}")
```

### Status Monitoring

```python
# Check task status
status = await processor.get_task_status(task_id)
print(f"Task status: {status.value}")

# Get detailed result
result = await processor.get_task_result(task_id)
if result:
    print(f"Status: {result.status.value}")
    print(f"Execution time: {result.execution_time:.3f}s")
    if result.error:
        print(f"Error: {result.error}")
```

---

## 🚦 Error Handling

### Retry Logic

```python
task = create_task(
    ProcessingType.AI_RESPONSE,
    payload,
    max_retries=3,  # Will retry up to 3 times
    timeout=10.0
)
```

### Error Handling Patterns

```python
try:
    result = await processor.wait_for_task(task_id, timeout=30.0)
    
    if result.status == TaskStatus.COMPLETED:
        print("Success:", result.result)
    elif result.status == TaskStatus.FAILED:
        print("Failed:", result.error)
    elif result.status == TaskStatus.TIMEOUT:
        print("Timed out")
    elif result.status == TaskStatus.CANCELLED:
        print("Cancelled")
        
except asyncio.TimeoutError:
    print("Wait timeout exceeded")
    await processor.cancel_task(task_id)
```

---

## 📈 Performance Tips

### 1. **Resource-Aware Task Submission**

```python
# CPU-intensive tasks
audio_task = create_task(
    ProcessingType.AUDIO_ENHANCEMENT,
    payload,
    cpu_intensive=True,  # Uses process pool
    priority=TaskPriority.HIGH
)

# I/O bound tasks
db_task = create_task(
    ProcessingType.DATABASE_OPERATION,
    payload,
    io_bound=True,  # Uses thread pool
    priority=TaskPriority.LOW
)
```

### 2. **Batch Processing**

```python
# Submit multiple tasks together
tasks = []
for data in batch_data:
    task = create_task(ProcessingType.TEXT_ANALYSIS, data, TaskPriority.BATCH)
    tasks.append(await processor.submit_task(task))

# Wait for all
results = []
for task_id in tasks:
    result = await processor.wait_for_task(task_id)
    results.append(result)
```

### 3. **Dependency Optimization**

```python
# Parallel independent tasks
task1 = create_task(ProcessingType.AUDIO_TRANSCRIPTION, data1)
task2 = create_task(ProcessingType.EMOTION_ANALYSIS, data2)

# Dependent task
task3 = create_task(
    ProcessingType.AI_RESPONSE,
    data3,
    depends_on=[task1.id, task2.id]
)
```

---

## 🔍 Debugging and Logging

### Enable Detailed Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create processor with debug info
processor = AdvancedAsyncProcessor(
    enable_monitoring=True,
    enable_profiling=True  # Detailed profiling
)
```

### Task Debugging

```python
# Add debug tags
task = create_task(
    ProcessingType.AI_RESPONSE,
    payload,
    tags={'debug', 'user_session_123', 'test_case'}
)

# Convert task to dict for inspection
task_dict = task.to_dict()
print(json.dumps(task_dict, indent=2))
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run specific test
python -m pytest test_async_processor.py::TestAdvancedAsyncProcessor::test_submit_and_process_task -v

# Run performance tests
python -m pytest test_async_processor.py::TestPerformance -v

# Run full test suite
python -m pytest test_async_processor.py -v
```

### Integration Testing

```python
async def test_full_workflow():
    processor = await create_processor(max_workers=3)
    
    try:
        # Test complete AI Teddy Bear workflow
        transcription_task = create_task(
            ProcessingType.AUDIO_TRANSCRIPTION,
            {'audio_data': test_audio}
        )
        
        emotion_task = create_task(
            ProcessingType.EMOTION_ANALYSIS,
            {'audio_data': test_audio},
            depends_on=[transcription_task.id]
        )
        
        ai_task = create_task(
            ProcessingType.AI_RESPONSE,
            {'prompt': 'Generate response'},
            depends_on=[transcription_task.id, emotion_task.id]
        )
        
        # Submit and verify
        await processor.submit_task(transcription_task)
        await processor.submit_task(emotion_task)
        await processor.submit_task(ai_task)
        
        result = await processor.wait_for_task(ai_task.id)
        assert result.status == TaskStatus.COMPLETED
        
    finally:
        await processor.shutdown()
```

---

## 🚀 Production Deployment

### Configuration for Production

```python
# Production configuration
processor = AdvancedAsyncProcessor(
    max_workers=20,              # Scale based on CPU cores
    max_thread_workers=10,       # I/O bound tasks
    max_process_workers=4,       # CPU intensive tasks
    queue_size=5000,            # Large queue for burst traffic
    enable_monitoring=True,      # Always monitor in production
    enable_profiling=False       # Disable profiling for performance
)
```

### Health Checks

```python
async def health_check():
    """Health check for monitoring systems"""
    metrics = await processor.get_performance_metrics()
    
    # Check if processor is healthy
    if not processor._running:
        return {"status": "unhealthy", "reason": "processor_stopped"}
    
    if metrics['queue_size'] > 1000:
        return {"status": "degraded", "reason": "high_queue_size"}
    
    if metrics['success_rate'] < 95.0:
        return {"status": "degraded", "reason": "low_success_rate"}
    
    return {"status": "healthy", "metrics": metrics}
```

### Graceful Shutdown

```python
import signal
import asyncio

async def main():
    processor = await create_processor()
    
    def signal_handler(signum, frame):
        print(f"Received signal {signum}, shutting down...")
        asyncio.create_task(processor.shutdown())
    
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Main application loop
        while processor._running:
            await asyncio.sleep(1)
    finally:
        await processor.shutdown()
```

---

## 📚 API Reference

### AdvancedAsyncProcessor

**Methods:**
- `start()` - Start the processor
- `shutdown(timeout=30.0)` - Graceful shutdown
- `submit_task(task)` - Submit task for processing
- `cancel_task(task_id)` - Cancel a task
- `wait_for_task(task_id, timeout=None)` - Wait for completion
- `get_task_status(task_id)` - Get task status
- `get_task_result(task_id)` - Get task result
- `get_performance_metrics()` - Get performance data
- `register_processor(task_type, func)` - Register custom processor

### ProcessingTask

**Properties:**
- `id` - Unique task identifier
- `task_type` - ProcessingType enum
- `payload` - Task data dictionary
- `priority` - TaskPriority enum
- `timeout` - Maximum execution time
- `depends_on` - List of dependency task IDs
- `tags` - Set of tags for tracking
- `cpu_intensive` - CPU intensity hint
- `memory_intensive` - Memory usage hint
- `io_bound` - I/O bound hint

### TaskResult

**Properties:**
- `task_id` - Task identifier
- `status` - TaskStatus enum
- `result` - Processing result
- `error` - Error message if failed
- `execution_time` - Time taken to execute
- `created_at` - Creation timestamp
- `completed_at` - Completion timestamp

---

## 🆘 Troubleshooting

### Common Issues

1. **Tasks not processing**
   ```python
   # Check if processor is running
   if not processor._running:
       await processor.start()
   ```

2. **High memory usage**
   ```python
   # Monitor memory usage
   metrics = await processor.get_performance_metrics()
   print(f"Peak memory: {metrics['peak_memory_usage_mb']} MB")
   ```

3. **Slow performance**
   ```python
   # Check worker utilization
   for worker_id, stats in metrics['worker_stats'].items():
       utilization = stats['total_execution_time'] / metrics['uptime_seconds']
       print(f"{worker_id}: {utilization:.1%} utilization")
   ```

4. **Task dependencies not working**
   ```python
   # Verify dependency setup
   ready_tasks = await processor.task_manager.get_ready_tasks()
   print(f"Ready tasks: {ready_tasks}")
   ```

---

## 🔧 Integration Examples

### Integration with AI Teddy Bear System

```python
# In production_teddy_system.py
from src.infrastructure.processing.async_processor import create_processor, create_task

class TeddyBearSystem:
    def __init__(self):
        self.processor = None
    
    async def start_system(self):
        self.processor = await create_processor(
            max_workers=8,
            enable_monitoring=True
        )
    
    async def process_child_interaction(self, audio_data, child_id):
        """Process complete child interaction"""
        
        # 1. Transcribe audio
        transcription_task = create_task(
            ProcessingType.AUDIO_TRANSCRIPTION,
            {'audio_data': audio_data, 'child_id': child_id},
            TaskPriority.HIGH
        )
        
        # 2. Analyze emotion (parallel with transcription)
        emotion_task = create_task(
            ProcessingType.EMOTION_ANALYSIS,
            {'audio_data': audio_data, 'child_id': child_id},
            TaskPriority.HIGH
        )
        
        # 3. Generate AI response (depends on both)
        ai_task = create_task(
            ProcessingType.AI_RESPONSE,
            {
                'child_id': child_id,
                'prompt_template': 'child_interaction'
            },
            TaskPriority.HIGH,
            depends_on=[transcription_task.id, emotion_task.id]
        )
        
        # Submit all tasks
        await self.processor.submit_task(transcription_task)
        await self.processor.submit_task(emotion_task)
        await self.processor.submit_task(ai_task)
        
        # Wait for final response
        result = await self.processor.wait_for_task(ai_task.id, timeout=30.0)
        
        return result
```

---

## 🎯 Best Practices

1. **Always use timeouts** for external API calls
2. **Set appropriate priorities** based on user interaction urgency
3. **Use dependencies** to ensure correct execution order
4. **Monitor performance metrics** in production
5. **Handle errors gracefully** with retry logic
6. **Use resource hints** (cpu_intensive, io_bound) for optimal scheduling
7. **Implement health checks** for monitoring systems
8. **Use tags** for debugging and tracking
9. **Graceful shutdown** to prevent data loss
10. **Test thoroughly** with various load patterns

---

## 📞 Support

For issues or questions:
1. Check the test files for usage examples
2. Review the performance metrics for debugging
3. Enable debug logging for detailed information
4. Use the health check endpoint for monitoring

---

*This guide covers the complete Advanced Async Processor system for the AI Teddy Bear project. The system is designed for high performance, reliability, and scalability in production environments.* 