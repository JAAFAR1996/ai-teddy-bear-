"""
📊 Certificate Monitoring & Alerting
====================================

Real-time certificate monitoring, alerting, and dashboard for mTLS
certificate lifecycle management in Zero Trust architecture.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from .mtls_manager import MTLSManager, CertificateStatus, CertificateInfo
from .kubernetes_mtls_integration import KubernetesMTLSIntegration

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Certificate alert levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MonitoringMetric(Enum):
    """Certificate monitoring metrics"""
    TOTAL_CERTIFICATES = "total_certificates"
    VALID_CERTIFICATES = "valid_certificates"
    EXPIRING_CERTIFICATES = "expiring_certificates"
    EXPIRED_CERTIFICATES = "expired_certificates"
    REVOKED_CERTIFICATES = "revoked_certificates"
    CERTIFICATE_ROTATIONS = "certificate_rotations"
    VALIDATION_FAILURES = "validation_failures"


@dataclass
class CertificateAlert:
    """Certificate-related alert"""
    alert_id: str
    service_name: str
    alert_type: str
    level: AlertLevel
    message: str
    details: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class MonitoringReport:
    """Certificate monitoring report"""
    timestamp: datetime
    total_services: int
    certificate_metrics: Dict[MonitoringMetric, int]
    service_statuses: Dict[str, CertificateStatus]
    alerts: List[CertificateAlert]
    recommendations: List[str]


class CertificateMetricsCollector:
    """Collects certificate metrics for monitoring"""
    
    def __init__(self, mtls_manager: MTLSManager):
        self.mtls_manager = mtls_manager
        self.metrics_history: List[Dict[str, Any]] = []
        self.collection_interval = 300  # 5 minutes
    
    async def collect_metrics(self) -> Dict[MonitoringMetric, int]:
        """Collect current certificate metrics"""
        try:
            certificates = await self.mtls_manager.list_all_certificates()
            
            metrics = {
                MonitoringMetric.TOTAL_CERTIFICATES: len(certificates),
                MonitoringMetric.VALID_CERTIFICATES: 0,
                MonitoringMetric.EXPIRING_CERTIFICATES: 0,
                MonitoringMetric.EXPIRED_CERTIFICATES: 0,
                MonitoringMetric.REVOKED_CERTIFICATES: 0
            }
            
            for cert_info in certificates.values():
                if cert_info.status == CertificateStatus.VALID:
                    metrics[MonitoringMetric.VALID_CERTIFICATES] += 1
                elif cert_info.status == CertificateStatus.EXPIRING_SOON:
                    metrics[MonitoringMetric.EXPIRING_CERTIFICATES] += 1
                elif cert_info.status == CertificateStatus.EXPIRED:
                    metrics[MonitoringMetric.EXPIRED_CERTIFICATES] += 1
                elif cert_info.status == CertificateStatus.REVOKED:
                    metrics[MonitoringMetric.REVOKED_CERTIFICATES] += 1
            
            # Store metrics history
            self.metrics_history.append({
                'timestamp': datetime.utcnow(),
                'metrics': {metric.value: value for metric, value in metrics.items()}
            })
            
            # Keep only last 24 hours of metrics
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            self.metrics_history = [
                m for m in self.metrics_history 
                if m['timestamp'] > cutoff_time
            ]
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to collect certificate metrics: {e}")
            return {}
    
    async def get_metrics_trend(
        self, 
        metric: MonitoringMetric, 
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get metrics trend over time"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        trend_data = []
        for entry in self.metrics_history:
            if entry['timestamp'] > cutoff_time:
                trend_data.append({
                    'timestamp': entry['timestamp'],
                    'value': entry['metrics'].get(metric.value, 0)
                })
        
        return sorted(trend_data, key=lambda x: x['timestamp'])
    
    async def start_metrics_collection(self) -> None:
        """Start automated metrics collection"""
        logger.info("Starting certificate metrics collection")
        
        while True:
            try:
                await self.collect_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error


class CertificateAlertManager:
    """Manages certificate alerts and notifications"""
    
    def __init__(self):
        self.alerts: Dict[str, CertificateAlert] = {}
        self.alert_handlers: Dict[AlertLevel, List[Callable]] = {
            AlertLevel.INFO: [],
            AlertLevel.WARNING: [],
            AlertLevel.ERROR: [],
            AlertLevel.CRITICAL: []
        }
        self.alert_counter = 0
    
    async def create_alert(
        self,
        service_name: str,
        alert_type: str,
        level: AlertLevel,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> CertificateAlert:
        """Create certificate alert"""
        
        self.alert_counter += 1
        alert_id = f"cert_alert_{self.alert_counter}_{datetime.utcnow().timestamp()}"
        
        alert = CertificateAlert(
            alert_id=alert_id,
            service_name=service_name,
            alert_type=alert_type,
            level=level,
            message=message,
            details=details or {},
            timestamp=datetime.utcnow()
        )
        
        self.alerts[alert_id] = alert
        
        # Trigger alert handlers
        for handler in self.alert_handlers.get(level, []):
            try:
                await handler(alert)
            except Exception as e:
                logger.error(f"Alert handler failed: {e}")
        
        logger.info(f"Created certificate alert: {alert_type} for {service_name}")
        return alert
    
    async def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].acknowledged = True
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve alert"""
        if alert_id in self.alerts:
            self.alerts[alert_id].resolved = True
            logger.info(f"Alert resolved: {alert_id}")
            return True
        return False
    
    def register_alert_handler(self, level: AlertLevel, handler: Callable) -> None:
        """Register alert handler for specific level"""
        if level not in self.alert_handlers:
            self.alert_handlers[level] = []
        self.alert_handlers[level].append(handler)
        logger.info(f"Registered alert handler for level: {level.value}")
    
    async def get_active_alerts(self) -> List[CertificateAlert]:
        """Get all active (unresolved) alerts"""
        return [alert for alert in self.alerts.values() if not alert.resolved]


