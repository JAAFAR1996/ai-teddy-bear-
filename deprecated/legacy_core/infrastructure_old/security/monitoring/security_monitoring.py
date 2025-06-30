"""
🔍 Security Monitoring System
=============================

Real-time security monitoring and incident response for Zero Trust architecture.
Provides threat detection, alerting, and security analytics dashboard.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import statistics

from ..zero_trust.zero_trust_manager import SecurityContext, SecurityEvent, ThreatLevel

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringMetric(Enum):
    """Security monitoring metrics"""
    AUTHENTICATION_FAILURES = "auth_failures"
    AUTHORIZATION_DENIALS = "authz_denials"
    THREAT_DETECTIONS = "threat_detections"
    POLICY_VIOLATIONS = "policy_violations"
    SUSPICIOUS_ACTIVITIES = "suspicious_activities"
    NETWORK_ANOMALIES = "network_anomalies"
    DATA_ACCESS_PATTERNS = "data_access_patterns"


@dataclass
class SecurityAlert:
    """Security alert information"""
    alert_id: str
    title: str
    description: str
    severity: AlertSeverity
    source: str
    affected_resources: List[str]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class SecurityMetric:
    """Security metric data point"""
    metric_name: str
    value: float
    timestamp: datetime = field(default_factory=datetime.utcnow)
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class IncidentReport:
    """Security incident report"""
    incident_id: str
    title: str
    description: str
    severity: AlertSeverity
    start_time: datetime
    end_time: Optional[datetime] = None
    affected_users: Set[str] = field(default_factory=set)
    affected_systems: Set[str] = field(default_factory=set)
    root_cause: Optional[str] = None
    remediation_actions: List[str] = field(default_factory=list)
    status: str = "open"


class SecurityMetricsCollector:
    """Collects and aggregates security metrics"""
    
    def __init__(self):
        self.metrics: Dict[str, List[SecurityMetric]] = {}
        self.metric_collectors: Dict[MonitoringMetric, Callable] = {
            MonitoringMetric.AUTHENTICATION_FAILURES: self._collect_auth_failures,
            MonitoringMetric.AUTHORIZATION_DENIALS: self._collect_authz_denials,
            MonitoringMetric.THREAT_DETECTIONS: self._collect_threat_detections,
            MonitoringMetric.POLICY_VIOLATIONS: self._collect_policy_violations,
            MonitoringMetric.SUSPICIOUS_ACTIVITIES: self._collect_suspicious_activities
        }
        self.collection_interval = 60  # seconds
    
    async def start_collection(self) -> None:
        """Start metric collection"""
        
        while True:
            for metric_type, collector in self.metric_collectors.items():
                try:
                    metrics = await collector()
                    await self._store_metrics(metric_type.value, metrics)
                except Exception as e:
                    logger.error(f"Error collecting {metric_type.value}: {e}")
            
            await asyncio.sleep(self.collection_interval)
    
    async def get_metrics(
        self, 
        metric_name: str,
        time_range: timedelta = timedelta(hours=1)
    ) -> List[SecurityMetric]:
        """Get metrics for specified time range"""
        
        cutoff_time = datetime.utcnow() - time_range
        metrics = self.metrics.get(metric_name, [])
        
        return [m for m in metrics if m.timestamp > cutoff_time]
    
    async def get_metric_summary(
        self, 
        metric_name: str,
        time_range: timedelta = timedelta(hours=1)
    ) -> Dict[str, float]:
        """Get metric summary statistics"""
        
        metrics = await self.get_metrics(metric_name, time_range)
        values = [m.value for m in metrics]
        
        if not values:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}
        
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": statistics.mean(values),
            "min": min(values),
            "max": max(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0
        }
    
    async def _store_metrics(self, metric_name: str, metrics: List[SecurityMetric]) -> None:
        """Store metrics with retention policy"""
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = []
        
        self.metrics[metric_name].extend(metrics)
        
        # Retention policy: keep only last 24 hours
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        self.metrics[metric_name] = [
            m for m in self.metrics[metric_name] 
            if m.timestamp > cutoff_time
        ]
    
    async def _collect_auth_failures(self) -> List[SecurityMetric]:
        """Collect authentication failure metrics"""
        # Placeholder - implement actual collection from security events
        return [SecurityMetric(
            metric_name="auth_failures",
            value=5.0,  # Mock value
            labels={"source": "login_service"}
        )]
    
    async def _collect_authz_denials(self) -> List[SecurityMetric]:
        """Collect authorization denial metrics"""
        return [SecurityMetric(
            metric_name="authz_denials",
            value=2.0,
            labels={"resource": "child_data"}
        )]
    
    async def _collect_threat_detections(self) -> List[SecurityMetric]:
        """Collect threat detection metrics"""
        return [SecurityMetric(
            metric_name="threat_detections",
            value=1.0,
            labels={"severity": "high"}
        )]
    
    async def _collect_policy_violations(self) -> List[SecurityMetric]:
        """Collect policy violation metrics"""
        return [SecurityMetric(
            metric_name="policy_violations",
            value=3.0,
            labels={"policy_type": "data_protection"}
        )]
    
    async def _collect_suspicious_activities(self) -> List[SecurityMetric]:
        """Collect suspicious activity metrics"""
        return [SecurityMetric(
            metric_name="suspicious_activities",
            value=7.0,
            labels={"activity_type": "unusual_access"}
        )]


class ThreatDetectionEngine:
    """Advanced threat detection engine"""
    
    def __init__(self):
        self.detection_rules = {
            'brute_force': self._detect_brute_force,
            'credential_stuffing': self._detect_credential_stuffing,
            'privilege_escalation': self._detect_privilege_escalation,
            'data_exfiltration': self._detect_data_exfiltration,
            'anomalous_behavior': self._detect_anomalous_behavior
        }
        self.baseline_behaviors: Dict[str, Dict[str, Any]] = {}
        self.active_threats: Dict[str, SecurityEvent] = {}
    
    async def analyze_behavior(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> List[SecurityEvent]:
        """Analyze user behavior for threats"""
        
        threats = []
        
        # Run all detection rules
        for rule_name, detector in self.detection_rules.items():
            try:
                threat = await detector(context, request_data)
                if threat:
                    threats.append(threat)
            except Exception as e:
                logger.error(f"Error in threat detection rule {rule_name}: {e}")
        
        # Update baseline behavior
        await self._update_baseline(context, request_data)
        
        return threats
    
    async def _detect_brute_force(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> Optional[SecurityEvent]:
        """Detect brute force attacks"""
        
        # Check for repeated failed attempts
        user_id = context.user_id
        
        # This would typically check against stored authentication logs
        # For demo purposes, we'll use a simple check
        if request_data.get('action') == 'login' and request_data.get('failed', False):
            return SecurityEvent(
                event_id=f"bf_{user_id}_{datetime.utcnow().timestamp()}",
                event_type="brute_force_detected",
                severity=ThreatLevel.HIGH,
                source=user_id,
                target="login_system",
                description="Potential brute force attack detected",
                metadata={
                    'ip_address': context.ip_address,
                    'user_agent': request_data.get('user_agent'),
                    'attempt_count': request_data.get('attempt_count', 1)
                }
            )
        
        return None
    
    async def _detect_credential_stuffing(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> Optional[SecurityEvent]:
        """Detect credential stuffing attacks"""
        
        # Check for logins from multiple IPs for same user
        if context.ip_address and request_data.get('action') == 'login':
            # This would check against IP history for the user
            # Simplified detection logic
            return None
        
        return None
    
    async def _detect_privilege_escalation(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> Optional[SecurityEvent]:
        """Detect privilege escalation attempts"""
        
        # Check for requests to resources above user's typical access level
        requested_resource = request_data.get('resource', '')
        
        if 'admin' in requested_resource and context.role != 'admin':
            return SecurityEvent(
                event_id=f"pe_{context.user_id}_{datetime.utcnow().timestamp()}",
                event_type="privilege_escalation_attempt",
                severity=ThreatLevel.CRITICAL,
                source=context.user_id,
                target=requested_resource,
                description="Privilege escalation attempt detected",
                metadata={
                    'user_role': context.role,
                    'requested_resource': requested_resource,
                    'ip_address': context.ip_address
                }
            )
        
        return None
    
    async def _detect_data_exfiltration(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> Optional[SecurityEvent]:
        """Detect data exfiltration attempts"""
        
        # Check for large data requests or unusual export patterns
        data_size = request_data.get('data_size', 0)
        
        if data_size > 1000000:  # 1MB threshold
            return SecurityEvent(
                event_id=f"de_{context.user_id}_{datetime.utcnow().timestamp()}",
                event_type="data_exfiltration_attempt",
                severity=ThreatLevel.HIGH,
                source=context.user_id,
                target="data_service",
                description="Large data request detected",
                metadata={
                    'data_size': data_size,
                    'resource': request_data.get('resource'),
                    'export_format': request_data.get('format')
                }
            )
        
        return None
    
    async def _detect_anomalous_behavior(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> Optional[SecurityEvent]:
        """Detect anomalous user behavior"""
        
        user_id = context.user_id
        baseline = self.baseline_behaviors.get(user_id, {})
        
        # Check time-based anomalies
        current_hour = datetime.utcnow().hour
        typical_hours = baseline.get('typical_hours', set())
        
        if typical_hours and current_hour not in typical_hours:
            return SecurityEvent(
                event_id=f"ab_{user_id}_{datetime.utcnow().timestamp()}",
                event_type="anomalous_behavior",
                severity=ThreatLevel.MEDIUM,
                source=user_id,
                target="user_behavior",
                description="User accessing system at unusual time",
                metadata={
                    'current_hour': current_hour,
                    'typical_hours': list(typical_hours),
                    'deviation_score': 0.8
                }
            )
        
        return None
    
    async def _update_baseline(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> None:
        """Update user behavior baseline"""
        
        user_id = context.user_id
        
        if user_id not in self.baseline_behaviors:
            self.baseline_behaviors[user_id] = {
                'typical_hours': set(),
                'common_resources': set(),
                'access_patterns': []
            }
        
        baseline = self.baseline_behaviors[user_id]
        
        # Update typical access hours
        current_hour = datetime.utcnow().hour
        baseline['typical_hours'].add(current_hour)
        
        # Update common resources
        resource = request_data.get('resource')
        if resource:
            baseline['common_resources'].add(resource)
        
        # Keep baseline size manageable
        if len(baseline['typical_hours']) > 24:
            baseline['typical_hours'] = set(list(baseline['typical_hours'])[-12:])


class SecurityAlertManager:
    """Manages security alerts and incidents"""
    
    def __init__(self):
        self.alerts: Dict[str, SecurityAlert] = {}
        self.incidents: Dict[str, IncidentReport] = {}
        self.alert_handlers: Dict[AlertSeverity, Callable] = {
            AlertSeverity.INFO: self._handle_info_alert,
            AlertSeverity.WARNING: self._handle_warning_alert,
            AlertSeverity.ERROR: self._handle_error_alert,
            AlertSeverity.CRITICAL: self._handle_critical_alert
        }
        self.notification_channels = []
    
    async def create_alert(
        self, 
        title: str,
        description: str,
        severity: AlertSeverity,
        source: str,
        affected_resources: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> SecurityAlert:
        """Create new security alert"""
        
        alert = SecurityAlert(
            alert_id=f"alert_{datetime.utcnow().timestamp()}",
            title=title,
            description=description,
            severity=severity,
            source=source,
            affected_resources=affected_resources,
            metadata=metadata or {}
        )
        
        self.alerts[alert.alert_id] = alert
        
        # Handle alert based on severity
        await self.alert_handlers[severity](alert)
        
        logger.info(f"Security alert created: {alert.title} ({severity.value})")
        
        return alert
    
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge security alert"""
        
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            self.alerts[alert_id].metadata['acknowledged_by'] = user_id
            self.alerts[alert_id].metadata['acknowledged_at'] = datetime.utcnow()
            
            logger.info(f"Alert acknowledged: {alert_id} by {user_id}")
            return True
        
        return False
    
    async def resolve_alert(self, alert_id: str, user_id: str, resolution: str) -> bool:
        """Resolve security alert"""
        
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            self.alerts[alert_id].metadata['resolved_by'] = user_id
            self.alerts[alert_id].metadata['resolved_at'] = datetime.utcnow()
            self.alerts[alert_id].metadata['resolution'] = resolution
            
            logger.info(f"Alert resolved: {alert_id} by {user_id}")
            return True
        
        return False
    
    async def create_incident(
        self, 
        title: str,
        description: str,
        severity: AlertSeverity,
        affected_users: Set[str],
        affected_systems: Set[str]
    ) -> IncidentReport:
        """Create security incident"""
        
        incident = IncidentReport(
            incident_id=f"inc_{datetime.utcnow().timestamp()}",
            title=title,
            description=description,
            severity=severity,
            start_time=datetime.utcnow(),
            affected_users=affected_users,
            affected_systems=affected_systems
        )
        
        self.incidents[incident.incident_id] = incident
        
        logger.critical(f"Security incident created: {incident.title}")
        
        # Automatically escalate critical incidents
        if severity == AlertSeverity.CRITICAL:
            await self._escalate_incident(incident)
        
        return incident
    
    async def _handle_info_alert(self, alert: SecurityAlert) -> None:
        """Handle info-level alert"""
        # Log for audit purposes
        logger.info(f"Info alert: {alert.title}")
    
    async def _handle_warning_alert(self, alert: SecurityAlert) -> None:
        """Handle warning-level alert"""
        # Send to monitoring dashboard
        logger.warning(f"Warning alert: {alert.title}")
    
    async def _handle_error_alert(self, alert: SecurityAlert) -> None:
        """Handle error-level alert"""
        # Notify security team
        logger.error(f"Error alert: {alert.title}")
        await self._send_notification(alert)
    
    async def _handle_critical_alert(self, alert: SecurityAlert) -> None:
        """Handle critical-level alert"""
        # Immediate escalation
        logger.critical(f"Critical alert: {alert.title}")
        await self._send_notification(alert)
        
        # Auto-create incident for critical alerts
        await self.create_incident(
            title=f"Critical Security Alert: {alert.title}",
            description=alert.description,
            severity=AlertSeverity.CRITICAL,
            affected_users={alert.source},
            affected_systems=set(alert.affected_resources)
        )
    
    async def _escalate_incident(self, incident: IncidentReport) -> None:
        """Escalate critical incident"""
        logger.critical(f"Escalating incident: {incident.title}")
        # Implement escalation logic (notify executives, etc.)
    
    async def _send_notification(self, alert: SecurityAlert) -> None:
        """Send alert notification"""
        # Implement notification logic (email, Slack, PagerDuty, etc.)
        logger.info(f"Sending notification for alert: {alert.title}")


