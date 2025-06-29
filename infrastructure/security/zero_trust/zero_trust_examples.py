"""
🛡️ Zero Trust Security Examples
===============================

Comprehensive examples demonstrating Zero Trust Security implementation
for AI Teddy Bear system with practical security scenarios.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from uuid import uuid4

from .zero_trust_manager import get_zero_trust_manager, SecurityContext
from .security_policy_engine import get_security_policy_engine, PolicyAction
from ..monitoring.security_monitoring import get_security_monitoring, AlertSeverity

logger = logging.getLogger(__name__)


async def example_1_parent_authentication():
    """Example 1: Parent authentication and child data access"""
    
    print("🔐 Example 1: Parent Authentication & Child Access")
    print("-" * 60)
    
    zt_manager = get_zero_trust_manager()
    
    # Parent login attempt
    username = "parent_alice@example.com"
    password = "secure_parent_password_123"
    
    # Authenticate parent
    token = await zt_manager.auth_service.authenticate_user(username, password)
    
    if token:
        print(f"✅ Parent authenticated successfully")
        print(f"   - Token generated for: {username}")
        
        # Try to access child data
        resource = "/api/v1/children/child-123/profile"
        action = "read_child_profile"
        
        authorized = await zt_manager.authenticate_and_authorize(
            token=token,
            resource=resource,
            action=action,
            ip_address="192.168.1.100"
        )
        
        if authorized:
            print(f"✅ Access granted to child data")
            print(f"   - Resource: {resource}")
            print(f"   - Action: {action}")
        else:
            print(f"❌ Access denied to child data")
    
    else:
        print(f"❌ Authentication failed for: {username}")


async def example_2_admin_privilege_escalation():
    """Example 2: Admin access with privilege escalation detection"""
    
    print("\n🔒 Example 2: Admin Access with Privilege Escalation Detection")
    print("-" * 60)
    
    zt_manager = get_zero_trust_manager()
    monitoring = get_security_monitoring()
    
    # Simulate admin token (normally would come from authentication)
    admin_context = SecurityContext(
        user_id="admin_bob",
        role="admin",
        permissions={"full_access", "admin_operations"},
        device_id="admin-device-001",
        ip_address="10.0.1.50",
        session_id="admin_session_123",
        risk_score=0.2
    )
    
    # Normal admin operation
    normal_resource = "/api/v1/admin/dashboard"
    normal_action = "view_dashboard"
    
    print(f"🔍 Admin accessing normal resource: {normal_resource}")
    
    # This should be allowed
    policy_engine = get_security_policy_engine()
    result = await policy_engine.evaluate_request(
        context=admin_context,
        request_data={
            'resource': normal_resource,
            'action': normal_action,
            'timestamp': datetime.utcnow()
        }
    )
    
    print(f"   - Policy decision: {result.action.value}")
    print(f"   - Reason: {result.reason}")
    
    # Suspicious admin operation
    suspicious_resource = "/api/v1/admin/users/create_super_admin"
    suspicious_action = "create_super_admin"
    
    print(f"\n🚨 Admin attempting suspicious operation: {suspicious_resource}")
    
    # Simulate privilege escalation attempt
    high_risk_context = SecurityContext(
        user_id="admin_bob",
        role="admin",
        permissions={"full_access", "admin_operations"},
        device_id="unknown-device",  # Suspicious: unknown device
        ip_address="203.0.113.42",  # Suspicious: external IP
        session_id="suspicious_session",
        risk_score=0.9  # High risk score
    )
    
    result = await policy_engine.evaluate_request(
        context=high_risk_context,
        request_data={
            'resource': suspicious_resource,
            'action': suspicious_action,
            'timestamp': datetime.utcnow(),
            'privilege_change': True
        }
    )
    
    print(f"   - Policy decision: {result.action.value}")
    print(f"   - Reason: {result.reason}")
    
    # Create security alert for suspicious activity
    if result.action in [PolicyAction.DENY, PolicyAction.CHALLENGE]:
        alert = await monitoring.alert_manager.create_alert(
            title="Suspicious Admin Activity Detected",
            description=f"Admin {high_risk_context.user_id} attempted privilege escalation",
            severity=AlertSeverity.WARNING,
            source=high_risk_context.user_id,
            affected_resources=[suspicious_resource],
            metadata={
                'risk_score': high_risk_context.risk_score,
                'device_id': high_risk_context.device_id,
                'ip_address': high_risk_context.ip_address
            }
        )
        print(f"🚨 Security alert created: {alert.alert_id}")


async def example_3_child_safety_monitoring():
    """Example 3: Child safety monitoring and data protection"""
    
    print("\n👶 Example 3: Child Safety Monitoring & Data Protection")
    print("-" * 60)
    
    policy_engine = get_security_policy_engine()
    monitoring = get_security_monitoring()
    
    # Parent accessing child data
    parent_context = SecurityContext(
        user_id="parent_charlie",
        role="parent",
        permissions={"read_child_data", "manage_child_settings"},
        device_id="parent-device-002",
        ip_address="192.168.1.105",
        session_id="parent_session_456",
        risk_score=0.1
    )
    
    # Request to access child conversation history
    child_data_request = {
        'resource': '/api/v1/children/child-456/conversations',
        'action': 'read_conversations',
        'child_age': 7,  # Under 13 - COPPA compliance required
        'data_type': 'conversation_history',
        'personal_data': {
            'child_name': 'Emma',
            'conversation_transcripts': True,
            'emotion_analysis': True
        },
        'consent': {
            'gdpr_consent': True,
            'coppa_consent': True,
            'parental_consent': True
        }
    }
    
    print(f"👨‍👩‍👧 Parent requesting child conversation data")
    print(f"   - Child age: {child_data_request['child_age']}")
    print(f"   - Data type: {child_data_request['data_type']}")
    
    # Evaluate request against policies
    result = await policy_engine.evaluate_request(
        context=parent_context,
        request_data=child_data_request
    )
    
    print(f"   - Policy decision: {result.action.value}")
    print(f"   - Confidence: {result.confidence:.2f}")
    
    # Check compliance
    compliance_results = await policy_engine.compliance_engine.check_compliance(
        context=parent_context,
        request_data=child_data_request
    )
    
    print(f"\n📋 Compliance Check Results:")
    for framework, compliant in compliance_results.items():
        status = "✅ COMPLIANT" if compliant else "❌ VIOLATION"
        print(f"   - {framework}: {status}")
    
    # If there are compliance violations, create alerts
    violations = [f for f, c in compliance_results.items() if not c]
    if violations:
        alert = await monitoring.alert_manager.create_alert(
            title="Compliance Violation Detected",
            description=f"Request violates: {', '.join(violations)}",
            severity=AlertSeverity.ERROR,
            source=parent_context.user_id,
            affected_resources=[child_data_request['resource']],
            metadata={
                'frameworks': violations,
                'child_age': child_data_request['child_age'],
                'data_types': list(child_data_request.get('personal_data', {}).keys())
            }
        )
        print(f"🚨 Compliance violation alert: {alert.alert_id}")


async def example_4_ai_service_security():
    """Example 4: AI service security and conversation processing"""
    
    print("\n🤖 Example 4: AI Service Security & Conversation Processing")
    print("-" * 60)
    
    policy_engine = get_security_policy_engine()
    
    # AI service context
    ai_context = SecurityContext(
        user_id="ai_service_001",
        role="ai_service",
        permissions={"process_conversations", "analyze_emotions", "generate_responses"},
        device_id="ai-cluster-node-01",
        ip_address="10.0.2.100",
        session_id="ai_service_session",
        risk_score=0.05
    )
    
    # Normal conversation processing
    conversation_request = {
        'resource': '/api/v1/ai/process_conversation',
        'action': 'process_child_message',
        'child_id': 'child-789',
        'message_content': 'Tell me a story about dragons',
        'conversation_id': 'conv-12345',
        'processing_type': 'response_generation',
        'safety_check': True
    }
    
    print(f"🔄 AI service processing conversation")
    print(f"   - Child ID: {conversation_request['child_id']}")
    print(f"   - Processing type: {conversation_request['processing_type']}")
    
    result = await policy_engine.evaluate_request(
        context=ai_context,
        request_data=conversation_request
    )
    
    print(f"   - Policy decision: {result.action.value}")
    print(f"   - Processing allowed: {'Yes' if result.action == PolicyAction.ALLOW else 'No'}")
    
    # Suspicious AI service behavior
    suspicious_request = {
        'resource': '/api/v1/data/export_all_children',
        'action': 'bulk_data_export',
        'data_size': 5000000,  # 5MB - large data request
        'export_format': 'json',
        'destination': 'external_service',
        'justification': 'model_training'
    }
    
    print(f"\n🚨 AI service attempting large data export")
    print(f"   - Data size: {suspicious_request['data_size']} bytes")
    print(f"   - Destination: {suspicious_request['destination']}")
    
    # High-risk context for suspicious behavior
    suspicious_ai_context = SecurityContext(
        user_id="ai_service_001",
        role="ai_service", 
        permissions={"process_conversations", "analyze_emotions"},
        device_id="unknown-ai-node",  # Suspicious
        ip_address="203.0.113.100",  # External IP
        session_id="suspicious_ai_session",
        risk_score=0.8
    )
    
    result = await policy_engine.evaluate_request(
        context=suspicious_ai_context,
        request_data=suspicious_request
    )
    
    print(f"   - Policy decision: {result.action.value}")
    print(f"   - Risk assessment: {'High risk detected' if result.action == PolicyAction.DENY else 'Acceptable risk'}")


async def example_5_network_security_monitoring():
    """Example 5: Network security monitoring and anomaly detection"""
    
    print("\n🌐 Example 5: Network Security Monitoring & Anomaly Detection")
    print("-" * 60)
    
    monitoring = get_security_monitoring()
    
    # Start monitoring
    await monitoring.start_monitoring()
    
    # Simulate various security events
    events = [
        # Normal parent access
        {
            'user_id': 'parent_diana',
            'action': 'view_child_profile',
            'resource': '/api/v1/children/child-999/profile',
            'ip_address': '192.168.1.200',
            'risk_score': 0.1,
            'timestamp': datetime.utcnow()
        },
        
        # Suspicious access pattern
        {
            'user_id': 'parent_diana',
            'action': 'bulk_data_access',
            'resource': '/api/v1/children/*/conversations',
            'ip_address': '203.0.113.200',  # Different IP
            'risk_score': 0.7,
            'timestamp': datetime.utcnow()
        },
        
        # Failed authentication attempts
        {
            'user_id': 'unknown_user',
            'action': 'login',
            'resource': '/auth/login',
            'ip_address': '198.51.100.50',
            'failed': True,
            'attempt_count': 15,
            'risk_score': 0.9,
            'timestamp': datetime.utcnow()
        }
    ]
    
    print("📊 Processing security events...")
    
    for event in events:
        print(f"\n   Event: {event['action']} by {event['user_id']}")
        print(f"   IP: {event['ip_address']}, Risk: {event['risk_score']:.1f}")
        
        # Analyze for threats
        threats = await monitoring.threat_engine.analyze_behavior(
            context=SecurityContext(
                user_id=event['user_id'],
                role='parent',  # Assume parent for this example
                permissions={'read_child_data'},
                ip_address=event['ip_address'],
                risk_score=event['risk_score']
            ),
            request_data=event
        )
        
        if threats:
            for threat in threats:
                print(f"   🚨 Threat detected: {threat.event_type} ({threat.severity.value})")
                
                # Create alert for detected threats
                await monitoring.alert_manager.create_alert(
                    title=f"Threat Detected: {threat.event_type}",
                    description=threat.description,
                    severity=AlertSeverity.WARNING if threat.severity.value == 'medium' else AlertSeverity.ERROR,
                    source=threat.source,
                    affected_resources=[threat.target],
                    metadata=threat.metadata
                )
        else:
            print(f"   ✅ No threats detected")
    
    # Get dashboard data
    dashboard_data = await monitoring.get_dashboard_data()
    
    print(f"\n📈 Security Dashboard Summary:")
    print(f"   - Active alerts: {dashboard_data['active_alerts']}")
    print(f"   - Recent incidents: {dashboard_data['recent_incidents']}")
    print(f"   - System status: {dashboard_data['system_status']}")
    print(f"   - Monitoring timestamp: {dashboard_data['timestamp']}")


async def example_6_incident_response():
    """Example 6: Security incident response and escalation"""
    
    print("\n🚨 Example 6: Security Incident Response & Escalation")
    print("-" * 60)
    
    monitoring = get_security_monitoring()
    
    # Simulate a critical security incident
    print("🔥 Critical security incident detected!")
    
    # Create critical incident
    incident = await monitoring.alert_manager.create_incident(
        title="Potential Data Breach Attempt",
        description="Multiple failed authentication attempts followed by privilege escalation",
        severity=AlertSeverity.CRITICAL,
        affected_users={"admin_eve", "parent_frank"},
        affected_systems={"authentication_service", "child_data_service"}
    )
    
    print(f"   - Incident ID: {incident.incident_id}")
    print(f"   - Severity: {incident.severity.value}")
    print(f"   - Affected users: {len(incident.affected_users)}")
    print(f"   - Affected systems: {len(incident.affected_systems)}")
    
    # Simulate incident response actions
    print(f"\n🛠️ Incident Response Actions:")
    
    # Step 1: Immediate containment
    print("   1. ⚡ Immediate containment measures")
    incident.remediation_actions.append("Blocked suspicious IP addresses")
    incident.remediation_actions.append("Temporarily disabled affected user accounts")
    
    # Step 2: Investigation
    print("   2. 🔍 Investigation and analysis")
    incident.remediation_actions.append("Analyzed authentication logs")
    incident.remediation_actions.append("Reviewed access patterns")
    
    # Step 3: Escalation
    print("   3. 📞 Escalation to security team")
    incident.remediation_actions.append("Notified security team")
    incident.remediation_actions.append("Initiated emergency response protocol")
    
    # Step 4: Resolution
    print("   4. ✅ Resolution and recovery")
    incident.end_time = datetime.utcnow()
    incident.status = "resolved"
    incident.root_cause = "Brute force attack from compromised external system"
    incident.remediation_actions.append("Updated firewall rules")
    incident.remediation_actions.append("Enhanced monitoring for similar patterns")
    
    print(f"\n📋 Incident Resolution Summary:")
    print(f"   - Status: {incident.status}")
    print(f"   - Duration: {(incident.end_time - incident.start_time).total_seconds():.0f} seconds")
    print(f"   - Root cause: {incident.root_cause}")
    print(f"   - Remediation actions: {len(incident.remediation_actions)}")


async def example_7_compliance_reporting():
    """Example 7: Compliance reporting and audit trails"""
    
    print("\n📊 Example 7: Compliance Reporting & Audit Trails")
    print("-" * 60)
    
    policy_engine = get_security_policy_engine()
    monitoring = get_security_monitoring()
    
    # Generate compliance report
    print("📋 Generating compliance report...")
    
    # Simulate various data access scenarios
    scenarios = [
        {
            'user': 'parent_grace',
            'child_age': 8,
            'data_type': 'conversation_history',
            'consent': {'gdpr': True, 'coppa': True},
            'purpose': 'parental_review'
        },
        {
            'user': 'researcher_henry',
            'child_age': 11,
            'data_type': 'anonymized_analytics',
            'consent': {'gdpr': False, 'coppa': True},
            'purpose': 'research'
        },
        {
            'user': 'admin_iris',
            'child_age': 6,
            'data_type': 'full_profile',
            'consent': {'gdpr': True, 'coppa': False},
            'purpose': 'system_maintenance'
        }
    ]
    
    compliance_summary = {
        'GDPR': {'compliant': 0, 'violations': 0},
        'COPPA': {'compliant': 0, 'violations': 0},
        'SOC2': {'compliant': 0, 'violations': 0}
    }
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['user']} accessing {scenario['data_type']}")
        
        context = SecurityContext(
            user_id=scenario['user'],
            role='parent' if 'parent' in scenario['user'] else 'admin',
            permissions={'read_child_data'},
            risk_score=0.1
        )
        
        request_data = {
            'child_age': scenario['child_age'],
            'data_type': scenario['data_type'],
            'gdpr_consent': scenario['consent']['gdpr'],
            'parental_consent': scenario['consent']['coppa'],
            'personal_data': {'child_profile': True}
        }
        
        # Check compliance
        compliance_results = await policy_engine.compliance_engine.check_compliance(
            context=context,
            request_data=request_data
        )
        
        for framework, compliant in compliance_results.items():
            if framework in compliance_summary:
                if compliant:
                    compliance_summary[framework]['compliant'] += 1
                else:
                    compliance_summary[framework]['violations'] += 1
        
        print(f"      GDPR: {'✅' if compliance_results.get('GDPR', False) else '❌'}")
        print(f"      COPPA: {'✅' if compliance_results.get('COPPA', False) else '❌'}")
        print(f"      SOC2: {'✅' if compliance_results.get('SOC2', False) else '❌'}")
    
    # Print compliance summary
    print(f"\n📈 Compliance Summary Report:")
    for framework, stats in compliance_summary.items():
        total = stats['compliant'] + stats['violations']
        compliance_rate = (stats['compliant'] / total * 100) if total > 0 else 0
        print(f"   {framework}:")
        print(f"      - Compliance rate: {compliance_rate:.1f}%")
        print(f"      - Compliant requests: {stats['compliant']}")
        print(f"      - Violations: {stats['violations']}")


async def run_all_zero_trust_examples():
    """Run all Zero Trust Security examples"""
    
    print("🛡️ Starting Zero Trust Security Examples")
    print("=" * 70)
    
    try:
        await example_1_parent_authentication()
        await example_2_admin_privilege_escalation()
        await example_3_child_safety_monitoring()
        await example_4_ai_service_security()
        await example_5_network_security_monitoring()
        await example_6_incident_response()
        await example_7_compliance_reporting()
        
        print("\n" + "=" * 70)
        print("✅ All Zero Trust Security examples completed successfully!")
        
        # Final security metrics
        zt_manager = get_zero_trust_manager()
        metrics = await zt_manager.get_security_metrics()
        
        print(f"\n📊 Final Security Metrics:")
        print(f"   - Total security events: {metrics['total_security_events']}")
        print(f"   - Recent events: {metrics['recent_events']}")
        print(f"   - Active policies: {metrics['active_policies']}")
        print(f"   - Average risk score: {metrics['average_risk_score']:.3f}")
        
    except Exception as e:
        print(f"\n❌ Error running Zero Trust examples: {e}")
        logger.error(f"Zero Trust examples failed: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run examples
    asyncio.run(run_all_zero_trust_examples()) 