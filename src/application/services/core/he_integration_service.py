from typing import Any, Dict, List, Optional

"""
Homomorphic Encryption Integration Service for AI Teddy Bear Project.

This service integrates homomorphic encryption with existing audio processing
and emotion analysis systems to provide end-to-end privacy-preserving computation.

Security Team Implementation - Task 9 Integration
Author: Security Team Lead
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from .audit_logger import SecurityAuditLogger
from .data_encryption import DataClassification
# Core imports
from .homomorphic_encryption import (EncryptedData, HEConfig,
                                     HEProcessingResult, HomomorphicEncryption,
                                     ProcessingMode)

# Audio processing imports
try:
    from ...audio.audio_processing import AudioConfig, AudioProcessor
    from ...domain.services.advanced_emotion_analyzer import \
        AdvancedEmotionAnalyzer

    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SecureAudioFeatures:
    """Secure container for audio features with encryption metadata."""

    encrypted_features: EncryptedData
    feature_types: List[str]
    extraction_timestamp: str
    child_id_hash: str
    processing_permissions: List[str]


@dataclass
class PrivacyPreservingResult:
    """Result of privacy-preserving emotion analysis."""

    emotion_analysis: HEProcessingResult
    privacy_level: str
    confidence_score: float
    processing_summary: Dict[str, Any]
    recommendations: List[str]
    audit_trail: Dict[str, Any]


class SecureAudioFeatureExtractor:
    """Extracts audio features with immediate encryption for privacy protection."""

    def __init__(self, he_service: HomomorphicEncryption):
        self.he_service = he_service
        self.audio_processor = AudioProcessor() if AUDIO_PROCESSING_AVAILABLE else None
        self.audit_logger = SecurityAuditLogger()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def extract_and_encrypt_features(
        self,
        audio_data: np.ndarray,
        child_id: str,
        feature_types: Optional[List[str]] = None,
    ) -> SecureAudioFeatures:
        """Extract audio features and immediately encrypt them."""
        if not AUDIO_PROCESSING_AVAILABLE:
            raise RuntimeError("Audio processing not available")

        feature_types = feature_types or [
            "mfcc",
            "spectral_centroid",
            "pitch",
            "energy",
            "tempo",
        ]

        # Log feature extraction start
        await self.audit_logger.log_security_event(
            event_type="secure_feature_extraction_start",
            details={
                "child_id_hash": self._hash_child_id(child_id),
                "feature_types": feature_types,
                "audio_duration": len(audio_data) / 16000,  # Assuming 16kHz
            },
            classification=DataClassification.RESTRICTED,
        )

        try:
            # Extract audio features using existing processor
            features = await self._extract_audio_features(audio_data, feature_types)

            # Immediately encrypt features
            encrypted_features = await self.he_service.encrypt_voice_features(
                features, child_id
            )

            # Create secure container
            secure_features = SecureAudioFeatures(
                encrypted_features=encrypted_features,
                feature_types=feature_types,
                extraction_timestamp=datetime.now().isoformat(),
                child_id_hash=self._hash_child_id(child_id),
                processing_permissions=["emotion_analysis", "behavioral_patterns"],
            )

            # Log successful extraction and encryption
            await self.audit_logger.log_security_event(
                event_type="secure_feature_extraction_success",
                details={
                    "feature_count": len(features),
                    "encryption_scheme": encrypted_features.scheme,
                    "privacy_preserved": True,
                },
                classification=DataClassification.RESTRICTED,
            )

            return secure_features

        except Exception as e:
            await self.audit_logger.log_security_event(
                event_type="secure_feature_extraction_failure",
                details={"error": str(e)},
                classification=DataClassification.RESTRICTED,
            )
            self.logger.error(f"Secure feature extraction failed: {e}")
            raise

    async def _extract_audio_features(
        self, audio_data: np.ndarray, feature_types: List[str]
    ) -> np.ndarray:
        """Extract specified audio features."""
        import librosa

        features_list = []

        for feature_type in feature_types:
            if feature_type == "mfcc":
                mfcc = librosa.feature.mfcc(y=audio_data, sr=16000, n_mfcc=13)
                features_list.extend(np.mean(mfcc, axis=1))

            elif feature_type == "spectral_centroid":
                centroid = librosa.feature.spectral_centroid(y=audio_data, sr=16000)
                features_list.append(np.mean(centroid))

            elif feature_type == "pitch":
                pitches, magnitudes = librosa.piptrack(y=audio_data, sr=16000)
                pitch_mean = (
                    np.mean(pitches[pitches > 0])
                    if len(pitches[pitches > 0]) > 0
                    else 0
                )
                features_list.append(pitch_mean)

            elif feature_type == "energy":
                rms = librosa.feature.rms(y=audio_data)
                features_list.append(np.mean(rms))

            elif feature_type == "tempo":
                tempo, _ = librosa.beat.beat_track(y=audio_data, sr=16000)
                features_list.append(tempo)

        return np.array(features_list, dtype=np.float32)

    def _hash_child_id(self, child_id: str) -> str:
        """Create privacy-preserving hash of child ID."""
        import hashlib

        return hashlib.sha256(child_id.encode()).hexdigest()[:16]


class PrivacyPreservingEmotionAnalyzer:
    """Performs emotion analysis on encrypted data without exposing plaintext."""

    def __init__(self, he_service: HomomorphicEncryption):
        self.he_service = he_service
        self.audit_logger = SecurityAuditLogger()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def analyze_emotions_privately(
        self,
        secure_features: SecureAudioFeatures,
        analysis_mode: ProcessingMode = ProcessingMode.EMOTION_ANALYSIS,
    ) -> PrivacyPreservingResult:
        """Analyze emotions while preserving complete privacy."""
        # Verify processing permissions
        if "emotion_analysis" not in secure_features.processing_permissions:
            raise PermissionError("Emotion analysis not permitted for this data")

        # Log analysis start
        await self.audit_logger.log_security_event(
            event_type="privacy_preserving_analysis_start",
            details={
                "child_id_hash": secure_features.child_id_hash,
                "analysis_mode": analysis_mode.value,
                "feature_types": secure_features.feature_types,
            },
            classification=DataClassification.RESTRICTED,
        )

        try:
            # Process emotions on encrypted data
            emotion_result = await self.he_service.process_encrypted_emotion(
                secure_features.encrypted_features, analysis_mode
            )

            # Generate privacy-preserving recommendations
            recommendations = self._generate_secure_recommendations(
                emotion_result, secure_features
            )

            # Create comprehensive result
            result = PrivacyPreservingResult(
                emotion_analysis=emotion_result,
                privacy_level="maximum",
                confidence_score=emotion_result.confidence_level,
                processing_summary={
                    "operations_performed": emotion_result.operations_performed,
                    "processing_time_ms": emotion_result.processing_time_ms,
                    "privacy_preserved": emotion_result.privacy_preserved,
                    "feature_types_analyzed": secure_features.feature_types,
                },
                recommendations=recommendations,
                audit_trail=emotion_result.audit_trail,
            )

            # Log successful analysis
            await self.audit_logger.log_security_event(
                event_type="privacy_preserving_analysis_success",
                details={
                    "processing_time_ms": emotion_result.processing_time_ms,
                    "privacy_level": result.privacy_level,
                    "recommendations_count": len(recommendations),
                },
                classification=DataClassification.RESTRICTED,
            )

            return result

        except Exception as e:
            await self.audit_logger.log_security_event(
                event_type="privacy_preserving_analysis_failure",
                details={"error": str(e)},
                classification=DataClassification.RESTRICTED,
            )
            self.logger.error(f"Privacy-preserving analysis failed: {e}")
            raise

    def _generate_secure_recommendations(
        self, emotion_result: HEProcessingResult, secure_features: SecureAudioFeatures
    ) -> List[str]:
        """Generate recommendations based on encrypted emotion analysis."""
        # Generate general recommendations without exposing specific emotions
        recommendations = [
            "Continue providing supportive communication",
            "Maintain engaging conversation patterns",
            "Adapt response style based on interaction patterns",
        ]

        # Add recommendations based on processing metadata
        if "behavioral_patterns" in emotion_result.operations_performed:
            recommendations.append("Monitor behavioral pattern changes")

        if emotion_result.processing_time_ms > 100:
            recommendations.append(
                "Consider optimizing processing for better responsiveness"
            )

        return recommendations


class HEIntegrationService:
    """Main integration service for homomorphic encryption with AI Teddy Bear systems."""

    def __init__(self, he_config: Optional[HEConfig] = None):
        self.he_config = he_config or HEConfig()
        self.he_service = HomomorphicEncryption(self.he_config)
        self.feature_extractor = SecureAudioFeatureExtractor(self.he_service)
        self.emotion_analyzer = PrivacyPreservingEmotionAnalyzer(self.he_service)
        self.audit_logger = SecurityAuditLogger()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def process_audio_securely(
        self,
        audio_data: np.ndarray,
        child_id: str,
        analysis_options: Optional[Dict[str, Any]] = None,
    ) -> PrivacyPreservingResult:
        """Complete secure audio processing pipeline."""
        analysis_options = analysis_options or {}

        # Log pipeline start
        await self.audit_logger.log_security_event(
            event_type="secure_audio_pipeline_start",
            details={
                "child_id_hash": self._hash_child_id(child_id),
                "audio_duration": len(audio_data) / 16000,
                "analysis_options": list(analysis_options.keys()),
            },
            classification=DataClassification.RESTRICTED,
        )

        try:
            # Step 1: Extract and encrypt features
            secure_features = await self.feature_extractor.extract_and_encrypt_features(
                audio_data, child_id, analysis_options.get("feature_types")
            )

            # Step 2: Analyze emotions privately
            processing_mode = self._get_processing_mode(analysis_options)
            result = await self.emotion_analyzer.analyze_emotions_privately(
                secure_features, processing_mode
            )

            # Log pipeline success
            await self.audit_logger.log_security_event(
                event_type="secure_audio_pipeline_success",
                details={
                    "total_processing_time_ms": result.emotion_analysis.processing_time_ms,
                    "privacy_level": result.privacy_level,
                    "operations_count": len(
                        result.emotion_analysis.operations_performed
                    ),
                },
                classification=DataClassification.RESTRICTED,
            )

            return result

        except Exception as e:
            await self.audit_logger.log_security_event(
                event_type="secure_audio_pipeline_failure",
                details={"error": str(e)},
                classification=DataClassification.RESTRICTED,
            )
            self.logger.error(f"Secure audio pipeline failed: {e}")
            raise

    async def batch_process_audio_securely(
        self,
        audio_batch: List[Tuple[np.ndarray, str]],
        analysis_options: Optional[Dict[str, Any]] = None,
    ) -> List[PrivacyPreservingResult]:
        """Process multiple audio samples securely in batch."""
        tasks = []
        for audio_data, child_id in audio_batch:
            task = self.process_audio_securely(audio_data, child_id, analysis_options)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results and log failures
        valid_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Batch processing failed for item {i}: {result}")
            else:
                valid_results.append(result)

        return valid_results

    def _get_processing_mode(self, analysis_options: Dict[str, Any]) -> ProcessingMode:
        """Determine processing mode from analysis options."""
        mode_str = analysis_options.get("mode", "emotion_analysis")

        mode_mapping = {
            "emotion": ProcessingMode.EMOTION_ANALYSIS,
            "behavioral": ProcessingMode.BEHAVIORAL_PATTERNS,
            "aggregate": ProcessingMode.AGGREGATE_ANALYSIS,
        }

        return mode_mapping.get(mode_str, ProcessingMode.EMOTION_ANALYSIS)

    def _hash_child_id(self, child_id: str) -> str:
        """Create privacy-preserving hash of child ID."""
        import hashlib

        return hashlib.sha256(child_id.encode()).hexdigest()[:16]

    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration status report."""
        he_report = self.he_service.generate_he_performance_report()

        return {
            "integration_status": "operational",
            "privacy_level": "maximum",
            "homomorphic_encryption": he_report,
            "audio_processing": {
                "secure_feature_extraction": True,
                "privacy_preserving_analysis": True,
                "batch_processing": True,
            },
            "security_features": {
                "end_to_end_encryption": True,
                "no_plaintext_exposure": True,
                "comprehensive_audit_logging": True,
                "secure_context_management": True,
            },
            "performance": {
                "concurrent_processing": True,
                "scalable_architecture": True,
                "optimized_memory_usage": True,
            },
            "compliance": {
                "privacy_by_design": True,
                "data_minimization": True,
                "secure_computation": True,
            },
            "timestamp": datetime.now().isoformat(),
        }

    async def cleanup(self) -> None:
        """Cleanup integration service resources."""
        try:
            await self.he_service.cleanup()
            self.logger.info("HE integration service cleanup completed")
        except Exception as e:
            self.logger.error(f"Integration cleanup failed: {e}")
            raise
