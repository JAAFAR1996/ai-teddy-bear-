"""
🔄 Legacy Moderation Adapter
Maintains backward compatibility with old moderation interfaces
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
import logging
import warnings


@dataclass
class LegacyModerationParams:
    """Parameter object for legacy moderation methods"""
    content: str
    user_id: Optional[str] = None 
    session_id: Optional[str] = None
    age: int = 10
    language: str = "en"
    context: Optional[List] = None
    
    def __post_init__(self):
        """Validate parameters after initialization"""
        if not self.content or not isinstance(self.content, str):
            raise ValueError("Content must be a non-empty string")
        
        if self.age < 1 or self.age > 18:
            raise ValueError("Age must be between 1 and 18")
        
        if self.language not in ["en", "ar", "es", "fr", "de"]:
            warnings.warn(f"Language '{self.language}' may not be fully supported")


@dataclass
class ModerationMetadata:
    """Enhanced metadata parameter object for advanced use cases"""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    age: int = 10
    language: str = "en"
    context: Optional[List] = None
    strict_mode: bool = False
    cache_enabled: bool = True
    parent_supervision: bool = False
    
    def to_legacy_params(self, content: str) -> LegacyModerationParams:
        """Convert to LegacyModerationParams"""
        return LegacyModerationParams(
            content=content,
            user_id=self.user_id,
            session_id=self.session_id,
            age=self.age,
            language=self.language,
            context=self.context
        )


class LegacyModerationAdapter:
    """
    Adapter to maintain backward compatibility with old moderation interfaces.
    High cohesion: all methods handle legacy interface conversions.
    """
    
    def __init__(self, modern_service):
        """Initialize adapter with modern service reference"""
        self.modern_service = modern_service
        self.logger = logging.getLogger(__name__)
    
    async def check_content_legacy(
        self,
        params: Union[LegacyModerationParams, str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy interface for content checking.
        Converts old parameters to new format and delegates to modern service.
        """
        try:
            # Convert string to params if needed
            if isinstance(params, str):
                content = params
                legacy_params = LegacyModerationParams(
                    content=content,
                    user_id=kwargs.get("user_id"),
                    session_id=kwargs.get("session_id"),
                    age=kwargs.get("age", 10),
                    language=kwargs.get("language", "en"),
                    context=kwargs.get("context")
                )
            else:
                legacy_params = params
            
            # Convert to modern request format
            from .models import ModerationRequest, ModerationContext
            
            modern_request = ModerationRequest(
                content=legacy_params.content,
                user_id=legacy_params.user_id,
                session_id=legacy_params.session_id,
                age=legacy_params.age,
                language=legacy_params.language,
                context=legacy_params.context
            )
            
            modern_context = ModerationContext(
                use_cache=kwargs.get("use_cache", True),
                strict_mode=kwargs.get("strict_mode", False)
            )
            
            # Call modern service
            result = await self.modern_service.check_content(modern_request, modern_context)
            
            # Convert result to legacy format
            return self._convert_to_legacy_format(result)
            
        except Exception as e:
            self.logger.error(f"Legacy content check failed: {e}")
            return self._create_legacy_error_response(str(e))
    
    async def check_content_with_params(
        self,
        content: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        age: int = 10,
        language: str = "en",
        context: Optional[List] = None,
        strict_mode: bool = False,
        use_cache: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Legacy method with individual parameters.
        Converts to parameter object and delegates.
        """
        try:
            # Create parameter object
            params = LegacyModerationParams(
                content=content,
                user_id=user_id,
                session_id=session_id,
                age=age,
                language=language,
                context=context
            )
            
            # Add additional context
            kwargs.update({
                "strict_mode": strict_mode,
                "use_cache": use_cache
            })
            
            return await self.check_content_legacy(params, **kwargs)
            
        except Exception as e:
            self.logger.error(f"Legacy parameterized check failed: {e}")
            return self._create_legacy_error_response(str(e))
    
    async def moderate_content(self, text: str, user_context: dict = None) -> dict:
        """
        Very old legacy interface - converts to modern format.
        """
        warnings.warn(
            "moderate_content is deprecated. Use check_content_legacy instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        user_context = user_context or {}
        
        params = LegacyModerationParams(
            content=text,
            user_id=user_context.get("user_id"),
            session_id=user_context.get("session_id"),
            age=user_context.get("age", 10),
            language=user_context.get("language", "en")
        )
        
        result = await self.check_content_legacy(params)
        
        # Convert to very old format
        return {
            "safe": result["allowed"],
            "reason": result.get("reason", ""),
            "confidence": result.get("confidence", 0.9),
            "categories": result.get("categories", [])
        }
    
    async def check_content_safe(
        self,
        params: LegacyModerationParams
    ) -> Dict[str, Any]:
        """
        Safe mode legacy interface - enables strict checking.
        """
        result = await self.check_content_legacy(
            params,
            strict_mode=True,
            use_cache=False
        )
        
        # Add safe mode indicators
        result["safe_mode"] = True
        result["extra_validation"] = True
        
        return result
    
    async def check_content_enhanced(
        self,
        content: str,
        metadata: ModerationMetadata
    ) -> Dict[str, Any]:
        """
        Enhanced legacy interface with metadata object.
        """
        try:
            params = metadata.to_legacy_params(content)
            
            kwargs = {
                "strict_mode": metadata.strict_mode,
                "use_cache": metadata.cache_enabled
            }
            
            result = await self.check_content_legacy(params, **kwargs)
            
            # Add enhanced metadata to result
            result["metadata"] = {
                "parent_supervision": metadata.parent_supervision,
                "enhanced_mode": True,
                "processing_mode": "enhanced"
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Enhanced content check failed: {e}")
            return self._create_legacy_error_response(str(e))
    
    def create_legacy_params(
        self,
        content: str,
        metadata: Optional[Union[Dict[str, Any], ModerationMetadata]] = None
    ) -> LegacyModerationParams:
        """
        Helper to create legacy parameters from various inputs.
        """
        if metadata is None:
            metadata = {}
        
        if isinstance(metadata, dict):
            return LegacyModerationParams(
                content=content,
                user_id=metadata.get("user_id"),
                session_id=metadata.get("session_id"),
                age=metadata.get("age", 10),
                language=metadata.get("language", "en"),
                context=metadata.get("context")
            )
        elif isinstance(metadata, ModerationMetadata):
            return metadata.to_legacy_params(content)
        else:
            raise ValueError("Metadata must be dict or ModerationMetadata")
    
    def validate_parameters(
        self,
        params: LegacyModerationParams
    ) -> Dict[str, Any]:
        """
        Legacy parameter validation method.
        """
        try:
            # Validation is done in __post_init__, so if we get here, it's valid
            return {
                "valid": True,
                "errors": [],
                "warnings": [],
                "normalized_params": {
                    "content_length": len(params.content),
                    "language": params.language,
                    "age": params.age,
                    "has_user_id": params.user_id is not None,
                    "has_session_id": params.session_id is not None,
                    "has_context": params.context is not None
                }
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": [],
                "normalized_params": None
            }
    
    def _convert_to_legacy_format(self, modern_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert modern result format to legacy format"""
        return {
            "allowed": modern_result.get("allowed", True),
            "safe": modern_result.get("allowed", True),  # Legacy alias
            "severity": modern_result.get("severity", "safe"),
            "categories": modern_result.get("categories", []),
            "confidence": modern_result.get("confidence", 0.9),
            "reason": modern_result.get("reason", ""),
            "flagged_content": modern_result.get("categories", []),  # Legacy alias
            "risk_level": modern_result.get("severity", "safe"),  # Legacy alias
            "processing_time_ms": modern_result.get("processing_time_ms", 0),
            "timestamp": modern_result.get("timestamp", 0),
            "legacy_format": True,
            "api_version": "legacy_v1"
        }
    
    def _create_legacy_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create legacy-formatted error response"""
        return {
            "allowed": True,  # Fail safe - allow content on error
            "safe": True,
            "severity": "safe",
            "categories": [],
            "confidence": 0.0,
            "reason": f"Error during processing: {error_message}",
            "error": True,
            "error_message": error_message,
            "flagged_content": [],
            "risk_level": "unknown",
            "processing_time_ms": 0,
            "timestamp": 0,
            "legacy_format": True,
            "api_version": "legacy_v1"
        }
    
    def get_legacy_interface_info(self) -> Dict[str, Any]:
        """Get information about available legacy interfaces"""
        return {
            "available_methods": [
                "check_content_legacy",
                "check_content_with_params", 
                "moderate_content",
                "check_content_safe",
                "check_content_enhanced"
            ],
            "deprecated_methods": [
                "moderate_content"
            ],
            "parameter_objects": [
                "LegacyModerationParams",
                "ModerationMetadata"
            ],
            "compatibility_level": "full",
            "migration_guide": {
                "old_method": "moderate_content",
                "new_method": "check_content_legacy",
                "breaking_changes": "Response format updated for consistency"
            }
        } 