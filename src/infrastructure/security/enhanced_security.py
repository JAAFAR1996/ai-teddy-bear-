from typing import Any, Dict, List, Optional

"""
Enhanced Security Module - Enterprise Grade 2025
OWASP compliant security with advanced threat protection
"""

import asyncio
import re
import secrets
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from ipaddress import ip_address, ip_network
from typing import Tuple, Union

import bcrypt
import jwt
import redis.asyncio as redis
import structlog
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from fastapi import HTTPException, Request, status

logger = structlog.get_logger()


class ThreatLevel(Enum):
    """Security threat levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventType(Enum):
    """Security event types for audit logging"""

    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    PASSWORD_RESET = "password_reset"
    ACCOUNT_LOCKOUT = "account_lockout"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    ENCRYPTION_OPERATION = "encryption_operation"
    DECRYPTION_OPERATION = "decryption_operation"
    API_KEY_USAGE = "api_key_usage"
    PRIVILEGE_ESCALATION = "privilege_escalation"


@dataclass
class SecurityEvent:
    """Security event data structure"""

    event_type: SecurityEventType
    timestamp: datetime
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    result: str = "success"
    threat_level: ThreatLevel = ThreatLevel.LOW
    details: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None


class AdvancedEncryption:
    """Enterprise-grade encryption service with multiple algorithms"""

    def __init__(self, master_key: Optional[bytes] = None):
        self.master_key = master_key or Fernet.generate_key()
        self.fernet = Fernet(self.master_key)
        self._key_cache: Dict[str, bytes] = {}

        # Generate RSA key pair for asymmetric encryption
        self.private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096, backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def encrypt_symmetric(
        self, data: Union[str, bytes], key_id: Optional[str] = None
    ) -> bytes:
        """Encrypt data using symmetric encryption (Fernet)"""
        if isinstance(data, str):
            data = data.encode("utf-8")

        if key_id and key_id in self._key_cache:
            fernet = Fernet(self._key_cache[key_id])
            return fernet.encrypt(data)

        return self.fernet.encrypt(data)

    def decrypt_symmetric(
        self, encrypted_data: bytes, key_id: Optional[str] = None
    ) -> bytes:
        """Decrypt data using symmetric encryption"""
        if key_id and key_id in self._key_cache:
            fernet = Fernet(self._key_cache[key_id])
            return fernet.decrypt(encrypted_data)

        return self.fernet.decrypt(encrypted_data)

    def encrypt_asymmetric(self, data: Union[str, bytes]) -> bytes:
        """Encrypt data using RSA public key"""
        if isinstance(data, str):
            data = data.encode("utf-8")

        # RSA can only encrypt data smaller than key size minus padding
        # For larger data, use hybrid encryption
        if len(data) > 446:  # 4096 bits - padding overhead
            return self._encrypt_hybrid(data)

        return self.public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def decrypt_asymmetric(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using RSA private key"""
        # Check if it's hybrid encryption
        if len(encrypted_data) > 512:  # RSA block size
            return self._decrypt_hybrid(encrypted_data)

        return self.private_key.decrypt(
            encrypted_data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

    def _encrypt_hybrid(self, data: bytes) -> bytes:
        """Hybrid encryption for large data (RSA + AES)"""
        # Generate AES key
        aes_key = secrets.token_bytes(32)  # 256-bit key
        iv = secrets.token_bytes(16)  # 128-bit IV

        # Encrypt data with AES
        cipher = Cipher(
            algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
        )
        encryptor = cipher.encryptor()

        # Pad data to multiple of 16 bytes
        padding_length = 16 - (len(data) % 16)
        padded_data = data + bytes([padding_length]) * padding_length

        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

        # Encrypt AES key with RSA
        encrypted_key = self.public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Combine encrypted key, IV, and encrypted data
        return encrypted_key + iv + encrypted_data

    def _decrypt_hybrid(self, encrypted_data: bytes) -> bytes:
        """Hybrid decryption for large data"""
        # Extract encrypted key (first 512 bytes)
        encrypted_key = encrypted_data[:512]
        iv = encrypted_data[512:528]
        encrypted_content = encrypted_data[528:]

        # Decrypt AES key with RSA
        aes_key = self.private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )

        # Decrypt data with AES
        cipher = Cipher(
            algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
        )
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_content) + decryptor.finalize()

        # Remove padding
        padding_length = padded_data[-1]
        return padded_data[:-padding_length]

    def generate_key_pair(self) -> Tuple[bytes, bytes]:
        """Generate new RSA key pair"""
        private_key = rsa.generate_private_key(
            public_exponent=65537, key_size=4096, backend=default_backend()
        )

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        public_pem = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        return private_pem, public_pem

    def derive_key(self, password: str, salt: bytes) -> bytes:
        """Derive encryption key from password using PBKDF2"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend(),
        )
        return kdf.derive(password.encode("utf-8"))


class PasswordSecurity:
    """Advanced password security with enterprise policies"""

    def __init__(self):
        self.min_length = 12
        self.max_length = 128
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_digits = True
        self.require_symbols = True
        self.min_entropy = 50  # bits
        self.password_history_size = 12
        self.max_age_days = 90

        # Common password patterns to reject
        self.forbidden_patterns = [
            r"(.)\1{3,}",  # Repeated characters
            r"(012|123|234|345|456|567|678|789|890)",  # Sequential numbers
            # Sequential letters
            r"(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)",
            r"(qwerty|asdfgh|zxcvbn)",  # Keyboard patterns
        ]

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with high cost factor"""
        return bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    def validate_password(
        self, password: str, user_info: Optional[Dict[str, str]] = None
    ) -> Tuple[bool, List[str]]:
        """Comprehensive password validation"""
        errors = []

        # Length check
        if len(password) < self.min_length:
            errors.append(
                f"Password must be at least {self.min_length} characters long"
            )
        if len(password) > self.max_length:
            errors.append(
                f"Password must be no more than {self.max_length} characters long"
            )

        # Character requirements
        if self.require_uppercase and not re.search(r"[A-Z]", password):
            errors.append("Password must contain at least one uppercase letter")
        if self.require_lowercase and not re.search(r"[a-z]", password):
            errors.append("Password must contain at least one lowercase letter")
        if self.require_digits and not re.search(r"\d", password):
            errors.append("Password must contain at least one digit")
        if self.require_symbols and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")

        # Pattern checks
        for pattern in self.forbidden_patterns:
            if re.search(pattern, password.lower()):
                errors.append("Password contains forbidden patterns")
                break

        # Entropy check
        entropy = self._calculate_entropy(password)
        if entropy < self.min_entropy:
            errors.append(
                f"Password is too predictable (entropy: {entropy:.1f} bits, minimum: {self.min_entropy})"
            )

        # User info check
        if user_info:
            for key, value in user_info.items():
                if value and len(value) > 3 and value.lower() in password.lower():
                    errors.append(f"Password cannot contain {key}")

        return len(errors) == 0, errors

    def _calculate_entropy(self, password: str) -> float:
        """Calculate password entropy in bits"""
        charset_size = 0

        if re.search(r"[a-z]", password):
            charset_size += 26
        if re.search(r"[A-Z]", password):
            charset_size += 26
        if re.search(r"\d", password):
            charset_size += 10
        if re.search(r"[^a-zA-Z0-9]", password):
            charset_size += 32  # Approximate special characters

        if charset_size == 0:
            return 0

        import math

        return len(password) * math.log2(charset_size)

    def generate_secure_password(self, length: int = 16) -> str:
        """Generate cryptographically secure password"""
        import string

        # Ensure we have all required character types
        chars = []
        if self.require_lowercase:
            chars.extend(string.ascii_lowercase)
        if self.require_uppercase:
            chars.extend(string.ascii_uppercase)
        if self.require_digits:
            chars.extend(string.digits)
        if self.require_symbols:
            chars.extend("!@#$%^&*()_+-=[]{}|;:,.<>?")

        # Generate password
        password = "".join(secrets.choice(chars) for _ in range(length))

        # Validate and regenerate if needed
        is_valid, _ = self.validate_password(password)
        if not is_valid:
            return self.generate_secure_password(length)

        return password


