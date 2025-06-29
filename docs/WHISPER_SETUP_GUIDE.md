# 🎤 Whisper & ElevenLabs Setup Guide

## Overview
The AI Teddy Bear now uses:
- **OpenAI Whisper** for high-accuracy Speech-to-Text (STT)
- **ElevenLabs** for high-quality Text-to-Speech (TTS) 
- **Google Speech Recognition** and **gTTS** as fallbacks

## Quick Setup

### 1. Install Dependencies
```bash
pip install openai-whisper elevenlabs
```

### 2. Configure API Keys
Add to `config/config.json`:
```json
{
  "API_KEYS": {
    "OPENAI_API_KEY": "sk-your-openai-key-here",
    "ELEVENLABS_API_KEY": "your-elevenlabs-key-here"
  }
}
```

### 3. Test Installation
Run the system and check console output:
- ✅ Whisper model loaded successfully
- ✅ ElevenLabs initialized successfully

## Features

### Whisper STT
- **High accuracy** speech recognition
- **Multilingual** support (Arabic + English)
- **Local processing** (no internet required after model download)
- **Automatic fallback** to Google Speech if Whisper fails

### ElevenLabs TTS
- **Natural voices** optimized for children
- **Multilingual** support including Arabic
- **Fast generation** and high quality
- **Automatic fallback** to gTTS if ElevenLabs fails

## Troubleshooting

### Whisper Issues
```bash
# If Whisper fails to install
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install openai-whisper
```

### ElevenLabs Issues
- Ensure you have a valid API key with credits
- Check internet connection for API calls
- System will fallback to gTTS if ElevenLabs fails

### Performance Tips
- Whisper models: `tiny` (fastest) → `base` (balanced) → `large` (best)
- Default is `base` for good balance of speed and accuracy
- First run downloads model (~150MB for base model)

## Voice Quality Comparison

| Technology | Quality | Speed | Internet | Cost |
|------------|---------|-------|----------|------|
| Whisper STT | Excellent | Fast | No* | Free |
| Google STT | Good | Fast | Yes | Free |
| ElevenLabs TTS | Excellent | Fast | Yes | Paid |
| gTTS | Good | Medium | Yes | Free |

*After initial model download

## Production Notes
- System automatically detects available technologies
- Graceful fallbacks ensure system always works
- All voice features work even without API keys (using free alternatives)
- Console shows which technology is being used for each operation

---
🧸 **The AI Teddy Bear now delivers enterprise-grade voice interaction!** 