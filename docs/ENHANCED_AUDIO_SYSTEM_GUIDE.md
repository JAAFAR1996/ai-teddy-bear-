# 🎵 Enhanced Audio System Guide
## دليل النظام الصوتي المتطور - مشروع AI Teddy Bear

---

## 📋 Table of Contents / جدول المحتويات

1. [Overview / نظرة عامة](#overview)
2. [Features / الميزات](#features)
3. [Installation / التثبيت](#installation)
4. [Quick Start / البداية السريعة](#quick-start)
5. [Audio Formats / تنسيقات الصوت](#audio-formats)
6. [Configuration / التكوين](#configuration)
7. [API Reference / مرجع البرمجة](#api-reference)
8. [Examples / أمثلة](#examples)
9. [Performance / الأداء](#performance)
10. [Troubleshooting / حل المشاكل](#troubleshooting)
11. [Advanced Features / الميزات المتقدمة](#advanced-features)

---

## 🌟 Overview

النظام الصوتي المتطور (Enhanced Audio System) هو نظام شامل لمعالجة الصوت مصمم خصيصاً لمشروع AI Teddy Bear. يوفر النظام دعماً كاملاً للتسجيل والتشغيل وتحويل النص إلى كلام مع دعم متعدد التنسيقات والتكامل السحابي.

### Key Capabilities:
- **Multi-format audio support**: WAV, MP3, OPUS, OGG, FLAC
- **Real-time audio processing**: Recording, playback, TTS
- **Session management**: Multi-child session handling
- **Cloud integration**: Automatic backup and sync
- **Performance monitoring**: Real-time stats and metrics
- **Modern architecture**: Async/await support, event-driven design

---

## ✨ Features

### 🎤 Audio Recording
- **High-quality recording** with configurable sample rates
- **Noise reduction** and audio enhancement
- **Voice activity detection** for automatic start/stop
- **Multiple quality modes**: Power save, Balanced, High quality, Adaptive

### 🔊 Audio Playback  
- **Multi-format playback** (WAV, MP3, OPUS, OGG, FLAC)
- **Audio effects**: Fade in/out, volume control, looping
- **Low-latency playback** for real-time interaction
- **Cross-platform support** (Windows, macOS, Linux)

### 🗣️ Text-to-Speech (TTS)
- **Multi-language support** with emotional context
- **Voice styles**: Friendly, excited, calm, gentle
- **Speed and volume control**
- **Caching system** for improved performance

### 💾 Audio Saving
- **Intelligent format detection** from file extensions
- **Quality-based compression** (0-10 scale)
- **Metadata embedding** for session tracking
- **Automatic cloud backup** (optional)

### 📊 Session Management
- **Multi-child sessions** with unique identifiers
- **Session types**: Conversation, Story telling, Learning, Play time
- **Performance tracking** per session
- **Automatic cleanup** and timeout handling

---

## 🚀 Installation

### Prerequisites
```bash
# Python 3.8+ required
python --version

# Install ffmpeg for full format support
# Windows: Download from https://ffmpeg.org/
# macOS: brew install ffmpeg  
# Linux: sudo apt-get install ffmpeg
```

### Basic Installation
```bash
# Clone the project
git clone <repository-url>
cd ai-teddy-bear

# Install dependencies
pip install -r requirements_enhanced_audio.txt

# Verify installation
python test_enhanced_audio_system.py quick
```

### Advanced Installation (with optional features)
```bash
# Install with cloud support
pip install boto3 google-cloud-storage azure-storage-blob

# Install with ML audio features
pip install torch torchaudio speechrecognition

# Install with MQTT IoT support
pip install asyncio-mqtt
```

---

## ⚡ Quick Start

### Basic Usage
```python
from src.audio.audio_manager import (
    EnhancedAudioManager,
    create_child_safe_config,
    AudioSessionType,
    AudioFormatType
)

# Create audio manager with child-safe settings
config = create_child_safe_config()
audio_manager = EnhancedAudioManager(config)

# Start a session
session_id = audio_manager.start_session(
    child_id="child_001",
    session_type=AudioSessionType.CONVERSATION
)

# Record audio
audio_data, metadata = audio_manager.record_audio(
    duration=5,
    session_id=session_id
)

# Play audio
audio_manager.play_audio(
    audio_data=audio_data,
    volume=0.7
)

# Text-to-speech
audio_manager.speak(
    text="مرحباً! كيف حالك اليوم؟",
    language="ar",
    session_id=session_id
)

# Save audio in multiple formats
audio_manager.save_audio(
    audio_data=audio_data,
    filename="recording.mp3",
    format=AudioFormatType.MP3,
    quality=8
)

# End session
audio_manager.end_session(session_id)
audio_manager.cleanup()
```

### Async Usage
```python
import asyncio
from src.audio.modern_audio_manager import ModernAudioManager

async def main():
    manager = ModernAudioManager(container)
    await manager.initialize()
    
    # Async operations
    session_id = await manager.start_session("child_001")
    
    audio_data = await manager.record_audio(
        duration=3,
        session_id=session_id
    )
    
    await manager.play_audio(
        audio_data=audio_data[0],
        session_id=session_id
    )
    
    await manager.cleanup()

asyncio.run(main())
```

---

## 🎵 Audio Formats

### Supported Formats

| Format | Extension | Compression | Quality | Use Case |
|--------|-----------|-------------|---------|----------|
| **WAV** | .wav | None | Lossless | High quality, editing |
| **MP3** | .mp3 | Lossy | Good | Universal compatibility |
| **OPUS** | .opus | Lossy | Excellent | Low latency, modern |
| **OGG** | .ogg | Lossy | Good | Open source |
| **FLAC** | .flac | Lossless | Perfect | Archival quality |

### Format Selection Guide

```python
# For real-time communication (low latency)
AudioFormatType.OPUS

# For maximum compatibility
AudioFormatType.MP3

# For highest quality
AudioFormatType.FLAC

# For simple applications
AudioFormatType.WAV
```

### Quality Settings
```python
# Quality scale: 0 (lowest) to 10 (highest)
QUALITY_PRESETS = {
    "phone": 2,      # Phone call quality
    "radio": 5,      # FM radio quality  
    "cd": 8,         # CD quality
    "studio": 10     # Studio quality
}
```

---

## ⚙️ Configuration

### Audio System Configuration
```python
from src.audio.audio_manager import AudioSystemConfig, AudioFormatType

config = AudioSystemConfig(
    # Recording settings
    default_record_duration=10,
    max_record_duration=60,
    sample_rate=44100,
    channels=2,
    
    # Quality settings
    noise_reduction_enabled=True,
    voice_activity_detection=True,
    compression_quality=7,
    
    # Output settings
    default_output_format=AudioFormatType.MP3,
    volume_level=0.8,
    
    # Session settings
    session_timeout_minutes=30,
    max_concurrent_sessions=3,
    
    # Cloud settings
    enable_cloud_sync=True,
    cloud_backup_enabled=True,
    
    # Safety settings
    child_safe_mode=True
)
```

### Predefined Configurations
```python
# Child-safe configuration (recommended for kids)
child_config = create_child_safe_config()

# High-quality configuration (for professional use)
hq_config = create_high_quality_config()

# Low-latency configuration (for real-time apps)
ll_config = create_low_latency_config()
```

---

## 📚 API Reference

### EnhancedAudioManager Class

#### Core Methods

```python
# Session Management
start_session(child_id: str, session_type: AudioSessionType, quality_mode: AudioQualityMode) -> str
end_session(session_id: str) -> bool
get_session_info(session_id: str) -> Optional[Dict[str, Any]]

# Audio Recording
record_audio(duration: int, process: bool, save: bool, filename: str, session_id: str, format: AudioFormatType) -> Tuple[np.ndarray, Dict]

# Audio Playback
play_audio(audio_data: np.ndarray, filename: str, volume: float, session_id: str, format_hint: AudioFormatType, loop: bool, fade_in: float, fade_out: float) -> bool

# Audio Saving
save_audio(audio_data: np.ndarray, filename: str, format: AudioFormatType, quality: int, metadata: Dict, session_id: str, cloud_sync: bool) -> bool

# Text-to-Speech
speak(text: str, language: str, speed: float, volume: float, cache: bool, session_id: str, voice_style: str) -> bool

# System Control
stop_all(session_id: str) -> None
cleanup() -> None
```

#### System Information
```python
# System stats and monitoring
get_system_stats() -> Dict[str, Any]
get_supported_formats() -> List[str]
get_format_info(format: AudioFormatType) -> Dict[str, Any]
test_audio_system() -> Dict[str, Any]
```

#### Event System
```python
# Event handling
add_event_listener(event_type: str, callback: Callable) -> None
remove_event_listener(event_type: str, callback: Callable) -> None

# Event types: "session_start", "session_end", "recording_start", 
#              "recording_end", "playback_start", "playback_end", 
#              "error", "quality_change", "cloud_sync"
```

---

## 💡 Examples

### Example 1: Complete Audio Workflow
```python
#!/usr/bin/env python3
"""Complete audio workflow example"""

from src.audio.audio_manager import *
import time

def main():
    # Initialize
    config = create_child_safe_config()
    manager = EnhancedAudioManager(config)
    
    print("🎵 Audio Workflow Demo")
    
    # Start session
    session_id = manager.start_session(
        child_id="demo_child",
        session_type=AudioSessionType.CONVERSATION
    )
    
    # Welcome message
    manager.speak(
        "مرحباً! سأقوم بتسجيل صوتك ثم تشغيله",
        language="ar",
        session_id=session_id
    )
    
    # Record audio
    print("🎤 Recording for 3 seconds...")
    audio_data, metadata = manager.record_audio(
        duration=3,
        session_id=session_id
    )
    
    # Play back recorded audio
    print("🔊 Playing back recorded audio...")
    manager.play_audio(
        audio_data=audio_data,
        volume=0.8,
        fade_in=0.2,
        fade_out=0.2,
        session_id=session_id
    )
    
    # Save in multiple formats
    formats = [AudioFormatType.WAV, AudioFormatType.MP3, AudioFormatType.OPUS]
    for fmt in formats:
        filename = f"demo_recording.{fmt.value}"
        success = manager.save_audio(
            audio_data=audio_data,
            filename=filename,
            format=fmt,
            quality=7
        )
        print(f"💾 Saved {fmt.value.upper()}: {success}")
    
    # Final message
    manager.speak(
        "تم الانتهاء من العرض التوضيحي!",
        language="ar",
        session_id=session_id
    )
    
    # Cleanup
    manager.end_session(session_id)
    manager.cleanup()
    
    print("✅ Demo completed!")

if __name__ == "__main__":
    main()
```

### Example 2: Multi-Session Management
```python
#!/usr/bin/env python3
"""Multi-session management example"""

from src.audio.audio_manager import *
import threading
import time

def child_session(manager, child_id):
    """Handle individual child session"""
    session_id = manager.start_session(
        child_id=child_id,
        session_type=AudioSessionType.PLAY_TIME
    )
    
    # Child-specific activities
    manager.speak(
        f"Hello {child_id}! Let's play together!",
        session_id=session_id
    )
    
    # Short recording
    audio_data, _ = manager.record_audio(
        duration=2,
        session_id=session_id
    )
    
    # Play back with effects
    manager.play_audio(
        audio_data=audio_data,
        volume=0.6,
        fade_in=0.3,
        session_id=session_id
    )
    
    manager.end_session(session_id)
    print(f"✅ {child_id} session completed")

def main():
    config = create_child_safe_config()
    manager = EnhancedAudioManager(config)
    
    print("👥 Multi-Session Demo")
    
    # Create multiple child sessions
    children = ["Alice", "Bob", "Charlie"]
    threads = []
    
    for child in children:
        thread = threading.Thread(
            target=child_session,
            args=(manager, child)
        )
        threads.append(thread)
        thread.start()
        time.sleep(1)  # Stagger session starts
    
    # Wait for all sessions to complete
    for thread in threads:
        thread.join()
    
    # Show final stats
    stats = manager.get_system_stats()
    print(f"\n📊 Final Stats:")
    print(f"   Sessions: {stats['active_sessions']}")
    print(f"   Recordings: {stats['performance']['total_recordings']}")
    print(f"   Playbacks: {stats['performance']['total_playbacks']}")
    
    manager.cleanup()
    print("✅ Multi-session demo completed!")

if __name__ == "__main__":
    main()
```

### Example 3: Real-time Audio Processing
```python
#!/usr/bin/env python3
"""Real-time audio processing with effects"""

from src.audio.audio_manager import *
import numpy as np

def apply_echo_effect(audio_data, delay_seconds=0.3, decay=0.5):
    """Add echo effect to audio"""
    sample_rate = 44100
    delay_samples = int(delay_seconds * sample_rate)
    
    # Create echo
    echo_audio = np.zeros(len(audio_data) + delay_samples)
    echo_audio[:len(audio_data)] = audio_data
    echo_audio[delay_samples:delay_samples+len(audio_data)] += audio_data * decay
    
    return echo_audio[:len(audio_data)]

def main():
    config = create_high_quality_config()
    manager = EnhancedAudioManager(config)
    
    print("🎭 Real-time Audio Effects Demo")
    
    session_id = manager.start_session(
        child_id="effects_demo",
        session_type=AudioSessionType.CONVERSATION
    )
    
    # Record audio
    print("🎤 Recording audio for effects...")
    manager.speak(
        "I will record your voice and add some cool effects!",
        session_id=session_id
    )
    
    audio_data, metadata = manager.record_audio(
        duration=4,
        process=True,
        session_id=session_id
    )
    
    # Apply effects
    print("🎭 Applying echo effect...")
    echo_audio = apply_echo_effect(audio_data)
    
    # Play original vs processed
    print("🔊 Playing original audio...")
    manager.play_audio(audio_data=audio_data, volume=0.7)
    
    time.sleep(1)
    
    print("🔊 Playing audio with echo...")
    manager.play_audio(audio_data=echo_audio, volume=0.7)
    
    # Save processed audio
    manager.save_audio(
        audio_data=echo_audio,
        filename="echo_effect.wav",
        format=AudioFormatType.WAV,
        metadata={"effect": "echo", "delay": 0.3, "decay": 0.5}
    )
    
    manager.speak(
        "Effects demo completed! The processed audio has been saved.",
        session_id=session_id
    )
    
    manager.end_session(session_id)
    manager.cleanup()
    
    print("✅ Effects demo completed!")

if __name__ == "__main__":
    main()
```

---

## 📈 Performance

### Performance Monitoring
```python
# Get real-time performance stats
stats = manager.get_system_stats()

print(f"Uptime: {stats['uptime_seconds']:.1f}s")
print(f"Total recordings: {stats['performance']['total_recordings']}")
print(f"Average processing time: {stats['performance']['average_processing_time']:.3f}s")
print(f"Error rate: {stats['performance']['total_errors']}")
```

### Performance Optimization Tips

1. **Use appropriate quality modes**:
   ```python
   # For real-time: use POWER_SAVE or BALANCED
   AudioQualityMode.POWER_SAVE
   
   # For archival: use HIGH_QUALITY
   AudioQualityMode.HIGH_QUALITY
   ```

2. **Choose optimal formats**:
   ```python
   # Low latency: OPUS
   # Small files: MP3
   # High quality: FLAC
   ```

3. **Configure sample rates**:
   ```python
   # Voice applications: 16kHz or 22kHz
   # Music applications: 44.1kHz or 48kHz
   ```

### Memory Usage
- **Audio caching**: Automatic cleanup after 50 items
- **Temporary files**: Auto-cleanup after 1 hour
- **Session data**: Saved and cleaned up automatically

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Audio Libraries Not Found
```
Error: Audio libraries not available. Some features will be limited.
```
**Solution**:
```bash
pip install soundfile librosa pydub pygame
```

#### 2. FFmpeg Not Found (for MP3/OPUS support)
```
Error: Audio libraries required for MP3 encoding
```
**Solution**:
- Windows: Download and install from https://ffmpeg.org/
- macOS: `brew install ffmpeg`
- Linux: `sudo apt-get install ffmpeg`

#### 3. PyAudio Installation Issues (Windows)
```
Error: Microsoft Visual C++ 14.0 is required
```
**Solution**:
```bash
pip install pipwin
pipwin install pyaudio
```

#### 4. No Audio Output
```
Audio playback successful but no sound
```
**Solutions**:
- Check system volume settings
- Verify audio device is not muted
- Try different audio output device
- Check pygame mixer initialization

#### 5. High CPU Usage
**Solutions**:
- Use lower quality modes for real-time applications
- Reduce sample rates for voice applications
- Enable audio caching
- Optimize session timeout settings

### Debug Mode
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Test system
manager = EnhancedAudioManager(config)
test_results = manager.test_audio_system()
print("System test results:", test_results)
```

### Performance Diagnostics
```python
# Run comprehensive diagnostics
python test_enhanced_audio_system.py

# Quick system test
python test_enhanced_audio_system.py quick
```

---

## 🚀 Advanced Features

### Cloud Integration
```python
# Enable cloud backup
config = AudioSystemConfig(
    enable_cloud_sync=True,
    cloud_backup_enabled=True
)

# Save with cloud sync
manager.save_audio(
    audio_data=audio_data,
    filename="important_recording.wav",
    cloud_sync=True,
    metadata={"priority": "high"}
)
```

### Custom Event Handlers
```python
def on_recording_start(event_data):
    print(f"Recording started: {event_data}")

def on_error(event_data):
    print(f"Audio error: {event_data['error']}")

# Register event handlers
manager.add_event_listener("recording_start", on_recording_start)
manager.add_event_listener("error", on_error)
```

### Session Persistence
```python
# Session data is automatically saved
session_info = manager.get_session_info(session_id)

# Export session data
export_path = manager.export_session_data(
    session_id=session_id,
    export_format="json"
)
```

### Quality Adaptation
```python
# Adaptive quality based on system performance
config = AudioSystemConfig(
    adaptive_quality=True,
    quality_mode=AudioQualityMode.ADAPTIVE
)

# Manual quality adjustment
manager._set_quality_mode(AudioQualityMode.HIGH_QUALITY)
```

### Batch Operations
```python
# Process multiple audio files
audio_files = ["file1.wav", "file2.wav", "file3.wav"]

for audio_file in audio_files:
    # Load, process, and save
    audio_data, _, _ = manager.audio_io.load_audio(audio_file)
    
    # Apply processing
    processed_audio = manager.processor.process(audio_data)
    
    # Save in new format
    output_file = audio_file.replace(".wav", ".mp3")
    manager.save_audio(
        audio_data=processed_audio,
        filename=output_file,
        format=AudioFormatType.MP3,
        quality=8
    )
```

---

## 📞 Support & Contributing

### Getting Help
- 📧 Email: support@ai-teddy-bear.com
- 📚 Documentation: https://docs.ai-teddy-bear.com
- 🐛 Issues: https://github.com/ai-teddy-bear/issues

### Contributing
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

### License
This project is licensed under the MIT License. See LICENSE file for details.

---

## 📝 Changelog

### Version 2.0.0 (Current)
- ✨ Enhanced audio manager with multi-format support
- 🔧 Improved performance monitoring
- 🌐 Cloud integration capabilities
- 🎵 Advanced audio effects support
- 📱 Better mobile device compatibility

### Version 1.0.0
- 🎤 Basic recording and playback
- 🗣️ Simple TTS functionality
- 📊 Session management

---

**🧸 AI Teddy Bear Project - Making Children's AI Interactions Magical! 🧸** 