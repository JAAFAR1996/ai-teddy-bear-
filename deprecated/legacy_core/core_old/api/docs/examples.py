"""
API Usage Examples and Code Samples
"""

# Python Client Example
PYTHON_CLIENT_EXAMPLE = """
import httpx
import asyncio

class TeddyBearClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    async def start_conversation(self, child_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/conversations/start",
                json={"child_id": child_id},
                headers=self.headers
            )
            return response.json()
    
    async def send_message(self, session_id: str, message: str):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/conversations/{session_id}/messages",
                json={"text": message},
                headers=self.headers
            )
            return response.json()

# Usage
async def main():
    client = TeddyBearClient("https://api.teddybear.com", "your-jwt-token")
    
    # Start conversation
    result = await client.start_conversation("child-123")
    session_id = result["session_id"]
    
    # Send message
    response = await client.send_message(session_id, "مرحبا")
    print(response["response_text"])

asyncio.run(main())
"""

# JavaScript Client Example
JAVASCRIPT_CLIENT_EXAMPLE = """
class TeddyBearAPI {
    constructor(baseURL, token) {
        this.baseURL = baseURL;
        this.headers = {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        };
    }
    
    async startConversation(childId) {
        const response = await fetch(`${this.baseURL}/api/v1/conversations/start`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ child_id: childId })
        });
        return response.json();
    }
    
    async sendMessage(sessionId, message) {
        const response = await fetch(`${this.baseURL}/api/v1/conversations/${sessionId}/messages`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ text: message })
        });
        return response.json();
    }
    
    async uploadAudio(sessionId, audioBlob) {
        const formData = new FormData();
        formData.append('audio', audioBlob);
        
        const response = await fetch(`${this.baseURL}/api/v1/conversations/${sessionId}/audio`, {
            method: 'POST',
            headers: { 'Authorization': this.headers.Authorization },
            body: formData
        });
        return response.json();
    }
}

// Usage
const api = new TeddyBearAPI('https://api.teddybear.com', 'your-jwt-token');

async function startChat() {
    try {
        const conversation = await api.startConversation('child-123');
        console.log('Session started:', conversation.session_id);
        
        const response = await api.sendMessage(conversation.session_id, 'مرحبا');
        console.log('AI Response:', response.response_text);
    } catch (error) {
        console.error('Error:', error);
    }
}
"""

# cURL Examples
CURL_EXAMPLES = """
# Authentication
curl -X POST "https://api.teddybear.com/api/v1/auth/login" \\
  -H "Content-Type: application/json" \\
  -d '{"email": "parent@example.com", "password": "password"}'

# Start Conversation
curl -X POST "https://api.teddybear.com/api/v1/conversations/start" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"child_id": "child-123", "initial_message": "مرحبا"}'

# Send Message
curl -X POST "https://api.teddybear.com/api/v1/conversations/session-456/messages" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{"text": "ما هي الشمس؟"}'

# Upload Audio
curl -X POST "https://api.teddybear.com/api/v1/conversations/session-456/audio" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\
  -F "audio=@recording.wav"

# Get Conversation History
curl -X GET "https://api.teddybear.com/api/v1/children/child-123/conversations" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
"""

# WebSocket Example
WEBSOCKET_EXAMPLE = """
// WebSocket Real-time Communication
const ws = new WebSocket('wss://api.teddybear.com/ws/conversation/session-456?token=YOUR_JWT_TOKEN');

ws.onopen = function(event) {
    console.log('Connected to conversation');
    
    // Send message
    ws.send(JSON.stringify({
        type: 'message',
        content: 'مرحبا دبدوب'
    }));
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'response':
            console.log('AI Response:', data.content);
            break;
        case 'audio':
            playAudio(data.audio_url);
            break;
        case 'emotion':
            updateEmotionDisplay(data.emotion);
            break;
    }
};

ws.onerror = function(error) {
    console.error('WebSocket error:', error);
};
"""

def get_all_examples():
    return {
        "python": PYTHON_CLIENT_EXAMPLE,
        "javascript": JAVASCRIPT_CLIENT_EXAMPLE,
        "curl": CURL_EXAMPLES,
        "websocket": WEBSOCKET_EXAMPLE
    }