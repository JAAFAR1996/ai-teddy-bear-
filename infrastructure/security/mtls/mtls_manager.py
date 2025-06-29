"""
🔐 mTLS Manager
==============

Comprehensive mutual TLS certificate management for Zero Trust Security.
Handles CA operations, service certificates, rotation, and monitoring.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import secrets
import base64
from pathlib import Path

from cryptography import x509
from cryptography.x509.oid import NameOID, ExtensionOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend
import ssl

logger = logging.getLogger(__name__)


class CertificateStatus(Enum):
    """Certificate status enumeration"""
    VALID = "valid"
    EXPIRING_SOON = "expiring_soon"
    EXPIRED = "expired"
    REVOKED = "revoked"
    INVALID = "invalid"


class ServiceType(Enum):
    """Service types for certificate generation"""
    API_SERVICE = "api_service"
    AI_SERVICE = "ai_service"
    CHILD_SERVICE = "child_service"
    PARENT_SERVICE = "parent_service"
    DATABASE = "database"
    CACHE = "cache"
    GATEWAY = "gateway"
    MONITORING = "monitoring"


@dataclass
class CertificateInfo:
    """Certificate information and metadata"""
    service_name: str
    common_name: str
    serial_number: str
    issued_at: datetime
    expires_at: datetime
    status: CertificateStatus
    san_domains: List[str] = field(default_factory=list)
    key_usage: List[str] = field(default_factory=list)
    issuer: str = ""
    fingerprint: str = ""
    revocation_reason: Optional[str] = None


@dataclass
class CertificateBundle:
    """Complete certificate bundle"""
    private_key: bytes
    certificate: bytes
    ca_certificate: bytes
    certificate_chain: bytes
    metadata: CertificateInfo


class CertificateAuthority:
    """Certificate Authority for mTLS certificates"""
    
    def __init__(self, ca_name: str = "AI-Teddy-CA"):
        self.ca_name = ca_name
        self.ca_key: Optional[rsa.RSAPrivateKey] = None
        self.ca_cert: Optional[x509.Certificate] = None
        self.serial_counter = 1000
        self._initialize_ca()
    
    def _initialize_ca(self) -> None:
        """Initialize Certificate Authority"""
        try:
            self.ca_key = self._generate_ca_key()
            self.ca_cert = self._generate_ca_cert()
            logger.info(f"Certificate Authority '{self.ca_name}' initialized")
        except Exception as e:
            logger.error(f"Failed to initialize CA: {e}")
            raise
    
    def _generate_ca_key(self) -> rsa.RSAPrivateKey:
        """Generate CA private key"""
        return rsa.generate_private_key(
            public_exponent=65537,
            key_size=4096,
            backend=default_backend()
        )
    
    def _generate_ca_cert(self) -> x509.Certificate:
        """Generate CA certificate"""
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "California"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "San Francisco"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AI Teddy Bear Security"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "Certificate Authority"),
            x509.NameAttribute(NameOID.COMMON_NAME, self.ca_name),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            self.ca_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=3650)  # 10 years
        ).add_extension(
            x509.KeyUsage(
                key_cert_sign=True,
                crl_sign=True,
                digital_signature=False,
                key_encipherment=False,
                key_agreement=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=0),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(self.ca_key.public_key()),
            critical=False,
        ).sign(self.ca_key, hashes.SHA256(), default_backend())
        
        return cert
    
    def generate_service_certificate(
        self, 
        service_name: str, 
        service_type: ServiceType,
        additional_sans: Optional[List[str]] = None
    ) -> Tuple[rsa.RSAPrivateKey, x509.Certificate]:
        """Generate service-specific certificate"""
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,  # 2048 for services, 4096 for CA
            backend=default_backend()
        )
        
        # Prepare subject
        subject = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "AI Teddy Bear"),
            x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, service_type.value),
            x509.NameAttribute(NameOID.COMMON_NAME, f"{service_name}.ai-teddy.local"),
        ])
        
        # Prepare SAN (Subject Alternative Names)
        san_list = [
            x509.DNSName(f"{service_name}.ai-teddy.local"),
            x509.DNSName(f"{service_name}.ai-teddy.svc.cluster.local"),
            x509.DNSName(f"{service_name}"),
            x509.DNSName(f"{service_name}.default"),
            x509.DNSName(f"{service_name}.default.svc"),
            x509.DNSName(f"{service_name}.default.svc.cluster.local"),
        ]
        
        # Add additional SANs
        if additional_sans:
            for san in additional_sans:
                san_list.append(x509.DNSName(san))
        
        # Generate certificate
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            self.ca_cert.subject
        ).public_key(
            private_key.public_key()
        ).serial_number(
            self._get_next_serial()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=90)  # 90 days for service certs
        ).add_extension(
            x509.SubjectAlternativeName(san_list),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                content_commitment=False,
                data_encipherment=False,
                encipher_only=False,
                decipher_only=False
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
            ]),
            critical=True,
        ).add_extension(
            x509.SubjectKeyIdentifier.from_public_key(private_key.public_key()),
            critical=False,
        ).add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(self.ca_cert.public_key()),
            critical=False,
        ).sign(self.ca_key, hashes.SHA256(), default_backend())
        
        logger.info(f"Generated certificate for service: {service_name}")
        return private_key, cert
    
    def _get_next_serial(self) -> int:
        """Get next serial number for certificate"""
        self.serial_counter += 1
        return self.serial_counter
    
    def export_ca_certificate(self) -> bytes:
        """Export CA certificate in PEM format"""
        return self.ca_cert.public_bytes(serialization.Encoding.PEM)
    
    def export_ca_key(self) -> bytes:
        """Export CA private key in PEM format"""
        return self.ca_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )


class CertificateValidator:
    """Certificate validation and verification"""
    
    def __init__(self, ca_cert: x509.Certificate):
        self.ca_cert = ca_cert
        self.ca_public_key = ca_cert.public_key()
    
    async def validate_certificate(self, cert: x509.Certificate) -> bool:
        """Validate certificate against CA"""
        try:
            # Check if certificate is signed by our CA
            self.ca_public_key.verify(
                cert.signature,
                cert.tbs_certificate_bytes,
                padding.PKCS1v15(),
                cert.signature_hash_algorithm
            )
            
            # Check validity period
            now = datetime.utcnow()
            if now < cert.not_valid_before or now > cert.not_valid_after:
                logger.warning(f"Certificate validity period check failed")
                return False
            
            # Check critical extensions
            if not self._validate_extensions(cert):
                return False
            
            logger.info(f"Certificate validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Certificate validation failed: {e}")
            return False
    
    def _validate_extensions(self, cert: x509.Certificate) -> bool:
        """Validate certificate extensions"""
        try:
            # Check Key Usage
            key_usage = cert.extensions.get_extension_for_oid(
                ExtensionOID.KEY_USAGE
            ).value
            
            if not (key_usage.digital_signature and key_usage.key_encipherment):
                logger.warning("Invalid key usage in certificate")
                return False
            
            # Check Extended Key Usage
            ext_key_usage = cert.extensions.get_extension_for_oid(
                ExtensionOID.EXTENDED_KEY_USAGE
            ).value
            
            required_usages = [
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH
            ]
            
            for usage in required_usages:
                if usage not in ext_key_usage:
                    logger.warning(f"Missing extended key usage: {usage}")
                    return False
            
            return True
            
        except x509.ExtensionNotFound:
            logger.warning("Required extensions not found in certificate")
            return False


class CertificateStore:
    """Certificate storage and management"""
    
    def __init__(self, storage_path: str = "/etc/ssl/ai-teddy"):
        self.storage_path = Path(storage_path)
        self.certificates: Dict[str, CertificateBundle] = {}
        self._ensure_storage_directory()
    
    def _ensure_storage_directory(self) -> None:
        """Ensure storage directory exists"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Certificate storage initialized: {self.storage_path}")
    
    async def store_certificate(
        self, 
        service_name: str, 
        bundle: CertificateBundle
    ) -> None:
        """Store certificate bundle"""
        try:
            # Store in memory
            self.certificates[service_name] = bundle
            
            # Store to filesystem
            service_dir = self.storage_path / service_name
            service_dir.mkdir(exist_ok=True)
            
            # Write certificate files
            (service_dir / "key.pem").write_bytes(bundle.private_key)
            (service_dir / "cert.pem").write_bytes(bundle.certificate)
            (service_dir / "ca.pem").write_bytes(bundle.ca_certificate)
            (service_dir / "chain.pem").write_bytes(bundle.certificate_chain)
            
            # Set secure permissions
            (service_dir / "key.pem").chmod(0o600)
            (service_dir / "cert.pem").chmod(0o644)
            (service_dir / "ca.pem").chmod(0o644)
            (service_dir / "chain.pem").chmod(0o644)
            
            logger.info(f"Certificate stored for service: {service_name}")
            
        except Exception as e:
            logger.error(f"Failed to store certificate for {service_name}: {e}")
            raise
    
    async def load_certificate(self, service_name: str) -> Optional[CertificateBundle]:
        """Load certificate bundle"""
        try:
            # Check memory first
            if service_name in self.certificates:
                return self.certificates[service_name]
            
            # Load from filesystem
            service_dir = self.storage_path / service_name
            if not service_dir.exists():
                return None
            
            bundle = CertificateBundle(
                private_key=(service_dir / "key.pem").read_bytes(),
                certificate=(service_dir / "cert.pem").read_bytes(),
                ca_certificate=(service_dir / "ca.pem").read_bytes(),
                certificate_chain=(service_dir / "chain.pem").read_bytes(),
                metadata=self._extract_certificate_info(
                    (service_dir / "cert.pem").read_bytes()
                )
            )
            
            # Cache in memory
            self.certificates[service_name] = bundle
            
            logger.info(f"Certificate loaded for service: {service_name}")
            return bundle
            
        except Exception as e:
            logger.error(f"Failed to load certificate for {service_name}: {e}")
            return None
    
    def _extract_certificate_info(self, cert_bytes: bytes) -> CertificateInfo:
        """Extract certificate information"""
        cert = x509.load_pem_x509_certificate(cert_bytes, default_backend())
        
        # Extract SAN domains
        san_domains = []
        try:
            san_ext = cert.extensions.get_extension_for_oid(
                ExtensionOID.SUBJECT_ALTERNATIVE_NAME
            ).value
            san_domains = [name.value for name in san_ext]
        except x509.ExtensionNotFound:
            pass
        
        # Determine status
        now = datetime.utcnow()
        if now > cert.not_valid_after:
            status = CertificateStatus.EXPIRED
        elif now > cert.not_valid_after - timedelta(days=30):
            status = CertificateStatus.EXPIRING_SOON
        else:
            status = CertificateStatus.VALID
        
        return CertificateInfo(
            service_name="",  # Will be set by caller
            common_name=cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value,
            serial_number=str(cert.serial_number),
            issued_at=cert.not_valid_before,
            expires_at=cert.not_valid_after,
            status=status,
            san_domains=san_domains,
            issuer=cert.issuer.rfc4514_string(),
            fingerprint=cert.fingerprint(hashes.SHA256()).hex()
        )


