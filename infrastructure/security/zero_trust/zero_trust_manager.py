"""
🔒 Zero Trust Security Manager
==============================

Comprehensive Zero Trust Security implementation for AI Teddy Bear system.
Handles authentication, authorization, policy management, and threat detection.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import jwt
import hashlib
import secrets
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security levels for Zero Trust classification"""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    TOP_SECRET = "top_secret"


class ThreatLevel(Enum):
    """Threat classification levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class SecurityContext:
    """Security context for requests"""
    user_id: str
    role: str
    permissions: Set[str]
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[str] = None
    risk_score: float = 0.0


@dataclass(frozen=True)
class SecurityEvent:
    """Security event for monitoring"""
    event_id: str
    event_type: str
    severity: ThreatLevel
    source: str
    target: str
    description: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AccessPolicy:
    """Access control policy"""
    policy_id: str
    name: str
    resource: str
    allowed_roles: Set[str]
    required_permissions: Set[str]
    security_level: SecurityLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


class AuthenticationService:
    """Zero Trust authentication service"""
    
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.token_expiry = timedelta(hours=24)
        self.refresh_expiry = timedelta(days=7)
        self.failed_attempts: Dict[str, List[datetime]] = {}
        self.max_attempts = 5
        self.lockout_duration = timedelta(minutes=30)
    
    async def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user with rate limiting"""
        
        # Check for account lockout
        if await self._is_account_locked(username):
            logger.warning(f"Authentication attempt on locked account: {username}")
            return None
        
        # Validate credentials (implement actual validation)
        if await self._validate_credentials(username, password):
            # Clear failed attempts on successful login
            self.failed_attempts.pop(username, None)
            
            # Generate JWT token
            token = await self._generate_token(username)
            logger.info(f"User authenticated successfully: {username}")
            return token
        else:
            # Record failed attempt
            await self._record_failed_attempt(username)
            logger.warning(f"Failed authentication attempt: {username}")
            return None
    
    async def validate_token(self, token: str) -> Optional[SecurityContext]:
        """Validate JWT token and extract security context"""
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token expiration
            exp = payload.get('exp')
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                logger.warning("Token expired")
                return None
            
            # Extract security context
            context = SecurityContext(
                user_id=payload.get('user_id'),
                role=payload.get('role'),
                permissions=set(payload.get('permissions', [])),
                device_id=payload.get('device_id'),
                session_id=payload.get('session_id')
            )
            
            return context
            
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            return None
    
    async def _validate_credentials(self, username: str, password: str) -> bool:
        """Validate user credentials (implement with database)"""
        # This is a placeholder - implement actual credential validation
        return username == "admin" and password == "secure_password"
    
    async def _generate_token(self, username: str) -> str:
        """Generate JWT token with user claims"""
        
        payload = {
            'user_id': username,
            'role': 'parent',  # Get from user database
            'permissions': ['read_child_data', 'write_child_data'],  # Get from RBAC
            'device_id': None,
            'session_id': secrets.token_urlsafe(16),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + self.token_expiry
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def _is_account_locked(self, username: str) -> bool:
        """Check if account is locked due to failed attempts"""
        
        attempts = self.failed_attempts.get(username, [])
        if len(attempts) < self.max_attempts:
            return False
        
        # Check if lockout period has expired
        last_attempt = max(attempts)
        if datetime.utcnow() - last_attempt > self.lockout_duration:
            # Clear expired lockout
            self.failed_attempts.pop(username, None)
            return False
        
        return True
    
    async def _record_failed_attempt(self, username: str) -> None:
        """Record failed authentication attempt"""
        
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.utcnow())
        
        # Keep only recent attempts
        cutoff = datetime.utcnow() - self.lockout_duration
        self.failed_attempts[username] = [
            attempt for attempt in self.failed_attempts[username]
            if attempt > cutoff
        ]


