import logging

logger = logging.getLogger(__name__)

import argparse
import base64
import os
import secrets


def generate_encryption_key(key_length: int = 32) -> str:
    """
    Generate a secure encryption key

    :param key_length: Length of the key in bytes
    :return: Base64 encoded encryption key
    """
    key = secrets.token_bytes(key_length)
    return base64.urlsafe_b64encode(key).decode("utf-8")


def main():
    """
    CLI for generating encryption keys
    """
    parser = argparse.ArgumentParser(description="Generate a secure encryption key")
    parser.add_argument(
        "-l",
        "--length",
        type=int,
        default=32,
        help="Length of the encryption key in bytes (default: 32)",
    )
    parser.add_argument("-o", "--output", type=str, help="Output file to save the key")
    args = parser.parse_args()
    encryption_key = generate_encryption_key(args.length)
    logger.info(f"Generated Encryption Key: {encryption_key}")
    if args.output:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
            with open(args.output, "w") as f:
                f.write(encryption_key)
            logger.info(f"Encryption key saved to {args.output}")
        except Exception as e:
            logger.info(f"Error saving encryption key: {e}")


if __name__ == "__main__":
    main()
