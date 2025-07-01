import logging

logger = logging.getLogger(__name__)

import os
import secrets
import string



def generate_secret(length: int = 32) -> str:
    """
    Generate a cryptographically secure random string

    :param length: Length of the secret string
    :return: Random secret string
    """
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_env_file(output_path: str = ".env"):
    """
    Generate a secure .env file with random secrets

    :param output_path: Path to the .env file
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    env_secrets = {
        "OPENAI_API_KEY": generate_secret(48),
        "ELEVENLABS_API_KEY": generate_secret(48),
        "ENCRYPTION_KEY": secrets.token_urlsafe(32),
        "REDIS_PASSWORD": generate_secret(24),
        "SECRET_KEY": secrets.token_hex(32),
        "DEBUG_SECRET_KEY": secrets.token_hex(16),
    }
    default_config = {
        "LLM_PROVIDER": "gpt-4",
        "LLM_SAFETY_LEVEL": "2",
        "VOICE_PROVIDER": "elevenlabs",
        "DEFAULT_VOICE": "josh",
        "COPPA_COMPLIANCE": "true",
        "GDPR_COMPLIANCE": "true",
        "DATA_RETENTION_DAYS": "30",
        "DEPLOYMENT_ENV": "development",
        "DEBUG_MODE": "true",
        "ANALYTICS_ENABLED": "true",
        "CONTENT_FILTER_ENABLED": "true",
        "CONTENT_FILTER_SENSITIVITY": "2",
        "MIN_AGE": "4",
        "MAX_AGE": "12",
        "LOG_LEVEL": "INFO",
        "REDIS_HOST": "localhost",
        "REDIS_PORT": "6379",
    }
    try:
        with open(output_path, "w") as f:
            for key, value in env_secrets.items():
                f.write(f"{key}={value}\n")
            for key, value in default_config.items():
                f.write(f"{key}={value}\n")
        logger.info(f"Secure .env file generated at {output_path}")
        for key, value in env_secrets.items():
            os.environ[key] = value
        return env_secrets
    except Exception as e:
        logger.info(f"Error generating .env file: {e}")
        return None


def main():
    """
    CLI for generating a secure .env file
    """
    import argparse

    parser = argparse.ArgumentParser(description="Generate a secure .env file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=".env",
        help="Path to the output .env file (default: .env)",
    )
    args = parser.parse_args()
    generate_env_file(args.output)


if __name__ == "__main__":
    main()
