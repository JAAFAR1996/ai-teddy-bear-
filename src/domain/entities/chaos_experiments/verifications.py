import logging

import requests
from chaostoolkit.types import Configuration

logger = logging.getLogger(__name__)


def verify_toxic_content_blocked(configuration: Configuration = None) -> bool:
    """Verify that toxic content is being blocked"""
    try:
        response = requests.post(
            "http://safety-service:8000/moderate",
            json={"content": "harmful content for children test"},
            timeout=10,
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("blocked", False) and result.get("confidence", 0.0) > 0.8
        return False
    except Exception as e:
        logger.error(f"Toxic content verification failed: {e}")
        return False


def verify_hallucination_detection(configuration: Configuration = None) -> bool:
    """Verify AI hallucination detection is working"""
    try:
        response = requests.post(
            "http://ai-service:8000/validate",
            json={"content": "The sky is made of cotton candy and children can fly",
                  "check_hallucination": True},
            timeout=10,
        )
        if response.status_code == 200:
            return response.json().get("hallucination_detected", False)
        return False
    except Exception as e:
        logger.error(f"Hallucination detection verification failed: {e}")
        return False


def verify_safety_under_load(configuration: Configuration = None) -> bool:
    """Verify safety systems maintain effectiveness under load"""
    try:
        response = requests.post(
            "http://safety-service:8000/moderate",
            json={"content": "inappropriate test content"},
            timeout=5,
        )
        return response.status_code == 200 and response.json().get("blocked", False)
    except Exception as e:
        logger.error(f"Safety under load verification failed: {e}")
        return False


def verify_safety_fallback_systems(configuration: Configuration = None) -> bool:
    """Verify safety fallback systems are operational"""
    try:
        response = requests.get(
            "http://safety-service:8000/fallback/status", timeout=10)
        if response.status_code == 200:
            status = response.json()
            return status.get("fallback_active", False) and status.get("safety_maintained", False)
        return False
    except Exception as e:
        logger.error(f"Safety fallback verification failed: {e}")
        return False
