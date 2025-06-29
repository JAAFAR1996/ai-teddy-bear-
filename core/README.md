# 🧸 AI Teddy Bear System - Quick Start

## 🚀 Running the System

### Prerequisites
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your-api-key-here
```

### Start API Server
```bash
# Development mode with auto-reload
python -m core.main --reload

# Production mode
python -m core.main --workers 4

# Custom port
python -m core.main --port 8080
```

### Start ESP32 Simulator
```bash
# In a separate terminal
python core/run_simulator.py
```

## 📁 Project Structure

```
core/
├── api/
│   └── production_api.py      # FastAPI server with all endpoints
├── application/
│   └── services/
│       ├── ai_service.py      # AI logic (OpenAI integration)
│       └── voice_service.py   # Voice processing (STT/TTS)
├── infrastructure/
│   ├── container.py           # Dependency injection
│   └── config.py             # Configuration management
├── simulators/
│   └── esp32_production_simulator.py  # PySide6 GUI simulator
├── main.py                   # Simple API launcher
└── run_simulator.py         # Simple simulator launcher
```

## 🔧 Configuration

Create a `.env` file:
```env
OPENAI_API_KEY=sk-...
ENVIRONMENT=development
DEBUG=false
```

Or use environment variables directly.

## 🧪 Testing

### API Endpoints
- Health check: `http://localhost:8000/health`
- API docs: `http://localhost:8000/docs`
- Device registration: `POST /api/v1/devices/register`
- Process audio: `POST /api/v1/audio/process`

### Simulator Usage
1. Click "Connect to Server"
2. Click "Setup Child Profile" 
3. Hold "Hold to Talk" button and speak
4. Release to send audio to server

## 🎯 Key Features

✅ **Clean Architecture**: Proper separation of concerns  
✅ **Async Everything**: No blocking operations  
✅ **Modern UI**: PySide6 instead of tkinter  
✅ **Secure**: API keys in environment variables  
✅ **Simple**: No over-engineering, just what's needed

## 📚 More Information

See [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) for detailed architecture documentation. 