class CertificateRotationManager:
    """Manages automatic certificate rotation"""
    
    def __init__(
        self, 
        ca: CertificateAuthority, 
        store: CertificateStore,
        rotation_threshold_days: int = 30
    ):
        self.ca = ca
        self.store = store
        self.rotation_threshold = timedelta(days=rotation_threshold_days)
        self.rotation_schedule: Dict[str, datetime] = {}
    
    async def check_and_rotate_certificates(self) -> List[str]:
        """Check all certificates and rotate if needed"""
        rotated_services = []
        
        for service_name in self.store.certificates.keys():
            if await self._should_rotate_certificate(service_name):
                await self._rotate_certificate(service_name)
                rotated_services.append(service_name)
        
        if rotated_services:
            logger.info(f"Rotated certificates for services: {rotated_services}")
        
        return rotated_services
    
    async def _should_rotate_certificate(self, service_name: str) -> bool:
        """Check if certificate should be rotated"""
        bundle = await self.store.load_certificate(service_name)
        if not bundle:
            return True  # Missing certificate should be generated
        
        # Check expiration
        time_until_expiry = bundle.metadata.expires_at - datetime.utcnow()
        if time_until_expiry <= self.rotation_threshold:
            return True
        
        # Check if manual rotation is scheduled
        if service_name in self.rotation_schedule:
            if datetime.utcnow() >= self.rotation_schedule[service_name]:
                del self.rotation_schedule[service_name]
                return True
        
        return False
    
    async def _rotate_certificate(self, service_name: str) -> None:
        """Rotate certificate for service"""
        try:
            # Determine service type (simplified logic)
            service_type = self._determine_service_type(service_name)
            
            # Generate new certificate
            private_key, certificate = self.ca.generate_service_certificate(
                service_name, service_type
            )
            
            # Create certificate bundle
            bundle = CertificateBundle(
                private_key=private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                certificate=certificate.public_bytes(serialization.Encoding.PEM),
                ca_certificate=self.ca.export_ca_certificate(),
                certificate_chain=certificate.public_bytes(serialization.Encoding.PEM) + 
                               self.ca.export_ca_certificate(),
                metadata=self.store._extract_certificate_info(
                    certificate.public_bytes(serialization.Encoding.PEM)
                )
            )
            bundle.metadata.service_name = service_name
            
            # Store new certificate
            await self.store.store_certificate(service_name, bundle)
            
            logger.info(f"Successfully rotated certificate for: {service_name}")
            
        except Exception as e:
            logger.error(f"Failed to rotate certificate for {service_name}: {e}")
            raise
    
    def _determine_service_type(self, service_name: str) -> ServiceType:
        """Determine service type from service name"""
        service_type_mapping = {
            'ai': ServiceType.AI_SERVICE,
            'child': ServiceType.CHILD_SERVICE,
            'parent': ServiceType.PARENT_SERVICE,
            'api': ServiceType.API_SERVICE,
            'database': ServiceType.DATABASE,
            'postgres': ServiceType.DATABASE,
            'redis': ServiceType.CACHE,
            'gateway': ServiceType.GATEWAY,
            'nginx': ServiceType.GATEWAY,
            'prometheus': ServiceType.MONITORING,
            'grafana': ServiceType.MONITORING,
        }
        
        for keyword, service_type in service_type_mapping.items():
            if keyword in service_name.lower():
                return service_type
        
        return ServiceType.API_SERVICE  # Default
    
    async def schedule_rotation(self, service_name: str, rotation_time: datetime) -> None:
        """Schedule manual certificate rotation"""
        self.rotation_schedule[service_name] = rotation_time
        logger.info(f"Scheduled rotation for {service_name} at {rotation_time}")


