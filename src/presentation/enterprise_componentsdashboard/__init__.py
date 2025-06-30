"""
Enterprise_Dashboard Components Package
مكونات منفصلة من enterprise_dashboard.py

تم إنشاؤها تلقائياً بواسطة God Class Splitter
"""

# Import all components for backward compatibility
from .emotionanalyticsenginecore import EmotionAnalyticsEngineCore
from .emotionanalyticsengineutility import EmotionAnalyticsEngineUtility
from .smartalertsystemcore import SmartAlertSystemCore
from .smartalertsystemprocessing import SmartAlertSystemProcessing
from .smartalertsystemnotification import SmartAlertSystemNotification
from .smartalertsystemutility import SmartAlertSystemUtility
from .enterprisedashboardwidgetcore import EnterpriseDashboardWidgetCore
from .enterprisedashboardwidgetprocessing import EnterpriseDashboardWidgetProcessing
from .enterprisedashboardwidgetnotification import EnterpriseDashboardWidgetNotification
from .enterprisedashboardwidgetutility import EnterpriseDashboardWidgetUtility

# Legacy compatibility
__all__ = [
    'EmotionAnalyticsEngineCore',
    'EmotionAnalyticsEngineUtility',
    'SmartAlertSystemCore',
    'SmartAlertSystemProcessing',
    'SmartAlertSystemNotification',
    'SmartAlertSystemUtility',
    'EnterpriseDashboardWidgetCore',
    'EnterpriseDashboardWidgetProcessing',
    'EnterpriseDashboardWidgetNotification',
    'EnterpriseDashboardWidgetUtility',
]