class AuthorizationService:
    """Zero Trust authorization service"""
    
    def __init__(self):
        self.policies: Dict[str, AccessPolicy] = {}
        self.role_hierarchy = {
            'admin': {'parent', 'child_service', 'guest'},
            'parent': {'child_service', 'guest'},
            'child_service': {'guest'},
            'guest': set()
        }
    
    async def authorize_request(
        self, 
        context: SecurityContext, 
        resource: str, 
        action: str
    ) -> bool:
        """Authorize request based on Zero Trust principles"""
        
        # Find applicable policies
        applicable_policies = await self._find_applicable_policies(resource)
        
        if not applicable_policies:
            logger.warning(f"No policies found for resource: {resource}")
            return False
        
        # Evaluate each policy
        for policy in applicable_policies:
            if await self._evaluate_policy(context, policy, action):
                logger.info(f"Access granted: {context.user_id} -> {resource}")
                return True
        
        logger.warning(f"Access denied: {context.user_id} -> {resource}")
        return False
    
    async def add_policy(self, policy: AccessPolicy) -> None:
        """Add access control policy"""
        self.policies[policy.policy_id] = policy
        logger.info(f"Policy added: {policy.name}")
    
    async def remove_policy(self, policy_id: str) -> None:
        """Remove access control policy"""
        if policy_id in self.policies:
            del self.policies[policy_id]
            logger.info(f"Policy removed: {policy_id}")
    
    async def _find_applicable_policies(self, resource: str) -> List[AccessPolicy]:
        """Find policies applicable to resource"""
        
        applicable = []
        for policy in self.policies.values():
            if policy.enabled and self._resource_matches(resource, policy.resource):
                applicable.append(policy)
        
        return applicable
    
    async def _evaluate_policy(
        self, 
        context: SecurityContext, 
        policy: AccessPolicy, 
        action: str
    ) -> bool:
        """Evaluate policy against security context"""
        
        # Check role authorization
        if not self._has_required_role(context.role, policy.allowed_roles):
            return False
        
        # Check permissions
        if not policy.required_permissions.issubset(context.permissions):
            return False
        
        # Check additional conditions
        if not await self._evaluate_conditions(context, policy.conditions):
            return False
        
        return True
    
    def _has_required_role(self, user_role: str, allowed_roles: Set[str]) -> bool:
        """Check if user role is authorized"""
        
        if user_role in allowed_roles:
            return True
        
        # Check role hierarchy
        user_inherited_roles = self.role_hierarchy.get(user_role, set())
        return bool(allowed_roles.intersection(user_inherited_roles))
    
    def _resource_matches(self, resource: str, pattern: str) -> bool:
        """Check if resource matches policy pattern"""
        # Simple pattern matching - can be enhanced with regex
        return resource.startswith(pattern.rstrip('*'))
    
    async def _evaluate_conditions(
        self, 
        context: SecurityContext, 
        conditions: Dict[str, Any]
    ) -> bool:
        """Evaluate additional policy conditions"""
        
        # Time-based conditions
        if 'time_range' in conditions:
            if not self._check_time_range(conditions['time_range']):
                return False
        
        # IP-based conditions
        if 'allowed_ips' in conditions and context.ip_address:
            if context.ip_address not in conditions['allowed_ips']:
                return False
        
        # Risk score conditions
        if 'max_risk_score' in conditions:
            if context.risk_score > conditions['max_risk_score']:
                return False
        
        return True
    
    def _check_time_range(self, time_range: Dict[str, str]) -> bool:
        """Check if current time is within allowed range"""
        # Implement time range validation
        return True


class ThreatDetectionService:
    """Zero Trust threat detection and monitoring"""
    
    def __init__(self):
        self.security_events: List[SecurityEvent] = []
        self.threat_patterns = {
            'brute_force': {'max_attempts': 10, 'time_window': 300},
            'unusual_access': {'risk_threshold': 0.8},
            'privilege_escalation': {'role_changes': True}
        }
        self.risk_scores: Dict[str, float] = {}
    
    async def detect_threats(self, context: SecurityContext, action: str) -> ThreatLevel:
        """Detect potential security threats"""
        
        threat_level = ThreatLevel.LOW
        
        # Check for brute force attacks
        if await self._detect_brute_force(context):
            threat_level = max(threat_level, ThreatLevel.HIGH)
        
        # Check for unusual access patterns
        if await self._detect_unusual_access(context, action):
            threat_level = max(threat_level, ThreatLevel.MEDIUM)
        
        # Check for privilege escalation
        if await self._detect_privilege_escalation(context):
            threat_level = max(threat_level, ThreatLevel.CRITICAL)
        
        # Record security event
        if threat_level != ThreatLevel.LOW:
            await self._record_security_event(context, action, threat_level)
        
        return threat_level
    
    async def calculate_risk_score(self, context: SecurityContext) -> float:
        """Calculate risk score for security context"""
        
        risk_score = 0.0
        
        # Factors that increase risk score
        # - Unknown device
        if not context.device_id:
            risk_score += 0.3
        
        # - Unusual time access
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:  # Outside normal hours
            risk_score += 0.2
        
        # - High privilege role
        if context.role in ['admin', 'super_admin']:
            risk_score += 0.1
        
        # - Previous security incidents
        user_incidents = len([
            event for event in self.security_events
            if event.source == context.user_id and 
            event.timestamp > datetime.utcnow() - timedelta(days=7)
        ])
        risk_score += min(user_incidents * 0.1, 0.4)
        
        return min(risk_score, 1.0)
    
    async def _detect_brute_force(self, context: SecurityContext) -> bool:
        """Detect brute force attack patterns"""
        
        recent_events = [
            event for event in self.security_events
            if event.source == context.user_id and
            event.event_type == 'authentication_failure' and
            event.timestamp > datetime.utcnow() - timedelta(seconds=300)
        ]
        
        return len(recent_events) > 10
    
    async def _detect_unusual_access(self, context: SecurityContext, action: str) -> bool:
        """Detect unusual access patterns"""
        
        # Check if user is accessing resources they don't normally access
        user_history = [
            event for event in self.security_events
            if event.source == context.user_id and
            event.timestamp > datetime.utcnow() - timedelta(days=30)
        ]
        
        # If this is a new type of action for this user, flag as unusual
        action_history = [e for e in user_history if action in e.description]
        
        return len(action_history) == 0 and len(user_history) > 0
    
    async def _detect_privilege_escalation(self, context: SecurityContext) -> bool:
        """Detect privilege escalation attempts"""
        
        # Check for rapid role changes or privilege increases
        role_changes = [
            event for event in self.security_events
            if event.source == context.user_id and
            'role_change' in event.event_type and
            event.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]
        
        return len(role_changes) > 0
    
    async def _record_security_event(
        self, 
        context: SecurityContext, 
        action: str, 
        threat_level: ThreatLevel
    ) -> None:
        """Record security event for monitoring"""
        
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(16),
            event_type='threat_detected',
            severity=threat_level,
            source=context.user_id,
            target=action,
            description=f"Threat detected: {threat_level.value}",
            metadata={
                'user_id': context.user_id,
                'role': context.role,
                'device_id': context.device_id,
                'ip_address': context.ip_address,
                'risk_score': context.risk_score
            }
        )
        
        self.security_events.append(event)
        logger.warning(f"Security threat detected: {threat_level.value} for user {context.user_id}")