class SecurityMonitoringDashboard:
    """Security monitoring dashboard and analytics"""
    
    def __init__(self):
        self.metrics_collector = SecurityMetricsCollector()
        self.threat_engine = ThreatDetectionEngine()
        self.alert_manager = SecurityAlertManager()
        self.dashboard_data: Dict[str, Any] = {}
    
    async def start_monitoring(self) -> None:
        """Start security monitoring"""
        
        # Start metrics collection
        asyncio.create_task(self.metrics_collector.start_collection())
        
        logger.info("Security monitoring started")
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        
        # Security metrics summary
        metrics_summary = {}
        for metric in MonitoringMetric:
            summary = await self.metrics_collector.get_metric_summary(metric.value)
            metrics_summary[metric.value] = summary
        
        # Active alerts
        active_alerts = [
            alert for alert in self.alert_manager.alerts.values()
            if not alert.resolved
        ]
        
        # Recent incidents
        recent_incidents = [
            incident for incident in self.alert_manager.incidents.values()
            if incident.start_time > datetime.utcnow() - timedelta(days=7)
        ]
        
        # Threat level distribution
        threat_distribution = {}
        for level in ThreatLevel:
            count = len([
                alert for alert in active_alerts
                if alert.severity.value == level.value
            ])
            threat_distribution[level.value] = count
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'metrics_summary': metrics_summary,
            'active_alerts': len(active_alerts),
            'recent_incidents': len(recent_incidents),
            'threat_distribution': threat_distribution,
            'system_status': 'operational',  # Can be made dynamic
            'alerts': [
                {
                    'id': alert.alert_id,
                    'title': alert.title,
                    'severity': alert.severity.value,
                    'timestamp': alert.timestamp.isoformat(),
                    'acknowledged': alert.acknowledged
                }
                for alert in active_alerts[-10:]  # Latest 10 alerts
            ]
        }
    
    async def analyze_security_trends(self, days: int = 7) -> Dict[str, Any]:
        """Analyze security trends over time"""
        
        time_range = timedelta(days=days)
        
        # Collect trend data for each metric
        trends = {}
        for metric in MonitoringMetric:
            metrics = await self.metrics_collector.get_metrics(metric.value, time_range)
            
            # Group by day
            daily_counts = {}
            for m in metrics:
                day_key = m.timestamp.date().isoformat()
                daily_counts[day_key] = daily_counts.get(day_key, 0) + m.value
            
            trends[metric.value] = daily_counts
        
        # Alert trends
        alert_trends = {}
        for alert in self.alert_manager.alerts.values():
            if alert.timestamp > datetime.utcnow() - time_range:
                day_key = alert.timestamp.date().isoformat()
                severity = alert.severity.value
                
                if day_key not in alert_trends:
                    alert_trends[day_key] = {}
                
                alert_trends[day_key][severity] = alert_trends[day_key].get(severity, 0) + 1
        
        return {
            'period': f"{days} days",
            'metric_trends': trends,
            'alert_trends': alert_trends,
            'analysis_timestamp': datetime.utcnow().isoformat()
        }


# Global Security Monitoring instance
_security_monitoring: Optional[SecurityMonitoringDashboard] = None


def get_security_monitoring() -> SecurityMonitoringDashboard:
    """Get global Security Monitoring instance"""
    global _security_monitoring
    if not _security_monitoring:
        _security_monitoring = SecurityMonitoringDashboard()
    return _security_monitoring 