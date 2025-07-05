"""Simple test to verify pytest is working"""

import pytest
from unittest.mock import MagicMock
import json


def test_basic_functionality():
    """Test basic functionality"""
    assert True


def test_encryption_mock():
    """Test encryption with mock"""
    # Mock encryption service
    encryption_service = MagicMock()
    encryption_service.encrypt.return_value = "encrypted_data"
    encryption_service.decrypt.return_value = "decrypted_data"

    # Test
    encrypted = encryption_service.encrypt("test_data")
    assert encrypted == "encrypted_data"

    decrypted = encryption_service.decrypt(encrypted)
    assert decrypted == "decrypted_data"


def test_json_operations():
    """Test JSON operations"""
    test_data = {"name": "Test Child", "age": 5, "language": "ar"}

    # Serialize and deserialize
    json_str = json.dumps(test_data)
    parsed_data = json.loads(json_str)

    assert parsed_data["name"] == "Test Child"
    assert parsed_data["age"] == 5
    assert parsed_data["language"] == "ar"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
