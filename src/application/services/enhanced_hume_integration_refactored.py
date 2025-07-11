"""
Enhanced_Hume_Integration Facade - Backward Compatibility
واجهة للحفاظ على التوافق مع النسخة السابقة

This file maintains backward compatibility while the actual implementation
has been split into smaller, more manageable components.

Generated by God Class Splitter
"""

# Import all components
from .enhanced_componentshume_componentsintegration import *

# Legacy class facade


class LanguageFacade:
    """Legacy facade for Language"""

    def __init__(self):
        self.language = Language()

    def __getattr__(self, name):
        return getattr(self.language, name)


# Alias for backward compatibility
Language = LanguageFacade


class AnalysisModeFacade:
    """Legacy facade for AnalysisMode"""

    def __init__(self):
        self.analysismode = AnalysisMode()

    def __getattr__(self, name):
        return getattr(self.analysismode, name)


# Alias for backward compatibility
AnalysisMode = AnalysisModeFacade


class EmotionCalibrationConfigFacade:
    """Legacy facade for EmotionCalibrationConfig"""

    def __init__(self):
        self.emotioncalibrationconfig = EmotionCalibrationConfig()

    def __getattr__(self, name):
        return getattr(self.emotioncalibrationconfig, name)


# Alias for backward compatibility
EmotionCalibrationConfig = EmotionCalibrationConfigFacade


class EmotionAnalysisResultFacade:
    """Legacy facade for EmotionAnalysisResult"""

    def __init__(self):
        self.emotionanalysisresult = EmotionAnalysisResult()

    def __getattr__(self, name):
        return getattr(self.emotionanalysisresult, name)


# Alias for backward compatibility
EmotionAnalysisResult = EmotionAnalysisResultFacade


class EnhancedHumeIntegrationCoreFacade:
    """Legacy facade for EnhancedHumeIntegrationCore"""

    def __init__(self):
        self.enhancedhumeintegrationcore = EnhancedHumeIntegrationCore()

    def __getattr__(self, name):
        return getattr(self.enhancedhumeintegrationcore, name)


# Alias for backward compatibility
EnhancedHumeIntegrationCore = EnhancedHumeIntegrationCoreFacade


class EnhancedHumeIntegrationUtilityFacade:
    """Legacy facade for EnhancedHumeIntegrationUtility"""

    def __init__(self):
        self.enhancedhumeintegrationutility = EnhancedHumeIntegrationUtility()

    def __getattr__(self, name):
        return getattr(self.enhancedhumeintegrationutility, name)


# Alias for backward compatibility
EnhancedHumeIntegrationUtility = EnhancedHumeIntegrationUtilityFacade