class MTLSManager:
    """Main mTLS Manager for Zero Trust Security"""
    
    def __init__(self, storage_path: str = "/etc/ssl/ai-teddy"):
        self.ca = CertificateAuthority()
        self.store = CertificateStore(storage_path)
        self.validator = CertificateValidator(self.ca.ca_cert)
        self.rotation_manager = CertificateRotationManager(self.ca, self.store)
        self.services_registry: Dict[str, ServiceType] = {}
    
    async def initialize_service_certificate(
        self, 
        service_name: str, 
        service_type: ServiceType,
        additional_sans: Optional[List[str]] = None
    ) -> CertificateBundle:
        """Initialize certificate for a service"""
        
        # Register service
        self.services_registry[service_name] = service_type
        
        # Check if certificate already exists and is valid
        existing_bundle = await self.store.load_certificate(service_name)
        if existing_bundle and existing_bundle.metadata.status == CertificateStatus.VALID:
            logger.info(f"Using existing valid certificate for: {service_name}")
            return existing_bundle
        
        # Generate new certificate
        private_key, certificate = self.ca.generate_service_certificate(
            service_name, service_type, additional_sans
        )
        
        # Create bundle
        bundle = CertificateBundle(
            private_key=private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ),
            certificate=certificate.public_bytes(serialization.Encoding.PEM),
            ca_certificate=self.ca.export_ca_certificate(),
            certificate_chain=certificate.public_bytes(serialization.Encoding.PEM) + 
                           self.ca.export_ca_certificate(),
            metadata=self.store._extract_certificate_info(
                certificate.public_bytes(serialization.Encoding.PEM)
            )
        )
        bundle.metadata.service_name = service_name
        
        # Store certificate
        await self.store.store_certificate(service_name, bundle)
        
        logger.info(f"Initialized certificate for service: {service_name}")
        return bundle
    
    async def get_ssl_context(self, service_name: str) -> ssl.SSLContext:
        """Get SSL context for service"""
        bundle = await self.store.load_certificate(service_name)
        if not bundle:
            raise ValueError(f"No certificate found for service: {service_name}")
        
        # Create SSL context
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Load CA certificate
        context.load_verify_locations(cadata=bundle.ca_certificate.decode())
        
        # Load client certificate and key
        context.load_cert_chain(
            certfile=None,
            keyfile=None,
            certdata=bundle.certificate,
            keydata=bundle.private_key
        )
        
        return context
    
    async def verify_peer_certificate(
        self, 
        peer_cert_der: bytes, 
        service_name: str
    ) -> bool:
        """Verify peer certificate in mTLS connection"""
        try:
            # Parse certificate
            peer_cert = x509.load_der_x509_certificate(peer_cert_der, default_backend())
            
            # Validate against our CA
            is_valid = await self.validator.validate_certificate(peer_cert)
            
            if is_valid:
                logger.info(f"Peer certificate verified for: {service_name}")
            else:
                logger.warning(f"Peer certificate validation failed for: {service_name}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying peer certificate: {e}")
            return False
    
    async def get_certificate_status(self, service_name: str) -> Optional[CertificateInfo]:
        """Get certificate status for service"""
        bundle = await self.store.load_certificate(service_name)
        return bundle.metadata if bundle else None
    
    async def list_all_certificates(self) -> Dict[str, CertificateInfo]:
        """List all managed certificates"""
        certificates = {}
        
        for service_name in self.store.certificates.keys():
            bundle = await self.store.load_certificate(service_name)
            if bundle:
                certificates[service_name] = bundle.metadata
        
        return certificates
    
    async def start_certificate_monitoring(self) -> None:
        """Start certificate monitoring and auto-rotation"""
        logger.info("Starting certificate monitoring and auto-rotation")
        
        while True:
            try:
                # Check and rotate certificates
                rotated = await self.rotation_manager.check_and_rotate_certificates()
                
                if rotated:
                    logger.info(f"Auto-rotated certificates: {rotated}")
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in certificate monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error


# Global mTLS Manager instance
_mtls_manager: Optional[MTLSManager] = None


def get_mtls_manager() -> MTLSManager:
    """Get global mTLS Manager instance"""
    global _mtls_manager
    if not _mtls_manager:
        _mtls_manager = MTLSManager()
    return _mtls_manager 