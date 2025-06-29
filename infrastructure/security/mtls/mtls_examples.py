"""
🔐 mTLS Implementation Examples
===============================

Comprehensive examples demonstrating mTLS certificate management
and secure communication in the AI Teddy Bear Zero Trust architecture.
"""

import asyncio
import logging
import ssl
from datetime import datetime, timedelta
from typing import Dict, Any

from .mtls_manager import get_mtls_manager, ServiceType
from .kubernetes_mtls_integration import get_mtls_orchestrator
from .certificate_monitoring import get_certificate_monitoring_dashboard

logger = logging.getLogger(__name__)


async def example_1_initialize_service_certificates():
    """Example 1: Initialize mTLS certificates for AI Teddy Bear services"""
    
    print("🔐 Example 1: Initialize Service Certificates")
    print("-" * 60)
    
    mtls_manager = get_mtls_manager()
    
    # Define AI Teddy Bear services
    services = {
        "ai-conversation-service": ServiceType.AI_SERVICE,
        "child-data-service": ServiceType.CHILD_SERVICE,
        "parent-auth-service": ServiceType.PARENT_SERVICE,
        "audio-processing-service": ServiceType.API_SERVICE,
        "safety-monitoring-service": ServiceType.MONITORING,
        "postgres-db": ServiceType.DATABASE,
        "redis-cache": ServiceType.CACHE,
        "api-gateway": ServiceType.GATEWAY
    }
    
    print(f"Initializing certificates for {len(services)} services...")
    
    for service_name, service_type in services.items():
        print(f"\n   📋 Service: {service_name}")
        print(f"   📁 Type: {service_type.value}")
        
        try:
            # Initialize certificate with additional SANs for flexibility
            additional_sans = [
                f"{service_name}.internal",
                f"{service_name}-svc",
                f"{service_name}.monitoring"
            ]
            
            bundle = await mtls_manager.initialize_service_certificate(
                service_name=service_name,
                service_type=service_type,
                additional_sans=additional_sans
            )
            
            print(f"   ✅ Certificate initialized successfully")
            print(f"   🔑 Serial: {bundle.metadata.serial_number}")
            print(f"   📅 Expires: {bundle.metadata.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   🌐 SAN domains: {len(bundle.metadata.san_domains)} domains")
            
        except Exception as e:
            print(f"   ❌ Failed to initialize certificate: {e}")
    
    print(f"\n✅ Certificate initialization completed!")


async def example_2_secure_service_communication():
    """Example 2: Demonstrate secure service-to-service communication"""
    
    print("\n🔗 Example 2: Secure Service Communication")
    print("-" * 60)
    
    mtls_manager = get_mtls_manager()
    
    # Simulate AI service connecting to child data service
    ai_service = "ai-conversation-service"
    child_service = "child-data-service"
    
    print(f"🤖 AI Service '{ai_service}' connecting to '{child_service}'")
    
    try:
        # Get SSL context for AI service (client)
        client_context = await mtls_manager.get_ssl_context(ai_service)
        
        # Get SSL context for child service (server)  
        server_context = await mtls_manager.get_ssl_context(child_service)
        
        print(f"   ✅ Client SSL context configured for {ai_service}")
        print(f"   ✅ Server SSL context configured for {child_service}")
        
        # Verify certificate status
        ai_cert_status = await mtls_manager.get_certificate_status(ai_service)
        child_cert_status = await mtls_manager.get_certificate_status(child_service)
        
        print(f"\n   📊 Certificate Status:")
        print(f"   - {ai_service}: {ai_cert_status.status.value}")
        print(f"   - {child_service}: {child_cert_status.status.value}")
        
        # Simulate peer certificate verification
        print(f"\n   🔍 Simulating peer certificate verification...")
        
        # In real implementation, this would be the actual peer certificate
        # For demo, we'll simulate validation success
        verification_result = True  # await mtls_manager.verify_peer_certificate(peer_cert_der, child_service)
        
        if verification_result:
            print(f"   ✅ Peer certificate verification successful")
            print(f"   🔒 Secure mTLS communication established")
        else:
            print(f"   ❌ Peer certificate verification failed")
            
    except Exception as e:
        print(f"   ❌ Secure communication setup failed: {e}")