class ZeroTrustManager:
    """Main Zero Trust Security Manager"""
    
    def __init__(self, secret_key: str):
        self.auth_service = AuthenticationService(secret_key)
        self.authz_service = AuthorizationService()
        self.threat_service = ThreatDetectionService()
        self._initialize_default_policies()
    
    async def authenticate_and_authorize(
        self, 
        token: str, 
        resource: str, 
        action: str,
        ip_address: Optional[str] = None
    ) -> bool:
        """Complete Zero Trust authentication and authorization"""
        
        # Step 1: Validate token and extract context
        context = await self.auth_service.validate_token(token)
        if not context:
            return False
        
        # Step 2: Calculate risk score
        risk_score = await self.threat_service.calculate_risk_score(context)
        context = SecurityContext(
            user_id=context.user_id,
            role=context.role,
            permissions=context.permissions,
            device_id=context.device_id,
            ip_address=ip_address,
            session_id=context.session_id,
            risk_score=risk_score
        )
        
        # Step 3: Detect threats
        threat_level = await self.threat_service.detect_threats(context, action)
        if threat_level == ThreatLevel.CRITICAL:
            logger.critical(f"Critical threat detected, blocking access: {context.user_id}")
            return False
        
        # Step 4: Authorize request
        return await self.authz_service.authorize_request(context, resource, action)
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics for monitoring"""
        
        recent_events = [
            event for event in self.threat_service.security_events
            if event.timestamp > datetime.utcnow() - timedelta(hours=24)
        ]
        
        return {
            'total_security_events': len(self.threat_service.security_events),
            'recent_events': len(recent_events),
            'threat_distribution': {
                level.value: len([e for e in recent_events if e.severity == level])
                for level in ThreatLevel
            },
            'active_policies': len(self.authz_service.policies),
            'average_risk_score': sum(self.threat_service.risk_scores.values()) / 
                                 max(len(self.threat_service.risk_scores), 1)
        }
    
    def _initialize_default_policies(self) -> None:
        """Initialize default access control policies"""
        
        # Policy for parent access to child data
        parent_policy = AccessPolicy(
            policy_id="parent_child_access",
            name="Parent Child Data Access",
            resource="/api/v1/children/*",
            allowed_roles={'parent', 'guardian'},
            required_permissions={'read_child_data'},
            security_level=SecurityLevel.CONFIDENTIAL
        )
        
        # Policy for admin access
        admin_policy = AccessPolicy(
            policy_id="admin_full_access",
            name="Admin Full Access",
            resource="/api/*",
            allowed_roles={'admin'},
            required_permissions={'full_access'},
            security_level=SecurityLevel.RESTRICTED
        )
        
        # Policy for AI service access
        ai_policy = AccessPolicy(
            policy_id="ai_service_access",
            name="AI Service Access",
            resource="/api/v1/ai/*",
            allowed_roles={'ai_service'},
            required_permissions={'process_conversations'},
            security_level=SecurityLevel.INTERNAL
        )
        
        # Add policies
        asyncio.create_task(self.authz_service.add_policy(parent_policy))
        asyncio.create_task(self.authz_service.add_policy(admin_policy))
        asyncio.create_task(self.authz_service.add_policy(ai_policy))


# Global Zero Trust Manager instance
_zero_trust_manager: Optional[ZeroTrustManager] = None


def get_zero_trust_manager() -> ZeroTrustManager:
    """Get global Zero Trust Manager instance"""
    global _zero_trust_manager
    if not _zero_trust_manager:
        secret_key = "your-super-secret-key-here"  # Use environment variable in production
        _zero_trust_manager = ZeroTrustManager(secret_key)
    return _zero_trust_manager 