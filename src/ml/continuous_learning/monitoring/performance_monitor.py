# ===================================================================
# 🧸 AI Teddy Bear - Performance Monitoring System
# Enterprise ML Performance Monitoring & Alerting
# ML Team Lead: Senior ML Engineer
# Date: January 2025
# ===================================================================

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """مستوى خطورة التنبيه"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """نوع المقياس"""
    PERFORMANCE = "performance"
    SAFETY = "safety"
    SATISFACTION = "satisfaction"
    TECHNICAL = "technical"
    BUSINESS = "business"


@dataclass
class PerformanceAlert:
    """تنبيه الأداء"""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    metric_name: str
    current_value: float
    threshold_value: float
    message: str
    affected_models: List[str]
    recommended_actions: List[str]
    auto_resolved: bool = False


@dataclass
class MetricSnapshot:
    """لقطة من المقاييس"""
    timestamp: datetime
    model_id: str
    metrics: Dict[str, float]
    health_score: float
    anomalies_detected: List[str]


class PerformanceMonitor:
    """مراقب الأداء الشامل"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_monitors: Dict[str, Dict[str, Any]] = {}
        self.metric_history: List[MetricSnapshot] = []
        self.active_alerts: List[PerformanceAlert] = []
        self.alert_rules = self._initialize_alert_rules()
        
        # إعداد النظم الفرعية
        self.metrics_collector = self._initialize_metrics_collector()
        self.anomaly_detector = self._initialize_anomaly_detector()
        self.alerting_system = self._initialize_alerting_system()
        
        logger.info("📊 Performance Monitor initialized")
    
    async def start_deployment_monitoring(self, deployment_id: str, 
                                        models: Dict[str, Any],
                                        monitoring_duration_hours: int = 48) -> None:
        """بدء مراقبة النشر"""
        
        logger.info(f"👁️ Starting deployment monitoring for {deployment_id}")
        
        # إعداد مراقبة للنشر
        monitoring_config = {
            'deployment_id': deployment_id,
            'models': models,
            'start_time': datetime.utcnow(),
            'duration_hours': monitoring_duration_hours,
            'check_interval_seconds': 60,
            'alert_thresholds': self._get_deployment_alert_thresholds(),
            'baseline_metrics': await self._establish_baseline_metrics(models)
        }
        
        # بدء مهمة المراقبة
        monitoring_task = asyncio.create_task(
            self._deployment_monitoring_loop(monitoring_config)
        )
        
        self.active_monitors[deployment_id] = {
            'config': monitoring_config,
            'task': monitoring_task,
            'status': 'active'
        }
    
    async def _deployment_monitoring_loop(self, config: Dict[str, Any]) -> None:
        """حلقة مراقبة النشر"""
        
        deployment_id = config['deployment_id']
        start_time = config['start_time']
        duration = timedelta(hours=config['duration_hours'])
        check_interval = config['check_interval_seconds']
        
        logger.info(f"🔄 Starting monitoring loop for {deployment_id}")
        
        while datetime.utcnow() - start_time < duration:
            try:
                # جمع المقاييس الحالية
                current_metrics = await self._collect_current_metrics(config['models'])
                
                # إنشاء لقطة من المقاييس
                for model_id, metrics in current_metrics.items():
                    snapshot = MetricSnapshot(
                        timestamp=datetime.utcnow(),
                        model_id=model_id,
                        metrics=metrics,
                        health_score=await self._calculate_health_score(metrics),
                        anomalies_detected=await self._detect_anomalies(model_id, metrics)
                    )
                    
                    self.metric_history.append(snapshot)
                    
                    # فحص التنبيهات
                    await self._check_alert_conditions(deployment_id, snapshot, config)
                
                # تنظيف البيانات القديمة
                await self._cleanup_old_metrics()
                
                # النوم حتى الفحص التالي
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop for {deployment_id}: {str(e)}")
                await asyncio.sleep(check_interval)
        
        # انتهاء المراقبة
        await self._finalize_deployment_monitoring(deployment_id)
        logger.info(f"✅ Monitoring completed for {deployment_id}")
    
    async def _collect_current_metrics(self, models: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """جمع المقاييس الحالية"""
        
        current_metrics = {}
        
        for model_id, model_data in models.items():
            # محاكاة جمع المقاييس من النماذج المنشورة
            metrics = await self._simulate_model_metrics(model_id, model_data)
            current_metrics[model_id] = metrics
        
        return current_metrics
    
    async def _simulate_model_metrics(self, model_id: str, model_data: Any) -> Dict[str, float]:
        """محاكاة مقاييس النموذج"""
        
        # محاكاة مقاييس واقعية مع اتجاهات وضوضاء
        base_metrics = {
            'safety_score': 0.96,
            'child_satisfaction': 0.83,
            'response_time_ms': 750,
            'accuracy': 0.87,
            'throughput_rps': 95,
            'error_rate': 0.008,
            'memory_usage_mb': 512,
            'cpu_usage_percent': 45,
            'engagement_rate': 0.79,
            'learning_effectiveness': 0.74,
            'parent_approval': 0.86
        }
        
        # إضافة ضوضاء واقعية
        current_metrics = {}
        for metric, base_value in base_metrics.items():
            if metric == 'response_time_ms':
                # وقت الاستجابة - توزيع جاما
                current_metrics[metric] = max(200, np.random.gamma(2, base_value/2))
            elif metric in ['error_rate']:
                # معدل الخطأ - توزيع أسي
                current_metrics[metric] = max(0.001, np.random.exponential(base_value))
            elif metric in ['throughput_rps']:
                # الإنتاجية - توزيع بواسون
                current_metrics[metric] = max(50, np.random.poisson(base_value))
            elif metric in ['memory_usage_mb']:
                # استخدام الذاكرة - توزيع طبيعي
                current_metrics[metric] = max(256, np.random.normal(base_value, base_value * 0.1))
            elif metric in ['cpu_usage_percent']:
                # استخدام المعالج - توزيع بيتا مقيس
                current_metrics[metric] = np.random.beta(3, 5) * 100
            else:
                # مقاييس الجودة - توزيع بيتا
                alpha = base_value * 20
                beta = (1 - base_value) * 20
                current_metrics[metric] = np.random.beta(alpha, beta)
        
        # إضافة اتجاهات زمنية طفيفة
        time_factor = (datetime.utcnow().minute % 60) / 60.0
        
        # تحسن طفيف مع الوقت لبعض المقاييس
        current_metrics['child_satisfaction'] *= (1 + time_factor * 0.02)
        current_metrics['accuracy'] *= (1 + time_factor * 0.01)
        
        # تدهور طفيف لمقاييس الموارد
        current_metrics['response_time_ms'] *= (1 + time_factor * 0.05)
        current_metrics['memory_usage_mb'] *= (1 + time_factor * 0.03)
        
        # تطبيق الحدود
        for metric in current_metrics:
            if metric not in ['response_time_ms', 'throughput_rps', 'memory_usage_mb', 'cpu_usage_percent']:
                current_metrics[metric] = max(0, min(1, current_metrics[metric]))
        
        return current_metrics
    
    async def _calculate_health_score(self, metrics: Dict[str, float]) -> float:
        """حساب درجة الصحة الإجمالية"""
        
        # أوزان المقاييس المختلفة
        weights = {
            'safety_score': 0.25,
            'child_satisfaction': 0.20,
            'accuracy': 0.15,
            'parent_approval': 0.15,
            'response_time_ms': 0.10,  # معكوس
            'error_rate': 0.10,        # معكوس
            'engagement_rate': 0.05
        }
        
        weighted_score = 0
        total_weight = 0
        
        for metric, weight in weights.items():
            if metric in metrics:
                value = metrics[metric]
                
                # تطبيع المقاييس المعكوسة
                if metric == 'response_time_ms':
                    # تحويل وقت الاستجابة إلى درجة (أقل = أفضل)
                    normalized_value = max(0, 1 - (value - 500) / 1500)  # 500-2000ms range
                elif metric == 'error_rate':
                    # تحويل معدل الخطأ إلى درجة (أقل = أفضل)
                    normalized_value = max(0, 1 - value / 0.1)  # 0-10% range
                else:
                    normalized_value = value
                
                weighted_score += normalized_value * weight
                total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.5
    
    async def _detect_anomalies(self, model_id: str, metrics: Dict[str, float]) -> List[str]:
        """كشف الشذوذ في المقاييس"""
        
        anomalies = []
        
        # الحصول على البيانات التاريخية للنموذج
        historical_data = [
            snapshot for snapshot in self.metric_history[-100:]  # آخر 100 قياس
            if snapshot.model_id == model_id
        ]
        
        if len(historical_data) < 10:
            return anomalies  # بيانات غير كافية
        
        # فحص كل مقياس للشذوذ
        for metric_name, current_value in metrics.items():
            historical_values = [
                snapshot.metrics.get(metric_name, 0) 
                for snapshot in historical_data
            ]
            
            if len(historical_values) >= 10:
                mean_value = np.mean(historical_values)
                std_value = np.std(historical_values)
                
                # كشف الشذوذ باستخدام قاعدة 3-sigma
                if std_value > 0:
                    z_score = abs(current_value - mean_value) / std_value
                    
                    if z_score > 3:
                        anomalies.append(f"{metric_name}_anomaly")
                        logger.warning(f"🚨 Anomaly detected in {model_id}.{metric_name}: {current_value:.3f} (z-score: {z_score:.2f})")
                
                # فحص الاتجاهات المفاجئة
                if len(historical_values) >= 20:
                    recent_values = historical_values[-10:]
                    older_values = historical_values[-20:-10]
                    
                    recent_mean = np.mean(recent_values)
                    older_mean = np.mean(older_values)
                    
                    if older_mean > 0:
                        change_percentage = abs(recent_mean - older_mean) / older_mean
                        
                        if change_percentage > 0.2:  # تغيير أكثر من 20%
                            anomalies.append(f"{metric_name}_trend_change")
                            logger.info(f"📈 Trend change detected in {model_id}.{metric_name}: {change_percentage:.1%}")
        
        return anomalies
    
    async def _check_alert_conditions(self, deployment_id: str, 
                                    snapshot: MetricSnapshot,
                                    config: Dict[str, Any]) -> None:
        """فحص شروط التنبيه"""
        
        alert_thresholds = config['alert_thresholds']
        
        for rule_name, rule_config in self.alert_rules.items():
            if await self._evaluate_alert_rule(rule_name, rule_config, snapshot, alert_thresholds):
                await self._trigger_alert(deployment_id, rule_name, rule_config, snapshot)
    
    async def _evaluate_alert_rule(self, rule_name: str, 
                                 rule_config: Dict[str, Any],
                                 snapshot: MetricSnapshot,
                                 thresholds: Dict[str, float]) -> bool:
        """تقييم قاعدة التنبيه"""
        
        metric_name = rule_config['metric']
        condition = rule_config['condition']
        threshold = thresholds.get(metric_name, rule_config.get('default_threshold', 0))
        
        current_value = snapshot.metrics.get(metric_name, 0)
        
        # تقييم الشرط
        if condition == 'less_than':
            return current_value < threshold
        elif condition == 'greater_than':
            return current_value > threshold
        elif condition == 'equals':
            return abs(current_value - threshold) < 0.001
        elif condition == 'anomaly':
            return metric_name + '_anomaly' in snapshot.anomalies_detected
        
        return False
    
    async def _trigger_alert(self, deployment_id: str, 
                           rule_name: str,
                           rule_config: Dict[str, Any],
                           snapshot: MetricSnapshot) -> None:
        """تشغيل التنبيه"""
        
        # فحص ما إذا كان التنبيه مكرر
        existing_alert = self._find_existing_alert(rule_name, snapshot.model_id)
        if existing_alert and not existing_alert.auto_resolved:
            return  # تجنب التنبيهات المكررة
        
        # إنشاء تنبيه جديد
        alert = PerformanceAlert(
            alert_id=f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{rule_name}",
            timestamp=datetime.utcnow(),
            severity=AlertSeverity(rule_config['severity']),
            metric_name=rule_config['metric'],
            current_value=snapshot.metrics.get(rule_config['metric'], 0),
            threshold_value=rule_config.get('default_threshold', 0),
            message=rule_config['message'].format(
                model_id=snapshot.model_id,
                current_value=snapshot.metrics.get(rule_config['metric'], 0),
                threshold=rule_config.get('default_threshold', 0)
            ),
            affected_models=[snapshot.model_id],
            recommended_actions=rule_config.get('actions', [])
        )
        
        self.active_alerts.append(alert)
        
        # إرسال التنبيه
        await self._send_alert(deployment_id, alert)
        
        # محاولة الحل التلقائي
        if rule_config.get('auto_resolve', False):
            await self._attempt_auto_resolution(alert, snapshot)
    
    def _find_existing_alert(self, rule_name: str, model_id: str) -> Optional[PerformanceAlert]:
        """البحث عن تنبيه موجود"""
        
        for alert in self.active_alerts:
            if (rule_name in alert.alert_id and 
                model_id in alert.affected_models and 
                not alert.auto_resolved):
                return alert
        
        return None
    
    async def _send_alert(self, deployment_id: str, alert: PerformanceAlert) -> None:
        """إرسال التنبيه"""
        
        severity_emoji = {
            AlertSeverity.LOW: "🟡",
            AlertSeverity.MEDIUM: "🟠", 
            AlertSeverity.HIGH: "🔴",
            AlertSeverity.CRITICAL: "🚨"
        }
        
        logger.warning(f"{severity_emoji[alert.severity]} ALERT [{alert.severity.value.upper()}] "
                      f"Deployment: {deployment_id} | {alert.message}")
        
        # في بيئة الإنتاج، سيتم إرسال التنبيهات عبر:
        # - Slack/Teams
        # - Email
        # - PagerDuty
        # - SMS للتنبيهات الحرجة
        
        # محاكاة إرسال التنبيه
        await self._notify_stakeholders(deployment_id, alert)
    
    async def _notify_stakeholders(self, deployment_id: str, alert: PerformanceAlert) -> None:
        """إشعار أصحاب المصلحة"""
        
        notification_channels = []
        
        if alert.severity == AlertSeverity.CRITICAL:
            notification_channels = ['email', 'sms', 'pagerduty', 'slack']
        elif alert.severity == AlertSeverity.HIGH:
            notification_channels = ['email', 'slack']
        else:
            notification_channels = ['slack']
        
        logger.info(f"📢 Notifying stakeholders via {notification_channels} for alert {alert.alert_id}")
    
    async def _attempt_auto_resolution(self, alert: PerformanceAlert, snapshot: MetricSnapshot) -> None:
        """محاولة الحل التلقائي"""
        
        resolved = False
        
        # محاولات الحل التلقائي حسب نوع المشكلة
        if 'response_time' in alert.metric_name:
            resolved = await self._auto_resolve_response_time_issue(alert, snapshot)
        elif 'memory' in alert.metric_name:
            resolved = await self._auto_resolve_memory_issue(alert, snapshot)
        elif 'error_rate' in alert.metric_name:
            resolved = await self._auto_resolve_error_rate_issue(alert, snapshot)
        
        if resolved:
            alert.auto_resolved = True
            logger.info(f"✅ Auto-resolved alert {alert.alert_id}")
    
    async def _auto_resolve_response_time_issue(self, alert: PerformanceAlert, snapshot: MetricSnapshot) -> bool:
        """حل مشكلة وقت الاستجابة تلقائياً"""
        
        # محاولة تحسين الأداء
        logger.info(f"🔧 Attempting auto-resolution for response time issue in {snapshot.model_id}")
        
        # في بيئة الإنتاج:
        # - زيادة موارد الحوسبة
        # - تحسين التخزين المؤقت
        # - توزيع الأحمال
        
        return np.random.choice([True, False], p=[0.7, 0.3])  # محاكاة نجاح 70%
    
    async def _auto_resolve_memory_issue(self, alert: PerformanceAlert, snapshot: MetricSnapshot) -> bool:
        """حل مشكلة الذاكرة تلقائياً"""
        
        logger.info(f"🔧 Attempting auto-resolution for memory issue in {snapshot.model_id}")
        
        # في بيئة الإنتاج:
        # - تنظيف الذاكرة
        # - إعادة تشغيل الخدمة
        # - زيادة حدود الذاكرة
        
        return np.random.choice([True, False], p=[0.6, 0.4])  # محاكاة نجاح 60%
    
    async def _auto_resolve_error_rate_issue(self, alert: PerformanceAlert, snapshot: MetricSnapshot) -> bool:
        """حل مشكلة معدل الخطأ تلقائياً"""
        
        logger.info(f"🔧 Attempting auto-resolution for error rate issue in {snapshot.model_id}")
        
        # في بيئة الإنتاج:
        # - إعادة تشغيل الخدمات المعطلة
        # - تحديث إعدادات الشبكة
        # - تصحيح مشاكل الاتصال
        
        return np.random.choice([True, False], p=[0.5, 0.5])  # محاكاة نجاح 50%
    
    async def _establish_baseline_metrics(self, models: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        """إنشاء مقاييس أساسية"""
        
        baseline_metrics = {}
        
        for model_id, model_data in models.items():
            # استخدام المقاييس من التدريب كأساس
            if hasattr(model_data, 'final_metrics'):
                baseline_metrics[model_id] = model_data.final_metrics
            else:
                # مقاييس افتراضية
                baseline_metrics[model_id] = {
                    'safety_score': 0.95,
                    'child_satisfaction': 0.80,
                    'accuracy': 0.85,
                    'response_time_ms': 1000,
                    'error_rate': 0.01
                }
        
        return baseline_metrics
    
    def _get_deployment_alert_thresholds(self) -> Dict[str, float]:
        """الحصول على عتبات تنبيه النشر"""
        
        return {
            'safety_score': 0.95,
            'child_satisfaction': 0.75,
            'accuracy': 0.80,
            'response_time_ms': 2000,
            'error_rate': 0.02,
            'memory_usage_mb': 1024,
            'cpu_usage_percent': 80,
            'throughput_rps': 50
        }
    
    def _initialize_alert_rules(self) -> Dict[str, Dict[str, Any]]:
        """تهيئة قواعد التنبيه"""
        
        return {
            'safety_score_critical': {
                'metric': 'safety_score',
                'condition': 'less_than',
                'default_threshold': 0.95,
                'severity': 'critical',
                'message': 'CRITICAL: Safety score for {model_id} dropped to {current_value:.3f} (threshold: {threshold})',
                'actions': ['immediate_rollback', 'escalate_to_safety_team'],
                'auto_resolve': False
            },
            'child_satisfaction_low': {
                'metric': 'child_satisfaction',
                'condition': 'less_than',
                'default_threshold': 0.75,
                'severity': 'high',
                'message': 'Child satisfaction for {model_id} is low: {current_value:.3f} (threshold: {threshold})',
                'actions': ['review_conversation_quality', 'check_personalization'],
                'auto_resolve': False
            },
            'response_time_high': {
                'metric': 'response_time_ms',
                'condition': 'greater_than',
                'default_threshold': 2000,
                'severity': 'medium',
                'message': 'Response time for {model_id} is high: {current_value:.0f}ms (threshold: {threshold}ms)',
                'actions': ['scale_up_resources', 'optimize_model'],
                'auto_resolve': True
            },
            'error_rate_high': {
                'metric': 'error_rate',
                'condition': 'greater_than',
                'default_threshold': 0.02,
                'severity': 'high',
                'message': 'Error rate for {model_id} is high: {current_value:.3f} (threshold: {threshold})',
                'actions': ['check_model_health', 'review_recent_changes'],
                'auto_resolve': True
            },
            'memory_usage_high': {
                'metric': 'memory_usage_mb',
                'condition': 'greater_than',
                'default_threshold': 1024,
                'severity': 'medium',
                'message': 'Memory usage for {model_id} is high: {current_value:.0f}MB (threshold: {threshold}MB)',
                'actions': ['increase_memory_limits', 'optimize_memory_usage'],
                'auto_resolve': True
            },
            'anomaly_detected': {
                'metric': 'any',
                'condition': 'anomaly',
                'default_threshold': 0,
                'severity': 'medium',
                'message': 'Anomaly detected in {model_id} metrics',
                'actions': ['investigate_anomaly', 'compare_with_baseline'],
                'auto_resolve': False
            }
        }
    
    def _initialize_metrics_collector(self) -> Dict[str, Any]:
        """تهيئة جامع المقاييس"""
        return {
            'collection_interval_seconds': 60,
            'metrics_retention_hours': 168,  # أسبوع
            'aggregation_enabled': True
        }
    
    def _initialize_anomaly_detector(self) -> Dict[str, Any]:
        """تهيئة كاشف الشذوذ"""
        return {
            'algorithm': 'statistical',
            'sensitivity': 0.95,
            'min_data_points': 10
        }
    
    def _initialize_alerting_system(self) -> Dict[str, Any]:
        """تهيئة نظام التنبيه"""
        return {
            'channels': ['slack', 'email', 'pagerduty'],
            'rate_limiting': True,
            'escalation_enabled': True
        }
    
    async def _cleanup_old_metrics(self) -> None:
        """تنظيف المقاييس القديمة"""
        
        # الاحتفاظ بآخر 1000 قياس فقط
        if len(self.metric_history) > 1000:
            self.metric_history = self.metric_history[-1000:]
        
        # إزالة التنبيهات القديمة المحلولة
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.active_alerts = [
            alert for alert in self.active_alerts
            if alert.timestamp > cutoff_time or not alert.auto_resolved
        ]
    
    async def _finalize_deployment_monitoring(self, deployment_id: str) -> None:
        """إنهاء مراقبة النشر"""
        
        if deployment_id in self.active_monitors:
            monitor_info = self.active_monitors[deployment_id]
            monitor_info['status'] = 'completed'
            monitor_info['end_time'] = datetime.utcnow()
            
            # إنشاء تقرير نهائي
            final_report = await self._generate_monitoring_report(deployment_id)
            logger.info(f"📊 Generated final monitoring report for {deployment_id}")
            
            # تنظيف الموارد
            del self.active_monitors[deployment_id]
    
    async def _generate_monitoring_report(self, deployment_id: str) -> Dict[str, Any]:
        """إنشاء تقرير المراقبة"""
        
        monitor_info = self.active_monitors.get(deployment_id, {})
        config = monitor_info.get('config', {})
        
        # جمع إحصائيات المراقبة
        monitoring_stats = {
            'deployment_id': deployment_id,
            'monitoring_duration_hours': config.get('duration_hours', 0),
            'total_metrics_collected': len([
                snapshot for snapshot in self.metric_history
                if any(model_id in snapshot.model_id for model_id in config.get('models', {}).keys())
            ]),
            'alerts_triggered': len([
                alert for alert in self.active_alerts
                if deployment_id in alert.alert_id
            ]),
            'anomalies_detected': sum(
                len(snapshot.anomalies_detected) for snapshot in self.metric_history
                if any(model_id in snapshot.model_id for model_id in config.get('models', {}).keys())
            ),
            'auto_resolutions': len([
                alert for alert in self.active_alerts
                if deployment_id in alert.alert_id and alert.auto_resolved
            ])
        }
        
        return monitoring_stats 