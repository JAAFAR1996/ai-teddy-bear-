import logging
from datetime import datetime
from typing import Any, Dict

import requests
from chaostoolkit.types import Configuration

logger = logging.getLogger(__name__)


def restore_all_safety_systems(configuration: Configuration = None) -> Dict[str, Any]:
    """Restore all safety systems to normal operation"""
    try:
        restoration_results = {}
        endpoints = {
            "content_filter": "http://safety-service:8000/restore",
            "ai_safety": "http://ai-service:8000/restore",
            "database": "http://child-service:8000/restore",
        }
        for component, url in endpoints.items():
            response = requests.post(
                url, json={"component": component}, timeout=10)
            restoration_results[component] = response.status_code == 200

        all_restored = all(restoration_results.values())
        logger.info(
            f"Safety system restoration: {'successful' if all_restored else 'partial'}")
        return {"success": all_restored, "components": restoration_results}
    except Exception as e:
        logger.error(f"Safety system restoration failed: {e}")
        return {"success": False, "error": str(e)}


def clear_toxic_content_cache(configuration: Configuration = None) -> Dict[str, Any]:
    """Clear any cached toxic content from the system"""
    try:
        response = requests.post(
            "http://safety-service:8000/cache/clear",
            json={"cache_type": "toxic_content"},
            timeout=10,
        )
        return {"success": response.status_code == 200}
    except Exception as e:
        logger.error(f"Toxic content cache clear failed: {e}")
        return {"success": False, "error": str(e)}


def reset_ai_models(configuration: Configuration = None) -> Dict[str, Any]:
    """Reset AI models to safe baseline state"""
    try:
        response = requests.post(
            "http://ai-service:8000/models/reset",
            json={"reset_to": "safe_baseline"},
            timeout=30,
        )
        return {"success": response.status_code == 200}
    except Exception as e:
        logger.error(f"AI model reset failed: {e}")
        return {"success": False, "error": str(e)}