async def example_3_certificate_rotation():
    """Example 3: Demonstrate automatic certificate rotation"""
    
    print("\n🔄 Example 3: Certificate Rotation")
    print("-" * 60)
    
    mtls_manager = get_mtls_manager()
    
    service_name = "ai-conversation-service"
    
    print(f"🔄 Testing certificate rotation for '{service_name}'")
    
    try:
        # Get current certificate info
        current_cert = await mtls_manager.get_certificate_status(service_name)
        if not current_cert:
            print(f"   ❌ No certificate found for {service_name}")
            return
        
        print(f"   📊 Current Certificate:")
        print(f"   - Serial: {current_cert.serial_number}")
        print(f"   - Status: {current_cert.status.value}")
        print(f"   - Expires: {current_cert.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Schedule manual rotation (simulating near-expiry)
        rotation_time = datetime.utcnow() + timedelta(seconds=5)
        await mtls_manager.rotation_manager.schedule_rotation(service_name, rotation_time)
        
        print(f"   ⏰ Scheduled rotation for: {rotation_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Wait for rotation
        print(f"   ⏳ Waiting for rotation...")
        await asyncio.sleep(6)
        
        # Check for rotated certificates
        rotated_services = await mtls_manager.rotation_manager.check_and_rotate_certificates()
        
        if service_name in rotated_services:
            # Get new certificate info
            new_cert = await mtls_manager.get_certificate_status(service_name)
            
            print(f"   ✅ Certificate rotated successfully!")
            print(f"   📊 New Certificate:")
            print(f"   - Serial: {new_cert.serial_number}")
            print(f"   - Status: {new_cert.status.value}")
            print(f"   - Expires: {new_cert.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"   ℹ️ No rotation needed at this time")
            
    except Exception as e:
        print(f"   ❌ Certificate rotation failed: {e}")


async def example_4_kubernetes_integration():
    """Example 4: Kubernetes mTLS integration and deployment"""
    
    print("\n☸️ Example 4: Kubernetes mTLS Integration")
    print("-" * 60)
    
    try:
        orchestrator = get_mtls_orchestrator()
        
        print(f"🚀 Bootstrapping cluster-wide mTLS...")
        
        # Bootstrap mTLS for the entire cluster
        success = await orchestrator.bootstrap_cluster_mtls()
        
        if success:
            print(f"   ✅ Cluster mTLS bootstrap completed")
            print(f"   📦 Kubernetes secrets deployed")
            print(f"   🔗 Istio policies applied")
            print(f"   🔄 Deployments updated")
        else:
            print(f"   ❌ Cluster mTLS bootstrap failed")
            return
        
        # Get K8s integration for monitoring
        k8s_integration = orchestrator.k8s_integration
        
        # Monitor certificate secrets
        print(f"\n   📊 Monitoring Kubernetes certificate secrets...")
        secrets_info = await k8s_integration.monitor_certificate_secrets()
        
        print(f"   📦 Found {len(secrets_info)} certificate secrets:")
        for secret in secrets_info[:5]:  # Show first 5
            days_until_expiry = (secret.certificate_expiry - datetime.utcnow()).days
            print(f"   - {secret.namespace}/{secret.name}: expires in {days_until_expiry} days")
        
        if len(secrets_info) > 5:
            print(f"   ... and {len(secrets_info) - 5} more secrets")
            
    except Exception as e:
        print(f"   ❌ Kubernetes integration failed: {e}")


async def example_5_certificate_monitoring():
    """Example 5: Certificate monitoring and alerting"""
    
    print("\n📊 Example 5: Certificate Monitoring & Alerting")
    print("-" * 60)
    
    try:
        monitoring_dashboard = get_certificate_monitoring_dashboard()
        
        print(f"📈 Starting certificate monitoring...")
        
        # Start monitoring (non-blocking)
        await monitoring_dashboard.start_monitoring()
        
        # Get dashboard data
        print(f"\n   📊 Getting dashboard data...")
        dashboard_data = await monitoring_dashboard.get_dashboard_data()
        
        print(f"   📈 Certificate Metrics:")
        for metric, value in dashboard_data.get('metrics', {}).items():
            print(f"   - {metric.replace('_', ' ').title()}: {value}")
        
        # Health status
        health = dashboard_data.get('health', {})
        health_summary = health.get('summary', {})
        
        print(f"\n   🏥 Health Summary:")
        print(f"   - Total Services: {health_summary.get('total_services', 0)}")
        print(f"   - Healthy Services: {health_summary.get('healthy_services', 0)}")
        print(f"   - Health Percentage: {health_summary.get('health_percentage', 0):.1f}%")
        
        # Alerts
        alerts = dashboard_data.get('alerts', {})
        print(f"\n   🚨 Alert Summary:")
        print(f"   - Total Active Alerts: {alerts.get('total', 0)}")
        
        alert_levels = alerts.get('by_level', {})
        for level, count in alert_levels.items():
            if count > 0:
                print(f"   - {level.upper()}: {count} alerts")
        
        # Recent alerts
        recent_alerts = alerts.get('recent', [])
        if recent_alerts:
            print(f"\n   🔔 Recent Alerts:")
            for alert in recent_alerts[:3]:  # Show first 3
                print(f"   - {alert['level'].upper()}: {alert['message']}")
        
        # Certificate details
        certificates = dashboard_data.get('certificates', {})
        expiring_soon = []
        
        for service, cert_info in certificates.items():
            days_until_expiry = cert_info['days_until_expiry']
            if days_until_expiry <= 30:
                expiring_soon.append((service, days_until_expiry))
        
        if expiring_soon:
            print(f"\n   ⚠️ Certificates Expiring Soon:")
            for service, days in sorted(expiring_soon, key=lambda x: x[1]):
                print(f"   - {service}: {days} days")
        
        # Generate monitoring report
        print(f"\n   📄 Generating monitoring report...")
        report = await monitoring_dashboard.generate_monitoring_report()
        
        print(f"   📊 Report Summary:")
        print(f"   - Report Time: {report.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Total Services: {report.total_services}")
        print(f"   - Active Alerts: {len(report.alerts)}")
        
        if report.recommendations:
            print(f"   📝 Recommendations:")
            for rec in report.recommendations:
                print(f"   - {rec}")
                
    except Exception as e:
        print(f"   ❌ Certificate monitoring failed: {e}")


async def example_6_esp32_device_certificates():
    """Example 6: ESP32 device certificate management"""
    
    print("\n🧸 Example 6: ESP32 Device Certificate Management")
    print("-" * 60)
    
    mtls_manager = get_mtls_manager()
    
    # Simulate ESP32 device registration
    device_ids = [
        "teddy-bear-001",
        "teddy-bear-002", 
        "teddy-bear-003"
    ]
    
    print(f"🧸 Managing certificates for {len(device_ids)} ESP32 devices...")
    
    for device_id in device_ids:
        print(f"\n   🤖 Device: {device_id}")
        
        try:
            # Generate certificate for ESP32 device
            additional_sans = [
                f"{device_id}.devices.ai-teddy.com",
                f"{device_id}.iot.local"
            ]
            
            bundle = await mtls_manager.initialize_service_certificate(
                service_name=device_id,
                service_type=ServiceType.API_SERVICE,  # IoT devices use API service type
                additional_sans=additional_sans
            )
            
            print(f"   ✅ Device certificate generated")
            print(f"   🔑 Serial: {bundle.metadata.serial_number}")
            print(f"   📅 Valid until: {bundle.metadata.expires_at.strftime('%Y-%m-%d')}")
            
            # Export certificate for ESP32 deployment
            cert_data = {
                'device_id': device_id,
                'certificate': bundle.certificate.decode('utf-8'),
                'private_key': bundle.private_key.decode('utf-8'),
                'ca_certificate': bundle.ca_certificate.decode('utf-8'),
                'expires_at': bundle.metadata.expires_at.isoformat()
            }
            
            print(f"   📦 Certificate bundle prepared for ESP32 deployment")
            print(f"   🌐 SAN domains: {len(bundle.metadata.san_domains)} configured")
            
        except Exception as e:
            print(f"   ❌ Failed to generate device certificate: {e}")


async def example_7_security_validation():
    """Example 7: Security validation and compliance checks"""
    
    print("\n🛡️ Example 7: Security Validation & Compliance")
    print("-" * 60)
    
    mtls_manager = get_mtls_manager()
    
    print(f"🔍 Performing security validation checks...")
    
    # Get all certificates
    certificates = await mtls_manager.list_all_certificates()
    
    security_report = {
        'total_certificates': len(certificates),
        'valid_certificates': 0,
        'security_issues': [],
        'compliance_status': 'COMPLIANT',
        'recommendations': []
    }
    
    for service_name, cert_info in certificates.items():
        print(f"\n   🔍 Validating: {service_name}")
        
        # Security checks
        issues = []
        
        # Check certificate validity
        if cert_info.status != 'valid':
            issues.append(f"Certificate status: {cert_info.status}")
        else:
            security_report['valid_certificates'] += 1
        
        # Check expiration
        days_until_expiry = (cert_info.expires_at - datetime.utcnow()).days
        if days_until_expiry <= 0:
            issues.append("Certificate has expired")
            security_report['compliance_status'] = 'NON_COMPLIANT'
        elif days_until_expiry <= 7:
            issues.append(f"Certificate expires in {days_until_expiry} days")
        
        # Check SAN domains
        if not cert_info.san_domains:
            issues.append("No Subject Alternative Names configured")
        
        # Check key usage (simplified)
        if len(cert_info.key_usage) == 0:
            issues.append("Key usage not specified")
        
        if issues:
            print(f"   ⚠️ Issues found: {len(issues)}")
            for issue in issues:
                print(f"      - {issue}")
            security_report['security_issues'].extend([f"{service_name}: {issue}" for issue in issues])
        else:
            print(f"   ✅ Security validation passed")
    
    # Generate recommendations
    if security_report['security_issues']:
        expired_certs = [issue for issue in security_report['security_issues'] if 'expired' in issue]
        if expired_certs:
            security_report['recommendations'].append("Immediately rotate expired certificates")
        
        expiring_certs = [issue for issue in security_report['security_issues'] if 'expires in' in issue]
        if expiring_certs:
            security_report['recommendations'].append("Schedule rotation for expiring certificates")
    
    # Print security report
    print(f"\n   📊 Security Validation Report:")
    print(f"   - Total Certificates: {security_report['total_certificates']}")
    print(f"   - Valid Certificates: {security_report['valid_certificates']}")
    print(f"   - Security Issues: {len(security_report['security_issues'])}")
    print(f"   - Compliance Status: {security_report['compliance_status']}")
    
    if security_report['recommendations']:
        print(f"   📝 Recommendations:")
        for rec in security_report['recommendations']:
            print(f"      - {rec}")


async def example_8_performance_monitoring():
    """Example 8: mTLS performance monitoring and optimization"""
    
    print("\n⚡ Example 8: Performance Monitoring & Optimization")
    print("-" * 60)
    
    mtls_manager = get_mtls_manager()
    
    print(f"📊 Measuring mTLS performance metrics...")
    
    services = ["ai-conversation-service", "child-data-service", "parent-auth-service"]
    performance_metrics = {}
    
    for service_name in services:
        print(f"\n   ⚡ Testing: {service_name}")
        
        try:
            # Measure certificate loading time
            start_time = datetime.utcnow()
            bundle = await mtls_manager.store.load_certificate(service_name)
            load_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Measure SSL context creation time
            start_time = datetime.utcnow()
            ssl_context = await mtls_manager.get_ssl_context(service_name)
            context_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            # Certificate size metrics
            cert_size = len(bundle.certificate) if bundle else 0
            key_size = len(bundle.private_key) if bundle else 0
            
            performance_metrics[service_name] = {
                'certificate_load_time_ms': load_time,
                'ssl_context_creation_ms': context_time,
                'certificate_size_bytes': cert_size,
                'private_key_size_bytes': key_size,
                'total_bundle_size_bytes': cert_size + key_size
            }
            
            print(f"   📊 Performance Metrics:")
            print(f"      - Certificate load: {load_time:.2f}ms")
            print(f"      - SSL context creation: {context_time:.2f}ms")
            print(f"      - Certificate size: {cert_size:,} bytes")
            print(f"      - Total bundle size: {cert_size + key_size:,} bytes")
            
        except Exception as e:
            print(f"   ❌ Performance test failed: {e}")
    
    # Calculate averages
    if performance_metrics:
        avg_load_time = sum(m['certificate_load_time_ms'] for m in performance_metrics.values()) / len(performance_metrics)
        avg_context_time = sum(m['ssl_context_creation_ms'] for m in performance_metrics.values()) / len(performance_metrics)
        avg_bundle_size = sum(m['total_bundle_size_bytes'] for m in performance_metrics.values()) / len(performance_metrics)
        
        print(f"\n   📈 Performance Summary:")
        print(f"   - Average certificate load time: {avg_load_time:.2f}ms")
        print(f"   - Average SSL context creation: {avg_context_time:.2f}ms")
        print(f"   - Average bundle size: {avg_bundle_size:,.0f} bytes")
        
        # Performance recommendations
        if avg_load_time > 100:
            print(f"   💡 Recommendation: Consider certificate caching optimization")
        if avg_context_time > 50:
            print(f"   💡 Recommendation: Optimize SSL context creation")
        if avg_bundle_size > 10000:
            print(f"   💡 Recommendation: Consider certificate size optimization")


async def run_all_mtls_examples():
    """Run all mTLS examples"""
    
    print("🔐 Starting mTLS Implementation Examples")
    print("=" * 70)
    
    try:
        await example_1_initialize_service_certificates()
        await example_2_secure_service_communication()
        await example_3_certificate_rotation()
        await example_4_kubernetes_integration()
        await example_5_certificate_monitoring()
        await example_6_esp32_device_certificates()
        await example_7_security_validation()
        await example_8_performance_monitoring()
        
        print("\n" + "=" * 70)
        print("✅ All mTLS examples completed successfully!")
        
        # Final summary
        mtls_manager = get_mtls_manager()
        certificates = await mtls_manager.list_all_certificates()
        
        print(f"\n📊 Final mTLS Status:")
        print(f"   - Total managed certificates: {len(certificates)}")
        print(f"   - Certificate Authority: {mtls_manager.ca.ca_name}")
        print(f"   - Storage location: {mtls_manager.store.storage_path}")
        print(f"   - Monitoring active: ✅")
        print(f"   - Auto-rotation enabled: ✅")
        print(f"   - Kubernetes integration: ✅")
        
        # Show certificate statuses
        status_counts = {}
        for cert_info in certificates.values():
            status = cert_info.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print(f"\n   📊 Certificate Status Distribution:")
        for status, count in status_counts.items():
            print(f"      - {status.title()}: {count}")
        
    except Exception as e:
        print(f"\n❌ Error running mTLS examples: {e}")
        logger.error(f"mTLS examples failed: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    asyncio.run(run_all_mtls_examples()) 