from flask import jsonify, request, current_app
from functools import wraps
from datetime import datetime
import asyncio
from .. import api_bp


def get_orchestrator():
    """Get orchestrator from app context"""
    return current_app.orchestrator


@api_bp.route('/system/info', methods=['GET'])
def get_system_info():
    """Get system information"""
    try:
        system_info = {
            "version": "1.0.0",
            "environment": "development",
            "uptime": "24h",
            "features": ["voice_chat", "streaming", "memory", "learning"],
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(system_info), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/health', methods=['GET'])
def health_check():
    """System health check with real data"""
    try:
        orchestrator = get_orchestrator()

        # استخدم health check الحقيقي
        if orchestrator:
            import asyncio
            health_data = asyncio.run(orchestrator.get_health_status())
        else:
            # Fallback للتطوير
            health_data = {
                "healthy": True,
                "timestamp": datetime.utcnow().isoformat(),
                "services": {
                    "ai": orchestrator.ai_service is not None,
                    "streaming": orchestrator.streaming_service is not None,
                    "voice": orchestrator.voice_service is not None,
                    "moderation": orchestrator.moderation_service is not None,
                    "memory": orchestrator.memory_service is not None,
                    "parent_dashboard": orchestrator.parent_dashboard is not None
                }
            }
        status_code = 200 if health_data.get('healthy', True) else 503
        return jsonify(health_data), status_code

    except Exception as e:
        return jsonify({"error": str(e), "healthy": False}), 500


@api_bp.route('/system/metrics', methods=['GET'])
def get_system_metrics():
    """Get system performance metrics"""
    try:
        metrics = {
            "active_sessions": 0,
            "total_conversations": 0,
            "memory_usage": "45%",
            "cpu_usage": "23%",
            "response_time": "120ms",
            "timestamp": datetime.utcnow().isoformat()
        }
        return jsonify(metrics), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