class CertificateHealthChecker:
    """Performs health checks on certificates"""
    
    def __init__(self, mtls_manager: MTLSManager):
        self.mtls_manager = mtls_manager
        self.health_check_interval = 600  # 10 minutes
        self.last_health_check: Optional[datetime] = None
    
    async def perform_health_check(self, service_name: str) -> Dict[str, Any]:
        """Perform comprehensive health check on certificate"""
        try:
            cert_info = await self.mtls_manager.get_certificate_status(service_name)
            if not cert_info:
                return {
                    'service': service_name,
                    'healthy': False,
                    'issues': ['Certificate not found'],
                    'recommendations': ['Generate new certificate']
                }
            
            issues = []
            recommendations = []
            
            # Check expiration
            days_until_expiry = (cert_info.expires_at - datetime.utcnow()).days
            if days_until_expiry <= 0:
                issues.append('Certificate has expired')
                recommendations.append('Immediately rotate certificate')
            elif days_until_expiry <= 30:
                issues.append(f'Certificate expires in {days_until_expiry} days')
                recommendations.append('Schedule certificate rotation')
            
            # Check certificate status
            if cert_info.status not in [CertificateStatus.VALID, CertificateStatus.EXPIRING_SOON]:
                issues.append(f'Certificate status: {cert_info.status.value}')
                recommendations.append('Investigate certificate status')
            
            # Check SAN domains
            if not cert_info.san_domains:
                issues.append('No Subject Alternative Names found')
                recommendations.append('Verify certificate configuration')
            
            # Overall health assessment
            healthy = len(issues) == 0 or (
                len(issues) == 1 and 'expires in' in issues[0] and days_until_expiry > 7
            )
            
            return {
                'service': service_name,
                'healthy': healthy,
                'certificate_info': {
                    'serial': cert_info.serial_number,
                    'expires_at': cert_info.expires_at.isoformat(),
                    'status': cert_info.status.value,
                    'days_until_expiry': days_until_expiry,
                    'san_domains': cert_info.san_domains
                },
                'issues': issues,
                'recommendations': recommendations,
                'check_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {e}")
            return {
                'service': service_name,
                'healthy': False,
                'issues': [f'Health check failed: {str(e)}'],
                'recommendations': ['Check certificate manager logs'],
                'error': str(e)
            }
    
    async def perform_cluster_health_check(self) -> Dict[str, Any]:
        """Perform health check on all managed certificates"""
        try:
            certificates = await self.mtls_manager.list_all_certificates()
            health_results = []
            
            for service_name in certificates.keys():
                health_result = await self.perform_health_check(service_name)
                health_results.append(health_result)
            
            # Aggregate results
            total_services = len(health_results)
            healthy_services = len([r for r in health_results if r.get('healthy', False)])
            unhealthy_services = total_services - healthy_services
            
            # Identify critical issues
            critical_issues = []
            for result in health_results:
                for issue in result.get('issues', []):
                    if 'expired' in issue.lower() or 'failed' in issue.lower():
                        critical_issues.append(f"{result['service']}: {issue}")
            
            self.last_health_check = datetime.utcnow()
            
            return {
                'timestamp': self.last_health_check.isoformat(),
                'overall_health': unhealthy_services == 0,
                'summary': {
                    'total_services': total_services,
                    'healthy_services': healthy_services,
                    'unhealthy_services': unhealthy_services,
                    'health_percentage': (healthy_services / total_services * 100) if total_services > 0 else 0
                },
                'critical_issues': critical_issues,
                'service_results': health_results
            }
            
        except Exception as e:
            logger.error(f"Cluster health check failed: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_health': False,
                'error': str(e)
            }


class CertificateMonitoringDashboard:
    """Real-time certificate monitoring dashboard"""
    
    def __init__(
        self, 
        mtls_manager: MTLSManager,
        k8s_integration: Optional[KubernetesMTLSIntegration] = None
    ):
        self.mtls_manager = mtls_manager
        self.k8s_integration = k8s_integration
        self.metrics_collector = CertificateMetricsCollector(mtls_manager)
        self.alert_manager = CertificateAlertManager()
        self.health_checker = CertificateHealthChecker(mtls_manager)
        self._setup_alert_handlers()
    
    def _setup_alert_handlers(self) -> None:
        """Setup default alert handlers"""
        
        async def log_alert(alert: CertificateAlert) -> None:
            logger.log(
                logging.CRITICAL if alert.level == AlertLevel.CRITICAL else logging.WARNING,
                f"Certificate Alert: {alert.message} (Service: {alert.service_name})"
            )
        
        # Register log handler for all levels
        for level in AlertLevel:
            self.alert_manager.register_alert_handler(level, log_alert)
    
    async def start_monitoring(self) -> None:
        """Start comprehensive certificate monitoring"""
        logger.info("Starting certificate monitoring dashboard")
        
        # Start metrics collection
        asyncio.create_task(self.metrics_collector.start_metrics_collection())
        
        # Start periodic alerting
        asyncio.create_task(self._monitoring_loop())
        
        logger.info("Certificate monitoring dashboard started")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop"""
        while True:
            try:
                # Perform health check
                health_report = await self.health_checker.perform_cluster_health_check()
                
                # Generate alerts based on health check
                await self._process_health_report(health_report)
                
                # Wait 10 minutes before next check
                await asyncio.sleep(600)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _process_health_report(self, health_report: Dict[str, Any]) -> None:
        """Process health report and generate alerts"""
        
        if not health_report.get('overall_health', True):
            # Critical system-wide issues
            critical_issues = health_report.get('critical_issues', [])
            
            for issue in critical_issues:
                service_name = issue.split(':')[0]
                await self.alert_manager.create_alert(
                    service_name=service_name,
                    alert_type="certificate_health",
                    level=AlertLevel.CRITICAL,
                    message=issue,
                    details={'health_report': health_report}
                )
        
        # Process individual service results
        for result in health_report.get('service_results', []):
            if not result.get('healthy', True):
                service_name = result['service']
                issues = result.get('issues', [])
                
                # Determine alert level based on issues
                alert_level = AlertLevel.WARNING
                for issue in issues:
                    if 'expired' in issue.lower() or 'failed' in issue.lower():
                        alert_level = AlertLevel.CRITICAL
                        break
                    elif 'expires in' in issue.lower():
                        days_match = [int(s) for s in issue.split() if s.isdigit()]
                        if days_match and days_match[0] <= 7:
                            alert_level = AlertLevel.ERROR
                
                await self.alert_manager.create_alert(
                    service_name=service_name,
                    alert_type="certificate_health",
                    level=alert_level,
                    message=f"Certificate health issues: {', '.join(issues)}",
                    details={'health_result': result}
                )
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        try:
            # Collect current metrics
            current_metrics = await self.metrics_collector.collect_metrics()
            
            # Get health status
            health_report = await self.health_checker.perform_cluster_health_check()
            
            # Get active alerts
            active_alerts = await self.alert_manager.get_active_alerts()
            
            # Get Kubernetes secrets info if available
            k8s_secrets_info = []
            if self.k8s_integration:
                k8s_secrets_info = await self.k8s_integration.monitor_certificate_secrets()
            
            # Get certificate details
            certificates = await self.mtls_manager.list_all_certificates()
            
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': {metric.value: value for metric, value in current_metrics.items()},
                'health': health_report,
                'alerts': {
                    'total': len(active_alerts),
                    'by_level': {
                        level.value: len([a for a in active_alerts if a.level == level])
                        for level in AlertLevel
                    },
                    'recent': [
                        {
                            'id': alert.alert_id,
                            'service': alert.service_name,
                            'type': alert.alert_type,
                            'level': alert.level.value,
                            'message': alert.message,
                            'timestamp': alert.timestamp.isoformat()
                        }
                        for alert in sorted(active_alerts, key=lambda x: x.timestamp, reverse=True)[:10]
                    ]
                },
                'certificates': {
                    service_name: {
                        'common_name': cert_info.common_name,
                        'status': cert_info.status.value,
                        'expires_at': cert_info.expires_at.isoformat(),
                        'days_until_expiry': (cert_info.expires_at - datetime.utcnow()).days,
                        'san_domains': cert_info.san_domains,
                        'serial_number': cert_info.serial_number
                    }
                    for service_name, cert_info in certificates.items()
                },
                'kubernetes_secrets': [
                    {
                        'name': secret.name,
                        'namespace': secret.namespace,
                        'service': secret.service_name,
                        'expires_at': secret.certificate_expiry.isoformat(),
                        'days_until_expiry': (secret.certificate_expiry - datetime.utcnow()).days
                    }
                    for secret in k8s_secrets_info
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    async def generate_monitoring_report(self) -> MonitoringReport:
        """Generate comprehensive monitoring report"""
        try:
            current_metrics = await self.metrics_collector.collect_metrics()
            certificates = await self.mtls_manager.list_all_certificates()
            active_alerts = await self.alert_manager.get_active_alerts()
            
            # Generate recommendations
            recommendations = []
            
            expired_count = current_metrics.get(MonitoringMetric.EXPIRED_CERTIFICATES, 0)
            if expired_count > 0:
                recommendations.append(f"Immediately rotate {expired_count} expired certificates")
            
            expiring_count = current_metrics.get(MonitoringMetric.EXPIRING_CERTIFICATES, 0)
            if expiring_count > 0:
                recommendations.append(f"Schedule rotation for {expiring_count} expiring certificates")
            
            if len(active_alerts) > 10:
                recommendations.append("High number of active alerts - investigate certificate infrastructure")
            
            return MonitoringReport(
                timestamp=datetime.utcnow(),
                total_services=len(certificates),
                certificate_metrics=current_metrics,
                service_statuses={name: info.status for name, info in certificates.items()},
                alerts=active_alerts,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Failed to generate monitoring report: {e}")
            raise


# Global monitoring dashboard instance
_certificate_monitoring_dashboard: Optional[CertificateMonitoringDashboard] = None


def get_certificate_monitoring_dashboard() -> CertificateMonitoringDashboard:
    """Get global certificate monitoring dashboard instance"""
    global _certificate_monitoring_dashboard
    if not _certificate_monitoring_dashboard:
        from .mtls_manager import get_mtls_manager
        from .kubernetes_mtls_integration import get_k8s_mtls_integration
        
        _certificate_monitoring_dashboard = CertificateMonitoringDashboard(
            get_mtls_manager(),
            get_k8s_mtls_integration()
        )
    return _certificate_monitoring_dashboard 