class RateLimitingService:
    """Advanced rate limiting with multiple strategies"""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self._memory_store: Dict[str, Dict[str, Any]] = {}

        # Rate limit configurations
        self.limits = {
            "api_general": {"requests": 100, "window": 60},  # 100 requests per minute
            "api_auth": {"requests": 5, "window": 60},  # 5 auth attempts per minute
            "websocket": {"connections": 10, "window": 60},  # 10 connections per minute
            "audio_upload": {"requests": 20, "window": 60},  # 20 uploads per minute
        }

    async def check_rate_limit(
        self,
        key: str,
        limit_type: str = "api_general",
        identifier: Optional[str] = None,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if request is within rate limit"""
        if limit_type not in self.limits:
            return True, {}

        config = self.limits[limit_type]
        full_key = f"rate_limit:{limit_type}:{key}"

        if identifier:
            full_key += f":{identifier}"

        if self.redis_client:
            return await self._check_redis_rate_limit(full_key, config)
        else:
            return await self._check_memory_rate_limit(full_key, config)

    async def _check_redis_rate_limit(
        self, key: str, config: Dict[str, int]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Redis-based sliding window rate limiting"""
        now = time.time()
        window_start = now - config["window"]

        async with self.redis_client.pipeline() as pipe:
            # Remove expired entries
            await pipe.zremrangebyscore(key, 0, window_start)

            # Count current requests
            current_count = await pipe.zcard(key)

            # Check if within limit
            if current_count >= config["requests"]:
                # Get window reset time
                oldest = await pipe.zrange(key, 0, 0, withscores=True)
                reset_time = oldest[0][1] + config["window"] if oldest else now

                return False, {
                    "limit": config["requests"],
                    "remaining": 0,
                    "reset_time": reset_time,
                    "retry_after": max(0, reset_time - now),
                }

            # Add current request
            await pipe.zadd(key, {str(now): now})
            await pipe.expire(key, config["window"])
            await pipe.execute()

            remaining = config["requests"] - current_count - 1

            return True, {
                "limit": config["requests"],
                "remaining": remaining,
                "reset_time": now + config["window"],
                "retry_after": 0,
            }

    async def _check_memory_rate_limit(
        self, key: str, config: Dict[str, int]
    ) -> Tuple[bool, Dict[str, Any]]:
        """Memory-based rate limiting (fallback)"""
        now = time.time()
        window_start = now - config["window"]

        if key not in self._memory_store:
            self._memory_store[key] = {
                "requests": [],
                "expires": now + config["window"],
            }

        bucket = self._memory_store[key]

        # Clean expired requests
        bucket["requests"] = [
            req_time for req_time in bucket["requests"] if req_time > window_start
        ]

        # Check limit
        if len(bucket["requests"]) >= config["requests"]:
            oldest_request = min(bucket["requests"])
            reset_time = oldest_request + config["window"]

            return False, {
                "limit": config["requests"],
                "remaining": 0,
                "reset_time": reset_time,
                "retry_after": max(0, reset_time - now),
            }

        # Add current request
        bucket["requests"].append(now)

        return True, {
            "limit": config["requests"],
            "remaining": config["requests"] - len(bucket["requests"]),
            "reset_time": now + config["window"],
            "retry_after": 0,
        }


class SecurityAuditLogger:
    """Comprehensive security audit logging"""

    def __init__(self, storage_backend: Optional[Any] = None):
        self.storage_backend = storage_backend
        self._event_buffer: List[SecurityEvent] = []
        self._buffer_size = 100
        self._buffer_lock = asyncio.Lock()

        # Start background flush task
        asyncio.create_task(self._flush_loop())

    async def log_event(self, event: SecurityEvent):
        """Log security event"""
        # Add correlation ID if not present
        if not event.correlation_id:
            import contextvars

            correlation_id_var = contextvars.ContextVar("correlation_id", default=None)
            event.correlation_id = correlation_id_var.get()

        async with self._buffer_lock:
            self._event_buffer.append(event)

            if len(self._event_buffer) >= self._buffer_size:
                await self._flush_events()

        # Log to structured logger immediately for critical events
        if event.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
            logger.warning(
                "Security event",
                event_type=event.event_type.value,
                threat_level=event.threat_level.value,
                user_id=event.user_id,
                ip_address=event.ip_address,
                resource=event.resource,
                details=event.details,
            )

    async def _flush_events(self):
        """Flush events to storage"""
        if not self._event_buffer:
            return

        events_to_flush = self._event_buffer.copy()
        self._event_buffer.clear()

        try:
            if self.storage_backend:
                await self.storage_backend.store_events(events_to_flush)
            else:
                # Fallback to structured logging
                for event in events_to_flush:
                    logger.info(
                        "Security audit event",
                        timestamp=event.timestamp.isoformat(),
                        event_type=event.event_type.value,
                        user_id=event.user_id,
                        ip_address=event.ip_address,
                        resource=event.resource,
                        action=event.action,
                        result=event.result,
                        threat_level=event.threat_level.value,
                        correlation_id=event.correlation_id,
                        details=event.details,
                    )
        except Exception as e:
            logger.error("Failed to flush security events", error=str(e))

    async def _flush_loop(self):
        """Background task to flush events periodically"""
        while True:
            try:
                await asyncio.sleep(30)  # Flush every 30 seconds
                async with self._buffer_lock:
                    await self._flush_events()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("Security audit flush error", error=str(e))


class ThreatDetectionEngine:
    """Advanced threat detection and prevention"""

    def __init__(self):
        self.suspicious_patterns = [
            # SQL Injection patterns
            r"(union\s+select|drop\s+table|delete\s+from|insert\s+into)",
            # XSS patterns
            r"(<script|javascript:|onload=|onerror=)",
            # Path traversal
            r"(\.\./|\.\.\\|%2e%2e%2f)",
            # Command injection
            r"(;|\||&|\$\(|\`)",
        ]

        self.ip_reputation_cache: Dict[str, Dict[str, Any]] = {}
        self.blocked_ips: set = set()
        self.suspicious_user_agents = [
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "zap",
            "burp",
        ]

    async def analyze_request(self, request: Request) -> Tuple[ThreatLevel, List[str]]:
        """Analyze request for potential threats"""
        threats = []
        max_threat_level = ThreatLevel.LOW

        # Check IP reputation
        client_ip = request.client.host if request.client else "unknown"
        ip_threat = await self._check_ip_reputation(client_ip)
        if ip_threat:
            threats.append(f"Suspicious IP: {ip_threat}")
            max_threat_level = max(max_threat_level, ThreatLevel.MEDIUM)

        # Check user agent
        user_agent = request.headers.get("user-agent", "").lower()
        if any(suspicious in user_agent for suspicious in self.suspicious_user_agents):
            threats.append("Suspicious user agent")
            max_threat_level = max(max_threat_level, ThreatLevel.HIGH)

        # Check for injection patterns in query parameters
        for param, value in request.query_params.items():
            if await self._check_injection_patterns(str(value)):
                threats.append(f"Potential injection in parameter: {param}")
                max_threat_level = max(max_threat_level, ThreatLevel.HIGH)

        # Check headers for anomalies
        header_threats = await self._analyze_headers(request.headers)
        threats.extend(header_threats)
        if header_threats:
            max_threat_level = max(max_threat_level, ThreatLevel.MEDIUM)

        return max_threat_level, threats

    async def _check_ip_reputation(self, ip: str) -> Optional[str]:
        """Check IP reputation against known threat databases"""
        # In production, this would query real threat intelligence APIs
        # For now, implement basic checks

        try:
            ip_obj = ip_address(ip)

            # Check for private/local IPs
            if ip_obj.is_private or ip_obj.is_loopback:
                return None

            # Check against known malicious networks (example)
            malicious_networks = [
                "10.0.0.0/8",  # Example - replace with real threat intelligence
            ]

            for network in malicious_networks:
                if ip_obj in ip_network(network):
                    return "Known malicious network"

            return None

        except ValueError:
            return "Invalid IP address"

    async def _check_injection_patterns(self, value: str) -> bool:
        """Check for SQL injection and other attack patterns"""
        value_lower = value.lower()

        for pattern in self.suspicious_patterns:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True

        return False

    async def _analyze_headers(self, headers) -> List[str]:
        """Analyze HTTP headers for suspicious patterns"""
        threats = []

        # Check for unusual header combinations
        if "x-forwarded-for" in headers and "x-real-ip" in headers:
            xff = headers["x-forwarded-for"]
            real_ip = headers["x-real-ip"]
            if xff != real_ip:
                threats.append("Inconsistent IP forwarding headers")

        # Check for suspicious content types
        content_type = headers.get("content-type", "")
        if "multipart/form-data" in content_type and "filename=" in content_type:
            # Potential file upload - needs additional validation
            threats.append("File upload detected - requires validation")

        return threats


class EnterpriseSecurityManager:
    """Main security manager coordinating all security components"""

    def __init__(self, settings: Optional[Any] = None):
        self.settings = settings
        self.encryption = AdvancedEncryption()
        self.password_security = PasswordSecurity()
        self.audit_logger = SecurityAuditLogger()
        self.threat_detector = ThreatDetectionEngine()

        # Rate limiting setup
        redis_client = None
        if settings and hasattr(settings, "redis_url"):
            redis_client = redis.from_url(settings.redis_url)

        self.rate_limiter = RateLimitingService(redis_client)

        # JWT settings
        self.jwt_secret = getattr(settings, "jwt_secret", secrets.token_urlsafe(32))
        self.jwt_algorithm = "HS256"
        self.jwt_expire_minutes = 30

    async def authenticate_request(self, request: Request) -> Dict[str, Any]:
        """Comprehensive request authentication and authorization"""
        start_time = time.time()

        try:
            # Threat detection
            threat_level, threats = await self.threat_detector.analyze_request(request)

            if threat_level == ThreatLevel.CRITICAL:
                await self.audit_logger.log_event(
                    SecurityEvent(
                        event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                        timestamp=datetime.utcnow(),
                        ip_address=request.client.host if request.client else None,
                        user_agent=request.headers.get("user-agent"),
                        threat_level=threat_level,
                        details={"threats": threats},
                    )
                )

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Request blocked due to security policy",
                )

            # Rate limiting
            client_ip = request.client.host if request.client else "unknown"
            is_allowed, rate_info = await self.rate_limiter.check_rate_limit(
                client_ip, "api_general"
            )

            if not is_allowed:
                await self.audit_logger.log_event(
                    SecurityEvent(
                        event_type=SecurityEventType.RATE_LIMIT_EXCEEDED,
                        timestamp=datetime.utcnow(),
                        ip_address=client_ip,
                        threat_level=ThreatLevel.MEDIUM,
                        details=rate_info,
                    )
                )

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={
                        "Retry-After": str(int(rate_info.get("retry_after", 60))),
                        "X-RateLimit-Limit": str(rate_info.get("limit", 0)),
                        "X-RateLimit-Remaining": str(rate_info.get("remaining", 0)),
                    },
                )

            # JWT token validation (if present)
            token = await self._extract_token(request)
            user_info = None

            if token:
                try:
                    user_info = jwt.decode(
                        token, self.jwt_secret, algorithms=[self.jwt_algorithm]
                    )

                    await self.audit_logger.log_event(
                        SecurityEvent(
                            event_type=SecurityEventType.LOGIN_SUCCESS,
                            timestamp=datetime.utcnow(),
                            user_id=user_info.get("user_id"),
                            ip_address=client_ip,
                            threat_level=ThreatLevel.LOW,
                        )
                    )

                except jwt.ExpiredSignatureError:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has expired",
                    )
                except jwt.InvalidTokenError:
                    await self.audit_logger.log_event(
                        SecurityEvent(
                            event_type=SecurityEventType.LOGIN_FAILURE,
                            timestamp=datetime.utcnow(),
                            ip_address=client_ip,
                            threat_level=ThreatLevel.MEDIUM,
                            details={"reason": "invalid_token"},
                        )
                    )

                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                    )

            processing_time = time.time() - start_time

            return {
                "user_info": user_info,
                "threat_level": threat_level,
                "threats": threats,
                "rate_info": rate_info,
                "processing_time": processing_time,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error("Security authentication error", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Security system error",
            )

    async def _extract_token(self, request: Request) -> Optional[str]:
        """Extract JWT token from request"""
        # Check Authorization header
        auth_header = request.headers.get("authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]

        # Check cookie
        token_cookie = request.cookies.get("access_token")
        if token_cookie:
            return token_cookie

        return None

    def generate_jwt_token(
        self, user_id: str, additional_claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate JWT token for user"""
        now = datetime.utcnow()
        payload = {
            "user_id": user_id,
            "iat": now,
            "exp": now + timedelta(minutes=self.jwt_expire_minutes),
            "iss": "ai-teddy-bear",
        }

        if additional_claims:
            payload.update(additional_claims)

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    async def encrypt_sensitive_data(
        self, data: Union[str, bytes], context: Optional[str] = None
    ) -> bytes:
        """Encrypt sensitive data with audit logging"""
        encrypted = self.encryption.encrypt_symmetric(data)

        await self.audit_logger.log_event(
            SecurityEvent(
                event_type=SecurityEventType.ENCRYPTION_OPERATION,
                timestamp=datetime.utcnow(),
                details={
                    "context": context,
                    "data_length": len(data) if isinstance(data, (str, bytes)) else 0,
                },
            )
        )

        return encrypted

    async def decrypt_sensitive_data(
        self, encrypted_data: bytes, context: Optional[str] = None
    ) -> bytes:
        """Decrypt sensitive data with audit logging"""
        decrypted = self.encryption.decrypt_symmetric(encrypted_data)

        await self.audit_logger.log_event(
            SecurityEvent(
                event_type=SecurityEventType.DECRYPTION_OPERATION,
                timestamp=datetime.utcnow(),
                details={"context": context},
            )
        )

        return decrypted


# Global security manager instance
_security_manager: Optional[EnterpriseSecurityManager] = None


def get_security_manager() -> EnterpriseSecurityManager:
    """Get global security manager instance"""
    global _security_manager
    if _security_manager is None:
        _security_manager = EnterpriseSecurityManager()
    return _security_manager


def set_security_manager(EnterpriseSecurityManager) -> None:
    """Set global security manager instance"""
    global _security_manager
    _security_manager = manager
