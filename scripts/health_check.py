import logging
import sys
from typing import Dict


def check_services() -> Dict[str, bool]:
    """
    Perform comprehensive health checks for critical services

    :return: Dictionary of service statuses
    """
    health_status = {
        "database_connection": False,
        "redis_connection": False,
        "llm_service": False,
        "voice_service": False,
    }

    try:
        # Database Connection Check
        import sqlite3

        conn = sqlite3.connect("data/child_memories.db")
        conn.cursor().execute("SELECT 1")
        conn.close()
        health_status["database_connection"] = True
    except Exception as e:
        logging.error(f"Database connection failed: {e}")

    try:
        # Redis Connection Check
        import redis

        r = redis.Redis(host="localhost", port=6379, db=0)
        r.ping()
        health_status["redis_connection"] = True
    except Exception as e:
        logging.error(f"Redis connection failed: {e}")

    try:
        # LLM Service Check
        from src.application.services.llm_service import LLMService

        llm_service = LLMService()
        test_response = llm_service.generate_response(
            {"user_input": "Health check test", "language": "en"}
        )
        if test_response and len(test_response) > 0:
            health_status["llm_service"] = True
    except Exception as e:
        logging.error(f"LLM service check failed: {e}")

    try:
        # Voice Service Check
        from src.application.services.voice_interaction_service import \
            VoiceInteractionService

        voice_service = VoiceInteractionService()
        test_audio = voice_service.synthesize_speech("Health check test")
        if test_audio and len(test_audio) > 0:
            health_status["voice_service"] = True
    except Exception as e:
        logging.error(f"Voice service check failed: {e}")

    return health_status


def main():
    """
    Run health checks and exit with appropriate status code
    """
    logging.basicConfig(level=logging.INFO)

    try:
        service_status = check_services()

        # Log detailed status
        for service, status in service_status.items():
            logging.info(f"{service}: {'Healthy' if status else 'Unhealthy'}")

        # Determine overall health
        if all(service_status.values()):
            logging.info("All services are healthy")
            sys.exit(0)
        else:
            logging.error("Some services are unhealthy")
            sys.exit(1)

    except Exception as e:
        logging.error(f"Health check failed with unexpected error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
