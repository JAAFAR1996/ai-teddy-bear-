"""
Enterprise_Dashboard Components Package
مكونات منفصلة من enterprise_dashboard.py

تم إنشاؤها تلقائياً بواسطة God Class Splitter
"""

# Import all components for backward compatibility
from .emotionanalyticsenginecore import EmotionAnalyticsEngineCore
from .emotionanalyticsengineutility import EmotionAnalyticsEngineUtility
from .enterprisedashboardwidgetcore import EnterpriseDashboardWidgetCore
from .enterprisedashboardwidgetnotification import EnterpriseDashboardWidgetNotification
from .enterprisedashboardwidgetprocessing import EnterpriseDashboardWidgetProcessing
from .enterprisedashboardwidgetutility import EnterpriseDashboardWidgetUtility
from .smartalertsystemcore import SmartAlertSystemCore
from .smartalertsystemnotification import SmartAlertSystemNotification
from .smartalertsystemprocessing import SmartAlertSystemProcessing
from .smartalertsystemutility import SmartAlertSystemUtility

# Legacy compatibility
__all__ = [
    "EmotionAnalyticsEngineCore",
    "EmotionAnalyticsEngineUtility",
    "SmartAlertSystemCore",
    "SmartAlertSystemProcessing",
    "SmartAlertSystemNotification",
    "SmartAlertSystemUtility",
    "EnterpriseDashboardWidgetCore",
    "EnterpriseDashboardWidgetProcessing",
    "EnterpriseDashboardWidgetNotification",
    "EnterpriseDashboardWidgetUtility",
]
