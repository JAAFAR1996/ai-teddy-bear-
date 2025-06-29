# Azure Speech Services Integration

## Overview
This document provides detailed instructions for integrating Azure Cognitive Speech Services with the AI Teddy Bear project.

## Prerequisites
- Azure Account
- Active Azure Subscription
- Python 3.9+
- Azure Cognitive Services Speech SDK

## Setup Steps

### 1. Create Azure Cognitive Services Resource
1. Log in to [Azure Portal](https://portal.azure.com/)
2. Click "Create a resource"
3. Search for "Speech Services"
4. Click "Create"
5. Configure resource:
   - Subscription: Select your subscription
   - Resource group: Create new or select existing
   - Name: `ai-teddy-bear-speech`
   - Region: Select closest to your deployment
   - Pricing tier: Select appropriate tier (F0 for free tier, S0 for standard)

### 2. Retrieve Credentials
1. Navigate to your Speech Services resource
2. Go to "Keys and Endpoint"
3. Copy:
   - Key 1 or Key 2
   - Region/Location

### 3. Environment Configuration
Add the following to your `.env` file:
```
AZURE_SPEECH_KEY=your_speech_key_here
AZURE_SPEECH_REGION=your_region_here
```

### 4. Install Dependencies
```bash
pip install azure-cognitiveservices-speech
```

### 5. Python Configuration Example
```python
import os
import azure.cognitiveservices.speech as speechsdk

def create_speech_config():
    speech_key = os.getenv('AZURE_SPEECH_KEY')
    service_region = os.getenv('AZURE_SPEECH_REGION')
    
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, 
        region=service_region
    )
    
    # Optional: Configure speech recognition
    speech_config.speech_recognition_language = "en-US"
    
    return speech_config
```

## Features Supported
- Speech-to-Text
- Text-to-Speech
- Language Detection
- Custom Voice Models

## Security Considerations
- Never commit API keys to version control
- Use environment variables
- Implement key rotation
- Use least-privilege access

## Troubleshooting
- Verify network connectivity
- Check API key and region
- Ensure correct SDK version
- Review Azure service logs

## Performance Optimization
- Use appropriate speech recognition model
- Minimize latency by selecting closest region
- Implement caching for repeated requests

## Compliance
- GDPR compliant
- COPPA considerations for child-focused application

## Cost Management
- Monitor usage in Azure Portal
- Set up budget alerts
- Consider free tier for development

## Example Usage
```python
def transcribe_audio(audio_path):
    speech_config = create_speech_config()
    audio_config = speechsdk.AudioConfig(filename=audio_path)
    
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, 
        audio_config=audio_config
    )
    
    result = speech_recognizer.recognize_once()
    
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation = result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation.reason}")
```

## Recommended Next Steps
1. Test speech recognition
2. Implement error handling
3. Add logging
4. Performance benchmark

## Resources
- [Azure Speech Services Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/speech-service/)
- [Python Speech SDK Samples](https://github.com/Azure-Samples/cognitive-services-speech-sdk)
