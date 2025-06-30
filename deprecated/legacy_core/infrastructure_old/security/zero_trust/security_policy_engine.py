"""
🛡️ Security Policy Engine
=========================

Advanced security policy engine for Zero Trust architecture.
Manages dynamic policy evaluation, threat response, and compliance enforcement.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json
import re

from .zero_trust_manager import SecurityContext, SecurityEvent, ThreatLevel

logger = logging.getLogger(__name__)


class PolicyAction(Enum):
    """Actions that can be taken based on policy evaluation"""
    ALLOW = "allow"
    DENY = "deny"
    CHALLENGE = "challenge"
    MONITOR = "monitor"
    QUARANTINE = "quarantine"


class PolicyType(Enum):
    """Types of security policies"""
    ACCESS_CONTROL = "access_control"
    DATA_PROTECTION = "data_protection"
    THREAT_RESPONSE = "threat_response"
    COMPLIANCE = "compliance"
    NETWORK_SECURITY = "network_security"


@dataclass
class PolicyRule:
    """Individual policy rule"""
    rule_id: str
    name: str
    condition: str  # JSON or expression
    action: PolicyAction
    priority: int = 100
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SecurityPolicy:
    """Comprehensive security policy"""
    policy_id: str
    name: str
    description: str
    policy_type: PolicyType
    rules: List[PolicyRule]
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = True


@dataclass
class PolicyEvaluationResult:
    """Result of policy evaluation"""
    policy_id: str
    rule_id: Optional[str]
    action: PolicyAction
    confidence: float
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class PolicyConditionEvaluator:
    """Evaluates policy conditions against security context"""
    
    def __init__(self):
        self.operators = {
            'eq': lambda a, b: a == b,
            'ne': lambda a, b: a != b,
            'gt': lambda a, b: a > b,
            'lt': lambda a, b: a < b,
            'gte': lambda a, b: a >= b,
            'lte': lambda a, b: a <= b,
            'in': lambda a, b: a in b,
            'not_in': lambda a, b: a not in b,
            'contains': lambda a, b: b in a,
            'matches': lambda a, b: bool(re.match(b, str(a))),
            'starts_with': lambda a, b: str(a).startswith(str(b)),
            'ends_with': lambda a, b: str(a).endswith(str(b))
        }
    
    async def evaluate_condition(
        self, 
        condition: str, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Evaluate policy condition"""
        
        try:
            # Parse JSON condition
            condition_obj = json.loads(condition)
            return await self._evaluate_object(condition_obj, context, request_data)
        
        except json.JSONDecodeError:
            # Treat as simple expression
            return await self._evaluate_expression(condition, context, request_data)
    
    async def _evaluate_object(
        self, 
        condition: Dict[str, Any], 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Evaluate complex condition object"""
        
        if 'and' in condition:
            results = []
            for sub_condition in condition['and']:
                result = await self._evaluate_object(sub_condition, context, request_data)
                results.append(result)
            return all(results)
        
        elif 'or' in condition:
            results = []
            for sub_condition in condition['or']:
                result = await self._evaluate_object(sub_condition, context, request_data)
                results.append(result)
            return any(results)
        
        elif 'not' in condition:
            result = await self._evaluate_object(condition['not'], context, request_data)
            return not result
        
        else:
            # Simple condition
            return await self._evaluate_simple_condition(condition, context, request_data)
    
    async def _evaluate_simple_condition(
        self, 
        condition: Dict[str, Any], 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Evaluate simple condition"""
        
        field = condition.get('field')
        operator = condition.get('operator', 'eq')
        value = condition.get('value')
        
        if not field or operator not in self.operators:
            return False
        
        # Get field value from context or request
        field_value = await self._get_field_value(field, context, request_data)
        
        # Apply operator
        return self.operators[operator](field_value, value)
    
    async def _get_field_value(
        self, 
        field: str, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> Any:
        """Extract field value from context or request data"""
        
        # Context fields
        if field.startswith('context.'):
            field_name = field[8:]  # Remove 'context.' prefix
            return getattr(context, field_name, None)
        
        # Request fields
        elif field.startswith('request.'):
            field_name = field[8:]  # Remove 'request.' prefix
            return request_data.get(field_name)
        
        # Time-based fields
        elif field == 'current_time':
            return datetime.utcnow()
        
        elif field == 'current_hour':
            return datetime.utcnow().hour
        
        elif field == 'current_day':
            return datetime.utcnow().weekday()
        
        # Default
        return None
    
    async def _evaluate_expression(
        self, 
        expression: str, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Evaluate simple string expression"""
        
        # Simple pattern matching for common cases
        if 'user_id=' in expression:
            expected_user = expression.split('user_id=')[1].strip('"\'')
            return context.user_id == expected_user
        
        if 'role=' in expression:
            expected_role = expression.split('role=')[1].strip('"\'')
            return context.role == expected_role
        
        # Default to False for unknown expressions
        return False


class ThreatResponseEngine:
    """Automated threat response engine"""
    
    def __init__(self):
        self.response_actions = {
            ThreatLevel.LOW: [PolicyAction.MONITOR],
            ThreatLevel.MEDIUM: [PolicyAction.CHALLENGE, PolicyAction.MONITOR],
            ThreatLevel.HIGH: [PolicyAction.DENY, PolicyAction.MONITOR],
            ThreatLevel.CRITICAL: [PolicyAction.QUARANTINE, PolicyAction.DENY]
        }
        self.automated_responses: Dict[str, Callable] = {}
    
    async def respond_to_threat(
        self, 
        threat_level: ThreatLevel,
        context: SecurityContext,
        threat_details: Dict[str, Any]
    ) -> List[PolicyAction]:
        """Execute automated threat response"""
        
        actions = self.response_actions.get(threat_level, [PolicyAction.MONITOR])
        
        for action in actions:
            await self._execute_response_action(action, context, threat_details)
        
        return actions
    
    async def _execute_response_action(
        self, 
        action: PolicyAction,
        context: SecurityContext,
        threat_details: Dict[str, Any]
    ) -> None:
        """Execute specific response action"""
        
        if action == PolicyAction.QUARANTINE:
            await self._quarantine_user(context.user_id)
        
        elif action == PolicyAction.DENY:
            await self._block_access(context.user_id, threat_details)
        
        elif action == PolicyAction.CHALLENGE:
            await self._challenge_user(context.user_id)
        
        elif action == PolicyAction.MONITOR:
            await self._enhance_monitoring(context.user_id)
    
    async def _quarantine_user(self, user_id: str) -> None:
        """Quarantine user account"""
        logger.critical(f"Quarantining user account: {user_id}")
        # Implement user quarantine logic
    
    async def _block_access(self, user_id: str, details: Dict[str, Any]) -> None:
        """Block user access"""
        logger.warning(f"Blocking access for user: {user_id}")
        # Implement access blocking logic
    
    async def _challenge_user(self, user_id: str) -> None:
        """Challenge user with additional authentication"""
        logger.info(f"Challenging user for additional auth: {user_id}")
        # Implement challenge logic (MFA, etc.)
    
    async def _enhance_monitoring(self, user_id: str) -> None:
        """Enhance monitoring for user"""
        logger.info(f"Enhanced monitoring activated for user: {user_id}")
        # Implement enhanced monitoring logic


class ComplianceEngine:
    """Compliance monitoring and enforcement engine"""
    
    def __init__(self):
        self.compliance_frameworks = {
            'GDPR': self._check_gdpr_compliance,
            'COPPA': self._check_coppa_compliance,
            'SOC2': self._check_soc2_compliance,
            'PCI_DSS': self._check_pci_compliance
        }
        self.violations: List[Dict[str, Any]] = []
    
    async def check_compliance(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check compliance across all frameworks"""
        
        results = {}
        
        for framework, checker in self.compliance_frameworks.items():
            try:
                is_compliant = await checker(context, request_data)
                results[framework] = is_compliant
                
                if not is_compliant:
                    await self._record_violation(framework, context, request_data)
            
            except Exception as e:
                logger.error(f"Compliance check failed for {framework}: {e}")
                results[framework] = False
        
        return results
    
    async def _check_gdpr_compliance(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Check GDPR compliance"""
        
        # Check for explicit consent for child data
        if 'child_data' in request_data:
            consent = request_data.get('consent', {})
            if not consent.get('gdpr_consent', False):
                return False
        
        # Check for data minimization
        if len(request_data.get('personal_data', {})) > 10:  # Arbitrary limit
            return False
        
        return True
    
    async def _check_coppa_compliance(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Check COPPA compliance for children under 13"""
        
        child_age = request_data.get('child_age')
        if child_age and child_age < 13:
            # Require parental consent
            parental_consent = request_data.get('parental_consent', False)
            if not parental_consent:
                return False
        
        return True
    
    async def _check_soc2_compliance(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Check SOC 2 compliance"""
        
        # Security principle checks
        if context.risk_score > 0.7:
            return False
        
        # Availability principle
        # Check if request is during maintenance window
        current_hour = datetime.utcnow().hour
        if 2 <= current_hour <= 4:  # Maintenance window
            return False
        
        return True
    
    async def _check_pci_compliance(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Check PCI DSS compliance for payment data"""
        
        # Check if payment data is being processed
        if 'payment_data' in request_data:
            # Require encrypted transmission
            if not request_data.get('encrypted', False):
                return False
            
            # Require authorized role
            if context.role not in ['payment_processor', 'admin']:
                return False
        
        return True
    
    async def _record_violation(
        self, 
        framework: str,
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> None:
        """Record compliance violation"""
        
        violation = {
            'framework': framework,
            'user_id': context.user_id,
            'timestamp': datetime.utcnow(),
            'context': {
                'role': context.role,
                'risk_score': context.risk_score
            },
            'request_summary': {
                'data_types': list(request_data.keys()),
                'size': len(str(request_data))
            }
        }
        
        self.violations.append(violation)
        logger.warning(f"Compliance violation recorded: {framework} for user {context.user_id}")


class SecurityPolicyEngine:
    """Main security policy engine"""
    
    def __init__(self):
        self.policies: Dict[str, SecurityPolicy] = {}
        self.condition_evaluator = PolicyConditionEvaluator()
        self.threat_response = ThreatResponseEngine()
        self.compliance_engine = ComplianceEngine()
        self._initialize_default_policies()
    
    async def evaluate_request(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> PolicyEvaluationResult:
        """Evaluate request against all applicable policies"""
        
        # Get applicable policies
        applicable_policies = await self._get_applicable_policies(context, request_data)
        
        # Evaluate each policy
        results = []
        for policy in applicable_policies:
            result = await self._evaluate_policy(policy, context, request_data)
            if result:
                results.append(result)
        
        # Determine final action based on priority
        if not results:
            return PolicyEvaluationResult(
                policy_id="default",
                rule_id=None,
                action=PolicyAction.DENY,
                confidence=1.0,
                reason="No applicable policies found"
            )
        
        # Sort by action priority (DENY > QUARANTINE > CHALLENGE > MONITOR > ALLOW)
        action_priority = {
            PolicyAction.DENY: 5,
            PolicyAction.QUARANTINE: 4,
            PolicyAction.CHALLENGE: 3,
            PolicyAction.MONITOR: 2,
            PolicyAction.ALLOW: 1
        }
        
        results.sort(key=lambda r: action_priority.get(r.action, 0), reverse=True)
        return results[0]
    
    async def add_policy(self, policy: SecurityPolicy) -> None:
        """Add security policy"""
        self.policies[policy.policy_id] = policy
        logger.info(f"Security policy added: {policy.name}")
    
    async def update_policy(self, policy: SecurityPolicy) -> None:
        """Update existing security policy"""
        if policy.policy_id in self.policies:
            policy.updated_at = datetime.utcnow()
            self.policies[policy.policy_id] = policy
            logger.info(f"Security policy updated: {policy.name}")
    
    async def remove_policy(self, policy_id: str) -> None:
        """Remove security policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            logger.info(f"Security policy removed: {policy_id}")
    
    async def _get_applicable_policies(
        self, 
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> List[SecurityPolicy]:
        """Get policies applicable to current request"""
        
        applicable = []
        for policy in self.policies.values():
            if policy.enabled:
                # Check if policy applies to this request
                if await self._policy_applies(policy, context, request_data):
                    applicable.append(policy)
        
        return applicable
    
    async def _policy_applies(
        self, 
        policy: SecurityPolicy,
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> bool:
        """Check if policy applies to request"""
        
        # Basic checks based on policy type
        if policy.policy_type == PolicyType.ACCESS_CONTROL:
            return True  # Always check access control
        
        elif policy.policy_type == PolicyType.DATA_PROTECTION:
            return 'personal_data' in request_data or 'child_data' in request_data
        
        elif policy.policy_type == PolicyType.THREAT_RESPONSE:
            return context.risk_score > 0.5
        
        elif policy.policy_type == PolicyType.COMPLIANCE:
            return True  # Always check compliance
        
        return True
    
    async def _evaluate_policy(
        self, 
        policy: SecurityPolicy,
        context: SecurityContext,
        request_data: Dict[str, Any]
    ) -> Optional[PolicyEvaluationResult]:
        """Evaluate single policy"""
        
        # Sort rules by priority
        sorted_rules = sorted(policy.rules, key=lambda r: r.priority, reverse=True)
        
        for rule in sorted_rules:
            if not rule.enabled:
                continue
            
            # Evaluate rule condition
            try:
                condition_met = await self.condition_evaluator.evaluate_condition(
                    rule.condition, context, request_data
                )
                
                if condition_met:
                    return PolicyEvaluationResult(
                        policy_id=policy.policy_id,
                        rule_id=rule.rule_id,
                        action=rule.action,
                        confidence=0.9,  # Can be made dynamic
                        reason=f"Rule {rule.name} matched",
                        metadata={
                            'policy_name': policy.name,
                            'rule_priority': rule.priority
                        }
                    )
            
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.rule_id}: {e}")
        
        return None
    
    def _initialize_default_policies(self) -> None:
        """Initialize default security policies"""
        
        # High-risk user monitoring policy
        high_risk_policy = SecurityPolicy(
            policy_id="high_risk_monitoring",
            name="High Risk User Monitoring",
            description="Enhanced monitoring for high-risk users",
            policy_type=PolicyType.THREAT_RESPONSE,
            rules=[
                PolicyRule(
                    rule_id="risk_score_check",
                    name="Risk Score Check",
                    condition='{"field": "context.risk_score", "operator": "gt", "value": 0.8}',
                    action=PolicyAction.CHALLENGE,
                    priority=200
                )
            ]
        )
        
        # Child data protection policy
        child_data_policy = SecurityPolicy(
            policy_id="child_data_protection",
            name="Child Data Protection",
            description="Protect child data according to COPPA",
            policy_type=PolicyType.DATA_PROTECTION,
            rules=[
                PolicyRule(
                    rule_id="child_age_check",
                    name="Child Age Verification",
                    condition='{"field": "request.child_age", "operator": "lt", "value": 13}',
                    action=PolicyAction.CHALLENGE,
                    priority=300
                )
            ]
        )
        
        # Add policies
        asyncio.create_task(self.add_policy(high_risk_policy))
        asyncio.create_task(self.add_policy(child_data_policy))


# Global Security Policy Engine instance
_security_policy_engine: Optional[SecurityPolicyEngine] = None


def get_security_policy_engine() -> SecurityPolicyEngine:
    """Get global Security Policy Engine instance"""
    global _security_policy_engine
    if not _security_policy_engine:
        _security_policy_engine = SecurityPolicyEngine()
    return _security_policy_engine 