from flask import jsonify, request
from datetime import datetime
from .. import api_bp
from ..middleware.auth import require_child_auth, require_parent_auth

# Import or define orchestrator here
try:
    from ..services.orchestrator import orchestrator
except ImportError:
    orchestrator = None


@api_bp.route('/conversations', methods=['POST'])
@require_child_auth
def start_conversation():
    """Start new conversation session"""
    try:
        data = request.json
        child_id = data.get('child_id', request.child_id)

        conversation = {
            "id": f"conv_{child_id}_{int(datetime.utcnow().timestamp())}",
            "child_id": child_id,
            "started_at": datetime.utcnow().isoformat(),
            "status": "active"
        }

        return jsonify(conversation), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/conversations/<conversation_id>/messages', methods=['POST'])
@require_child_auth
async def send_message(conversation_id):
    """Send message in conversation"""
    try:
        data = request.json
        message = data.get('message')
        message_type = data.get('type', 'text')

        if not message:
            return jsonify({"error": "Message required"}), 400

        if orchestrator and hasattr(orchestrator, 'ai_service'):
            # معالجة حقيقية
            response = await orchestrator.ai_service.get_response(message)
            ai_response = response.text if hasattr(
                response, 'text') else str(response)
        else:
            # Mock response
            ai_response = "مرحباً! كيف يمكنني مساعدتك اليوم؟"

        # Mock AI response
        response = {
            "id": f"msg_{conversation_id}_{int(datetime.utcnow().timestamp())}",
            "conversation_id": conversation_id,
            "user_message": message,
            "ai_response": "مرحباً! كيف يمكنني مساعدتك اليوم؟",
            "timestamp": datetime.utcnow().isoformat()
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/conversations/<conversation_id>', methods=['GET'])
@require_parent_auth
def get_conversation(conversation_id):
    """Get conversation details"""
    try:
        # Mock conversation data
        conversation = {
            "id": conversation_id,
            "messages": [
                {
                    "id": "msg_1",
                    "type": "user",
                    "content": "مرحبا",
                    "timestamp": datetime.utcnow().isoformat()
                },
                {
                    "id": "msg_2",
                    "type": "ai",
                    "content": "أهلاً وسهلاً بك!",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "duration": "5 minutes",
            "status": "completed"
        }

        return jsonify(conversation), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
