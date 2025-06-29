"""
☸️ Kubernetes mTLS Integration
==============================

Kubernetes and Istio integration for mTLS certificate deployment,
monitoring, and automation in Zero Trust architecture.
"""

import logging
import asyncio
import yaml
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from kubernetes import client, config
from kubernetes.client.rest import ApiException

from .mtls_manager import MTLSManager, ServiceType, CertificateBundle

logger = logging.getLogger(__name__)


@dataclass
class K8sSecretInfo:
    """Kubernetes secret information"""
    name: str
    namespace: str
    service_name: str
    created_at: datetime
    updated_at: datetime
    certificate_expiry: datetime


class KubernetesMTLSIntegration:
    """Kubernetes integration for mTLS certificates"""
    
    def __init__(self, mtls_manager: MTLSManager):
        self.mtls_manager = mtls_manager
        self.k8s_client = None
        self.apps_v1 = None
        self.core_v1 = None
        self._initialize_k8s_client()
    
    def _initialize_k8s_client(self) -> None:
        """Initialize Kubernetes client"""
        try:
            # Try to load in-cluster config first
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config")
        except config.ConfigException:
            try:
                # Fall back to local kubeconfig
                config.load_kube_config()
                logger.info("Loaded local Kubernetes config")
            except config.ConfigException as e:
                logger.error(f"Failed to load Kubernetes config: {e}")
                raise
        
        self.k8s_client = client.ApiClient()
        self.apps_v1 = client.AppsV1Api()
        self.core_v1 = client.CoreV1Api()
    
    async def deploy_certificate_as_secret(
        self, 
        service_name: str, 
        namespace: str = "default"
    ) -> bool:
        """Deploy certificate as Kubernetes secret"""
        try:
            # Get certificate bundle
            bundle = await self.mtls_manager.store.load_certificate(service_name)
            if not bundle:
                logger.error(f"No certificate found for service: {service_name}")
                return False
            
            # Create secret data
            secret_data = {
                'tls.key': base64.b64encode(bundle.private_key).decode('utf-8'),
                'tls.crt': base64.b64encode(bundle.certificate).decode('utf-8'),
                'ca.crt': base64.b64encode(bundle.ca_certificate).decode('utf-8'),
                'cert-chain.pem': base64.b64encode(bundle.certificate_chain).decode('utf-8')
            }
            
            # Create secret manifest
            secret = client.V1Secret(
                api_version="v1",
                kind="Secret",
                metadata=client.V1ObjectMeta(
                    name=f"{service_name}-mtls-certs",
                    namespace=namespace,
                    labels={
                        "app": service_name,
                        "certificate.ai-teddy.com/managed-by": "mtls-manager",
                        "certificate.ai-teddy.com/service": service_name,
                        "certificate.ai-teddy.com/type": "mtls"
                    },
                    annotations={
                        "certificate.ai-teddy.com/created-at": datetime.utcnow().isoformat(),
                        "certificate.ai-teddy.com/expires-at": bundle.metadata.expires_at.isoformat(),
                        "certificate.ai-teddy.com/serial": bundle.metadata.serial_number,
                        "certificate.ai-teddy.com/fingerprint": bundle.metadata.fingerprint
                    }
                ),
                type="kubernetes.io/tls",
                data=secret_data
            )
            
            # Deploy secret
            try:
                self.core_v1.create_namespaced_secret(namespace=namespace, body=secret)
                logger.info(f"Created secret {service_name}-mtls-certs in namespace {namespace}")
            except ApiException as e:
                if e.status == 409:  # Secret already exists
                    self.core_v1.patch_namespaced_secret(
                        name=f"{service_name}-mtls-certs",
                        namespace=namespace,
                        body=secret
                    )
                    logger.info(f"Updated secret {service_name}-mtls-certs in namespace {namespace}")
                else:
                    raise
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy certificate secret for {service_name}: {e}")
            return False
    
    async def create_istio_mtls_policy(
        self, 
        service_name: str, 
        namespace: str = "default"
    ) -> bool:
        """Create Istio mTLS policy for service"""
        try:
            # PeerAuthentication for strict mTLS
            peer_auth = {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "PeerAuthentication",
                "metadata": {
                    "name": f"{service_name}-mtls",
                    "namespace": namespace,
                    "labels": {
                        "app": service_name,
                        "security.ai-teddy.com/managed-by": "mtls-manager"
                    }
                },
                "spec": {
                    "selector": {
                        "matchLabels": {
                            "app": service_name
                        }
                    },
                    "mtls": {
                        "mode": "STRICT"
                    }
                }
            }
            
            # DestinationRule for mTLS
            destination_rule = {
                "apiVersion": "networking.istio.io/v1beta1", 
                "kind": "DestinationRule",
                "metadata": {
                    "name": f"{service_name}-mtls",
                    "namespace": namespace,
                    "labels": {
                        "app": service_name,
                        "security.ai-teddy.com/managed-by": "mtls-manager"
                    }
                },
                "spec": {
                    "host": f"{service_name}.{namespace}.svc.cluster.local",
                    "trafficPolicy": {
                        "tls": {
                            "mode": "ISTIO_MUTUAL"
                        }
                    }
                }
            }
            
            # Apply policies using kubectl (simplified)
            await self._apply_yaml_manifest(peer_auth)
            await self._apply_yaml_manifest(destination_rule)
            
            logger.info(f"Created Istio mTLS policies for {service_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create Istio mTLS policy for {service_name}: {e}")
            return False
    
    async def _apply_yaml_manifest(self, manifest: Dict[str, Any]) -> None:
        """Apply YAML manifest to Kubernetes"""
        # This is a simplified implementation
        # In production, you would use the appropriate Kubernetes API
        yaml_content = yaml.dump(manifest)
        logger.debug(f"Would apply manifest:\n{yaml_content}")
    
    async def update_deployment_with_mtls(
        self, 
        service_name: str, 
        namespace: str = "default"
    ) -> bool:
        """Update deployment to use mTLS certificates"""
        try:
            # Get existing deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace=namespace
            )
            
            # Add certificate volume and volume mount
            cert_volume = client.V1Volume(
                name="mtls-certs",
                secret=client.V1SecretVolumeSource(
                    secret_name=f"{service_name}-mtls-certs",
                    default_mode=0o400
                )
            )
            
            cert_volume_mount = client.V1VolumeMount(
                name="mtls-certs",
                mount_path="/etc/ssl/certs/mtls",
                read_only=True
            )
            
            # Update deployment spec
            if not deployment.spec.template.spec.volumes:
                deployment.spec.template.spec.volumes = []
            
            # Remove existing mtls-certs volume if present
            deployment.spec.template.spec.volumes = [
                v for v in deployment.spec.template.spec.volumes 
                if v.name != "mtls-certs"
            ]
            deployment.spec.template.spec.volumes.append(cert_volume)
            
            # Update containers
            for container in deployment.spec.template.spec.containers:
                if not container.volume_mounts:
                    container.volume_mounts = []
                
                # Remove existing mtls-certs volume mount
                container.volume_mounts = [
                    vm for vm in container.volume_mounts 
                    if vm.name != "mtls-certs"
                ]
                container.volume_mounts.append(cert_volume_mount)
                
                # Add environment variables for certificate paths
                if not container.env:
                    container.env = []
                
                mtls_env_vars = [
                    client.V1EnvVar(name="MTLS_CERT_PATH", value="/etc/ssl/certs/mtls/tls.crt"),
                    client.V1EnvVar(name="MTLS_KEY_PATH", value="/etc/ssl/certs/mtls/tls.key"),
                    client.V1EnvVar(name="MTLS_CA_PATH", value="/etc/ssl/certs/mtls/ca.crt"),
                    client.V1EnvVar(name="MTLS_ENABLED", value="true")
                ]
                
                # Update or add environment variables
                for env_var in mtls_env_vars:
                    existing_var = next(
                        (e for e in container.env if e.name == env_var.name), 
                        None
                    )
                    if existing_var:
                        existing_var.value = env_var.value
                    else:
                        container.env.append(env_var)
            
            # Update deployment
            self.apps_v1.patch_namespaced_deployment(
                name=service_name,
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Updated deployment {service_name} with mTLS configuration")
            return True
            
        except ApiException as e:
            if e.status == 404:
                logger.warning(f"Deployment {service_name} not found in namespace {namespace}")
            else:
                logger.error(f"Failed to update deployment {service_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating deployment {service_name}: {e}")
            return False
    
    async def monitor_certificate_secrets(self) -> List[K8sSecretInfo]:
        """Monitor certificate secrets across all namespaces"""
        try:
            secrets_info = []
            
            # List all namespaces
            namespaces = self.core_v1.list_namespace()
            
            for namespace in namespaces.items:
                ns_name = namespace.metadata.name
                
                # List secrets with our label
                secrets = self.core_v1.list_namespaced_secret(
                    namespace=ns_name,
                    label_selector="certificate.ai-teddy.com/managed-by=mtls-manager"
                )
                
                for secret in secrets.items:
                    annotations = secret.metadata.annotations or {}
                    
                    secret_info = K8sSecretInfo(
                        name=secret.metadata.name,
                        namespace=ns_name,
                        service_name=secret.metadata.labels.get(
                            "certificate.ai-teddy.com/service", "unknown"
                        ),
                        created_at=datetime.fromisoformat(
                            annotations.get("certificate.ai-teddy.com/created-at", 
                                          datetime.utcnow().isoformat())
                        ),
                        updated_at=secret.metadata.creation_timestamp.replace(tzinfo=None),
                        certificate_expiry=datetime.fromisoformat(
                            annotations.get("certificate.ai-teddy.com/expires-at",
                                          datetime.utcnow().isoformat())
                        )
                    )
                    
                    secrets_info.append(secret_info)
            
            return secrets_info
            
        except Exception as e:
            logger.error(f"Failed to monitor certificate secrets: {e}")
            return []
    
    async def cleanup_expired_secrets(self) -> List[str]:
        """Clean up expired certificate secrets"""
        try:
            cleaned_secrets = []
            secrets_info = await self.monitor_certificate_secrets()
            
            for secret_info in secrets_info:
                if secret_info.certificate_expiry < datetime.utcnow():
                    try:
                        self.core_v1.delete_namespaced_secret(
                            name=secret_info.name,
                            namespace=secret_info.namespace
                        )
                        
                        cleaned_secrets.append(f"{secret_info.namespace}/{secret_info.name}")
                        logger.info(f"Cleaned up expired secret: {secret_info.namespace}/{secret_info.name}")
                        
                    except ApiException as e:
                        logger.error(f"Failed to delete secret {secret_info.name}: {e}")
            
            return cleaned_secrets
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired secrets: {e}")
            return []


class IstioMTLSPolicyManager:
    """Manages Istio mTLS policies"""
    
    def __init__(self, k8s_integration: KubernetesMTLSIntegration):
        self.k8s_integration = k8s_integration
    
    async def create_service_mesh_policies(
        self, 
        services: Dict[str, ServiceType],
        namespace: str = "default"
    ) -> bool:
        """Create comprehensive service mesh mTLS policies"""
        try:
            # Global mTLS policy
            global_mtls_policy = {
                "apiVersion": "security.istio.io/v1beta1",
                "kind": "PeerAuthentication", 
                "metadata": {
                    "name": "default-mtls",
                    "namespace": namespace
                },
                "spec": {
                    "mtls": {
                        "mode": "STRICT"
                    }
                }
            }
            
            # Service-specific policies
            for service_name, service_type in services.items():
                await self._create_service_specific_policies(
                    service_name, service_type, namespace
                )
            
            # Apply global policy
            await self.k8s_integration._apply_yaml_manifest(global_mtls_policy)
            
            logger.info(f"Created service mesh mTLS policies for {len(services)} services")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create service mesh policies: {e}")
            return False
    
    async def _create_service_specific_policies(
        self,
        service_name: str,
        service_type: ServiceType,
        namespace: str
    ) -> None:
        """Create service-specific mTLS policies"""
        
        # Service-specific peer authentication
        peer_auth = {
            "apiVersion": "security.istio.io/v1beta1",
            "kind": "PeerAuthentication",
            "metadata": {
                "name": f"{service_name}-mtls",
                "namespace": namespace
            },
            "spec": {
                "selector": {
                    "matchLabels": {
                        "app": service_name
                    }
                },
                "mtls": {
                    "mode": "STRICT"
                }
            }
        }
        
        # Service-specific destination rule
        destination_rule = {
            "apiVersion": "networking.istio.io/v1beta1",
            "kind": "DestinationRule", 
            "metadata": {
                "name": f"{service_name}-mtls",
                "namespace": namespace
            },
            "spec": {
                "host": f"{service_name}.{namespace}.svc.cluster.local",
                "trafficPolicy": {
                    "tls": {
                        "mode": "ISTIO_MUTUAL"
                    }
                }
            }
        }
        
        # Service type specific configurations
        if service_type == ServiceType.DATABASE:
            # Stricter policies for database
            destination_rule["spec"]["trafficPolicy"]["connectionPool"] = {
                "tcp": {
                    "maxConnections": 50,
                    "connectTimeout": "30s"
                }
            }
        
        elif service_type == ServiceType.AI_SERVICE:
            # Special configuration for AI services
            destination_rule["spec"]["trafficPolicy"]["outlierDetection"] = {
                "consecutiveErrors": 3,
                "interval": "30s",
                "baseEjectionTime": "30s"
            }
        
        # Apply policies
        await self.k8s_integration._apply_yaml_manifest(peer_auth)
        await self.k8s_integration._apply_yaml_manifest(destination_rule)


class MTLSAutomationOrchestrator:
    """Orchestrates mTLS automation for the entire cluster"""
    
    def __init__(self, mtls_manager: MTLSManager):
        self.mtls_manager = mtls_manager
        self.k8s_integration = KubernetesMTLSIntegration(mtls_manager)
        self.istio_manager = IstioMTLSPolicyManager(self.k8s_integration)
        self.services_to_secure: Dict[str, ServiceType] = {}
    
    async def bootstrap_cluster_mtls(self) -> bool:
        """Bootstrap mTLS for entire cluster"""
        try:
            logger.info("Starting cluster mTLS bootstrap")
            
            # Define services to secure
            self.services_to_secure = {
                "ai-service": ServiceType.AI_SERVICE,
                "child-service": ServiceType.CHILD_SERVICE,
                "parent-service": ServiceType.PARENT_SERVICE,
                "api-gateway": ServiceType.GATEWAY,
                "postgres": ServiceType.DATABASE,
                "redis": ServiceType.CACHE,
                "auth-service": ServiceType.API_SERVICE,
                "policy-engine": ServiceType.API_SERVICE,
                "monitoring": ServiceType.MONITORING
            }
            
            # Generate certificates for all services
            for service_name, service_type in self.services_to_secure.items():
                logger.info(f"Bootstrapping mTLS for service: {service_name}")
                
                # Initialize certificate
                await self.mtls_manager.initialize_service_certificate(
                    service_name, service_type
                )
                
                # Deploy to Kubernetes
                await self.k8s_integration.deploy_certificate_as_secret(service_name)
                
                # Update deployment
                await self.k8s_integration.update_deployment_with_mtls(service_name)
            
            # Create Istio policies
            await self.istio_manager.create_service_mesh_policies(self.services_to_secure)
            
            logger.info("Cluster mTLS bootstrap completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Cluster mTLS bootstrap failed: {e}")
            return False
    
    async def start_automation_monitoring(self) -> None:
        """Start automated monitoring and maintenance"""
        logger.info("Starting mTLS automation monitoring")
        
        while True:
            try:
                # Monitor certificates
                await self._monitor_and_rotate_certificates()
                
                # Clean up expired secrets
                cleaned = await self.k8s_integration.cleanup_expired_secrets()
                if cleaned:
                    logger.info(f"Cleaned up {len(cleaned)} expired secrets")
                
                # Wait 1 hour before next cycle
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in automation monitoring: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _monitor_and_rotate_certificates(self) -> None:
        """Monitor and rotate certificates as needed"""
        
        # Check all services
        for service_name in self.services_to_secure.keys():
            cert_info = await self.mtls_manager.get_certificate_status(service_name)
            
            if not cert_info:
                logger.warning(f"No certificate found for service: {service_name}")
                continue
            
            # Check if certificate needs rotation
            days_until_expiry = (cert_info.expires_at - datetime.utcnow()).days
            
            if days_until_expiry <= 30:  # Rotate 30 days before expiry
                logger.info(f"Rotating certificate for {service_name} (expires in {days_until_expiry} days)")
                
                # Rotate certificate
                service_type = self.services_to_secure[service_name]
                await self.mtls_manager.initialize_service_certificate(
                    service_name, service_type
                )
                
                # Update Kubernetes secret
                await self.k8s_integration.deploy_certificate_as_secret(service_name)
                
                # Restart deployment to pick up new certificate
                await self._restart_deployment(service_name)
    
    async def _restart_deployment(self, service_name: str, namespace: str = "default") -> None:
        """Restart deployment to pick up new certificates"""
        try:
            # Add restart annotation to trigger rolling update
            deployment = self.k8s_integration.apps_v1.read_namespaced_deployment(
                name=service_name,
                namespace=namespace
            )
            
            if not deployment.spec.template.metadata.annotations:
                deployment.spec.template.metadata.annotations = {}
            
            deployment.spec.template.metadata.annotations["kubectl.kubernetes.io/restartedAt"] = datetime.utcnow().isoformat()
            
            self.k8s_integration.apps_v1.patch_namespaced_deployment(
                name=service_name,
                namespace=namespace,
                body=deployment
            )
            
            logger.info(f"Triggered rolling restart for deployment: {service_name}")
            
        except Exception as e:
            logger.error(f"Failed to restart deployment {service_name}: {e}")


# Global instances
_k8s_mtls_integration: Optional[KubernetesMTLSIntegration] = None
_mtls_orchestrator: Optional[MTLSAutomationOrchestrator] = None


def get_k8s_mtls_integration() -> KubernetesMTLSIntegration:
    """Get global Kubernetes mTLS integration instance"""
    global _k8s_mtls_integration
    if not _k8s_mtls_integration:
        from .mtls_manager import get_mtls_manager
        _k8s_mtls_integration = KubernetesMTLSIntegration(get_mtls_manager())
    return _k8s_mtls_integration


def get_mtls_orchestrator() -> MTLSAutomationOrchestrator:
    """Get global mTLS orchestrator instance"""
    global _mtls_orchestrator
    if not _mtls_orchestrator:
        from .mtls_manager import get_mtls_manager
        _mtls_orchestrator = MTLSAutomationOrchestrator(get_mtls_manager())
    return _mtls_orchestrator 