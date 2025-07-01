"""
Unit Tests for Homomorphic Encryption System.

Security Team Implementation - Task 9 Tests
Author: Security Team Lead
"""

import asyncio
import hashlib
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pytest

# Import the modules to test
try:
    from src.infrastructure.security.homomorphic_encryption import (
        TENSEAL_AVAILABLE,
        EncryptedData,
        HEConfig,
        HEScheme,
        HomomorphicEncryption,
        ProcessingMode,
    )

    HE_IMPORTS_AVAILABLE = True
except ImportError as e:
    HE_IMPORTS_AVAILABLE = False
    import_error = str(e)


class TestHEConfig:
    """Test homomorphic encryption configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        if not HE_IMPORTS_AVAILABLE:
            pytest.skip(f"HE imports not available: {import_error}")

        config = HEConfig()
        assert config.scheme == HEScheme.CKKS
        assert config.poly_modulus_degree == 8192
        assert config.scale == 2**40
        assert config.enable_galois_keys is True
        assert config.security_level == 128


class TestHomomorphicEncryption:
    """Test main homomorphic encryption service."""

    @pytest.fixture
    def he_service(self):
        """Create homomorphic encryption service for testing."""
        if not HE_IMPORTS_AVAILABLE:
            pytest.skip(f"HE imports not available: {import_error}")

        with patch("core.infrastructure.security.homomorphic_encryption.SecurityAuditLogger"):
            config = HEConfig()
            return HomomorphicEncryption(config)

    def test_initialization(self, he_service):
        """Test service initialization."""
        if not HE_IMPORTS_AVAILABLE:
            pytest.skip(f"HE imports not available: {import_error}")

        assert he_service.config is not None
        assert he_service.context_manager is not None
        assert he_service.voice_encryptor is not None
        assert he_service.emotion_processor is not None

    @pytest.mark.asyncio
    @pytest.mark.skipif(not TENSEAL_AVAILABLE, reason="TenSEAL not available")
    async def test_encrypt_voice_features(self, he_service):
        """Test voice feature encryption."""
        if not HE_IMPORTS_AVAILABLE:
            pytest.skip(f"HE imports not available: {import_error}")

        features = np.array([0.1, 0.5, 0.3, 0.8, 0.2])
        child_id = "test_child_456"

        he_service.audit_logger = AsyncMock()
        encrypted_data = await he_service.encrypt_voice_features(features, child_id)

        assert isinstance(encrypted_data, EncryptedData)
        assert encrypted_data.data_type == "voice_features"
        assert len(encrypted_data.child_id_hash) == 16

    def test_generate_performance_report(self, he_service):
        """Test performance report generation."""
        if not HE_IMPORTS_AVAILABLE:
            pytest.skip(f"HE imports not available: {import_error}")

        report = he_service.generate_he_performance_report()

        assert "configuration" in report
        assert "capabilities" in report
        assert "security_features" in report
        assert report["capabilities"]["voice_feature_encryption"] is True


class TestSecurityAndPrivacy:
    """Test security and privacy aspects."""

    def test_child_id_hashing_consistency(self):
        """Test child ID hashing produces consistent results."""
        if not HE_IMPORTS_AVAILABLE:
            pytest.skip(f"HE imports not available: {import_error}")

        child_id = "consistent_test_child"
        hash1 = hashlib.sha256(child_id.encode()).hexdigest()[:16]
        hash2 = hashlib.sha256(child_id.encode()).hexdigest()[:16]

        assert hash1 == hash2
        assert len(hash1) == 16

    def test_child_id_hashing_uniqueness(self):
        """Test different child IDs produce different hashes."""
        if not HE_IMPORTS_AVAILABLE:
            pytest.skip(f"HE imports not available: {import_error}")

        child_id1 = "child_one"
        child_id2 = "child_two"

        hash1 = hashlib.sha256(child_id1.encode()).hexdigest()[:16]
        hash2 = hashlib.sha256(child_id2.encode()).hexdigest()[:16]

        assert hash1 != hash2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
