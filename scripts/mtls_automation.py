"""
🤖 mTLS Automation Scripts
==========================

Comprehensive automation scripts for mTLS certificate management,
deployment, monitoring, and maintenance in production environments.
"""

import argparse
import asyncio
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

sys.path.append(str(Path(__file__).parent.parent))
from infrastructure.security.mtls.certificate_monitoring import \
    get_certificate_monitoring_dashboard
from infrastructure.security.mtls.kubernetes_mtls_integration import \
    get_mtls_orchestrator
from infrastructure.security.mtls.mtls_manager import (ServiceType,
                                                       get_mtls_manager)

logger = logging.getLogger(__name__)


class MTLSAutomationCLI:
    """Command-line interface for mTLS automation"""

    def __init__(self):
        self.mtls_manager = get_mtls_manager()
        self.orchestrator = get_mtls_orchestrator()
        self.monitoring = get_certificate_monitoring_dashboard()

    async def bootstrap_cluster(self, config_file: Optional[str] = None) -> bool:
        """Bootstrap mTLS for entire cluster"""
        logger.info("🚀 Bootstrapping cluster-wide mTLS...")
        try:
            config = await self._load_config(config_file)
            success = await self.orchestrator.bootstrap_cluster_mtls()
            if success:
                logger.info("✅ Cluster mTLS bootstrap completed successfully")
                await self.monitoring.start_monitoring()
                logger.info("📊 Certificate monitoring started")
                return True
            else:
                logger.info("❌ Cluster mTLS bootstrap failed")
                return False
        except Exception as e:
            logger.error(f"Bootstrap failed: {e}")
            logger.info(f"❌ Bootstrap error: {e}")
            return False

    async def generate_service_certificate(
        self,
        service_name: str,
        service_type: str,
        additional_sans: Optional[List[str]] = None,
    ) -> bool:
        """Generate certificate for a specific service"""
        logger.info(f"🔐 Generating certificate for service: {service_name}")
        try:
            try:
                svc_type = ServiceType(service_type.lower())
            except ValueError:
                logger.info(f"❌ Invalid service type: {service_type}")
                logger.info(f"Valid types: {[t.value for t in ServiceType]}")
                return False
            bundle = await self.mtls_manager.initialize_service_certificate(
                service_name=service_name,
                service_type=svc_type,
                additional_sans=additional_sans,
            )
            logger.info("✅ Certificate generated successfully")
            logger.info(f"   Serial: {bundle.metadata.serial_number}")
            logger.info(
                f"   Expires: {bundle.metadata.expires_at.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            logger.info(f"   SAN domains: {len(bundle.metadata.san_domains)}")
            return True
        except Exception as e:
            logger.error(f"Certificate generation failed: {e}")
            logger.info(f"❌ Certificate generation error: {e}")
            return False

    async def rotate_certificates(
        self, service_names: Optional[List[str]] = None
    ) -> bool:
        """Rotate certificates for specified services or all services"""
        if service_names:
            logger.info(
                f"🔄 Rotating certificates for services: {', '.join(service_names)}"
            )
        else:
            logger.info("🔄 Rotating all certificates...")
        try:
            if service_names:
                for service_name in service_names:
                    await self.orchestrator.mtls_manager.rotation_manager.schedule_rotation(
                        service_name, datetime.utcnow()
                    )
            rotated = (
                await self.orchestrator.mtls_manager.rotation_manager.check_and_rotate_certificates()
            )
            if rotated:
                logger.info(f"✅ Rotated certificates for: {', '.join(rotated)}")
                for service_name in rotated:
                    await self.orchestrator.k8s_integration.deploy_certificate_as_secret(
                        service_name
                    )
                logger.info("📦 Updated Kubernetes secrets")
                return True
            else:
                logger.info("ℹ️ No certificates needed rotation")
                return True
        except Exception as e:
            logger.error(f"Certificate rotation failed: {e}")
            logger.info(f"❌ Rotation error: {e}")
            return False

    async def check_certificate_health(self, output_format: str = "text") -> bool:
        """Check health of all certificates"""
        logger.info("🏥 Checking certificate health...")
        try:
            dashboard_data = await self.monitoring.get_dashboard_data()
            if output_format.lower() == "json":
                logger.info(json.dumps(dashboard_data, indent=2, default=str))
            else:
                health = dashboard_data.get("health", {})
                summary = health.get("summary", {})
                logger.info("\n📊 Health Summary:")
                logger.info(f"   Total Services: {summary.get('total_services', 0)}")
                logger.info(
                    f"   Healthy Services: {summary.get('healthy_services', 0)}"
                )
                logger.info(
                    f"   Health Percentage: {summary.get('health_percentage', 0):.1f}%"
                )
                critical_issues = health.get("critical_issues", [])
                if critical_issues:
                    logger.info("\n🚨 Critical Issues:")
                    for issue in critical_issues:
                        logger.info(f"   - {issue}")
                certificates = dashboard_data.get("certificates", {})
                expiring_soon = []
                expired = []
                for service, cert_info in certificates.items():
                    days = cert_info["days_until_expiry"]
                    if days <= 0:
                        expired.append(service)
                    elif days <= 30:
                        expiring_soon.append((service, days))
                if expired:
                    logger.info("\n❌ Expired Certificates:")
                    for service in expired:
                        logger.info(f"   - {service}")
                if expiring_soon:
                    logger.info("\n⚠️ Expiring Soon:")
                    for service, days in sorted(expiring_soon, key=lambda x: x[1]):
                        logger.info(f"   - {service}: {days} days")
            return len(dashboard_data.get("health", {}).get("critical_issues", [])) == 0
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            logger.info(f"❌ Health check error: {e}")
            return False

    async def export_certificates(self, output_dir: str, format: str = "pem") -> bool:
        """Export certificates to specified directory"""
        logger.info(f"📦 Exporting certificates to: {output_dir}")
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            certificates = await self.mtls_manager.list_all_certificates()
            for service_name in certificates.keys():
                bundle = await self.mtls_manager.store.load_certificate(service_name)
                if not bundle:
                    continue
                service_dir = output_path / service_name
                service_dir.mkdir(exist_ok=True)
                if format.lower() == "pem":
                    (service_dir / "cert.pem").write_bytes(bundle.certificate)
                    (service_dir / "key.pem").write_bytes(bundle.private_key)
                    (service_dir / "ca.pem").write_bytes(bundle.ca_certificate)
                    (service_dir / "chain.pem").write_bytes(bundle.certificate_chain)
                elif format.lower() == "json":
                    cert_data = {
                        "service_name": service_name,
                        "certificate": bundle.certificate.decode("utf-8"),
                        "private_key": bundle.private_key.decode("utf-8"),
                        "ca_certificate": bundle.ca_certificate.decode("utf-8"),
                        "metadata": {
                            "serial_number": bundle.metadata.serial_number,
                            "expires_at": bundle.metadata.expires_at.isoformat(),
                            "status": bundle.metadata.status.value,
                            "san_domains": bundle.metadata.san_domains,
                        },
                    }
                    (service_dir / "certificate.json").write_text(
                        json.dumps(cert_data, indent=2)
                    )
            logger.info(
                f"✅ Exported {len(certificates)} certificates in {format.upper()} format"
            )
            return True
        except Exception as e:
            logger.error(f"Certificate export failed: {e}")
            logger.info(f"❌ Export error: {e}")
            return False

    async def monitor_certificates(self, duration_hours: int = 24) -> bool:
        """Monitor certificates for specified duration"""
        logger.info(f"📊 Starting certificate monitoring for {duration_hours} hours...")
        try:
            await self.monitoring.start_monitoring()
            end_time = datetime.utcnow() + timedelta(hours=duration_hours)
            while datetime.utcnow() < end_time:
                dashboard_data = await self.monitoring.get_dashboard_data()
                timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                alerts = dashboard_data.get("alerts", {})
                health = dashboard_data.get("health", {}).get("summary", {})
                logger.info(f"\n[{timestamp}] Status Update:")
                logger.info(f"   Health: {health.get('health_percentage', 0):.1f}%")
                logger.info(f"   Active Alerts: {alerts.get('total', 0)}")
                recent_alerts = alerts.get("recent", [])
                critical_alerts = [a for a in recent_alerts if a["level"] == "critical"]
                if critical_alerts:
                    logger.info(f"   🚨 Critical Alerts: {len(critical_alerts)}")
                await asyncio.sleep(300)
            logger.info("✅ Monitoring completed")
            return True
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            logger.info(f"❌ Monitoring error: {e}")
            return False

    async def backup_certificates(self, backup_dir: str) -> bool:
        """Backup all certificates and CA"""
        logger.info(f"💾 Backing up certificates to: {backup_dir}")
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_path / f"mtls_backup_{timestamp}.json"
            ca_data = {
                "ca_certificate": self.mtls_manager.ca.export_ca_certificate().decode(
                    "utf-8"
                ),
                "ca_key": self.mtls_manager.ca.export_ca_key().decode("utf-8"),
            }
            certificates = await self.mtls_manager.list_all_certificates()
            cert_data = {}
            for service_name in certificates.keys():
                bundle = await self.mtls_manager.store.load_certificate(service_name)
                if bundle:
                    cert_data[service_name] = {
                        "certificate": bundle.certificate.decode("utf-8"),
                        "private_key": bundle.private_key.decode("utf-8"),
                        "metadata": {
                            "serial_number": bundle.metadata.serial_number,
                            "expires_at": bundle.metadata.expires_at.isoformat(),
                            "status": bundle.metadata.status.value,
                            "san_domains": bundle.metadata.san_domains,
                        },
                    }
            backup_data = {
                "backup_timestamp": datetime.utcnow().isoformat(),
                "ca_data": ca_data,
                "certificates": cert_data,
            }
            backup_file.write_text(json.dumps(backup_data, indent=2))
            logger.info(f"✅ Backed up {len(cert_data)} certificates")
            logger.info(f"   Backup file: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            logger.info(f"❌ Backup error: {e}")
            return False

    async def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration file"""
        if not config_file:
            return {}
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        if config_path.suffix.lower() in [".yaml", ".yml"]:
            return yaml.safe_load(config_path.read_text())
        elif config_path.suffix.lower() == ".json":
            return json.loads(config_path.read_text())
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="mTLS Automation CLI for AI Teddy Bear System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Bootstrap cluster mTLS
  python mtls_automation.py bootstrap --config cluster_config.yaml
  
  # Generate service certificate
  python mtls_automation.py generate --service ai-service --type ai_service
  
  # Rotate certificates
  python mtls_automation.py rotate --services ai-service,child-service
  
  # Check certificate health
  python mtls_automation.py health --format json
  
  # Monitor certificates
  python mtls_automation.py monitor --duration 24
  
  # Backup certificates
  python mtls_automation.py backup --output /backup/mtls
        """,
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument("--config", "-c", type=str, help="Configuration file path")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    bootstrap_parser = subparsers.add_parser("bootstrap", help="Bootstrap cluster mTLS")
    bootstrap_parser.add_argument(
        "--config", type=str, help="Cluster configuration file"
    )
    generate_parser = subparsers.add_parser(
        "generate", help="Generate service certificate"
    )
    generate_parser.add_argument("--service", required=True, help="Service name")
    generate_parser.add_argument("--type", required=True, help="Service type")
    generate_parser.add_argument("--sans", nargs="*", help="Additional SAN domains")
    rotate_parser = subparsers.add_parser("rotate", help="Rotate certificates")
    rotate_parser.add_argument(
        "--services",
        type=str,
        help="Comma-separated service names (all if not specified)",
    )
    health_parser = subparsers.add_parser("health", help="Check certificate health")
    health_parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    export_parser = subparsers.add_parser("export", help="Export certificates")
    export_parser.add_argument("--output", required=True, help="Output directory")
    export_parser.add_argument(
        "--format", choices=["pem", "json"], default="pem", help="Export format"
    )
    monitor_parser = subparsers.add_parser("monitor", help="Monitor certificates")
    monitor_parser.add_argument(
        "--duration", type=int, default=24, help="Monitoring duration in hours"
    )
    backup_parser = subparsers.add_parser("backup", help="Backup certificates")
    backup_parser.add_argument("--output", required=True, help="Backup directory")
    args = parser.parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    if not args.command:
        parser.print_help()
        return 1
    cli = MTLSAutomationCLI()
    try:
        success = False
        if args.command == "bootstrap":
            success = await cli.bootstrap_cluster(args.config)
        elif args.command == "generate":
            success = await cli.generate_service_certificate(
                args.service, args.type, args.sans
            )
        elif args.command == "rotate":
            services = args.services.split(",") if args.services else None
            success = await cli.rotate_certificates(services)
        elif args.command == "health":
            success = await cli.check_certificate_health(args.format)
        elif args.command == "export":
            success = await cli.export_certificates(args.output, args.format)
        elif args.command == "monitor":
            success = await cli.monitor_certificates(args.duration)
        elif args.command == "backup":
            success = await cli.backup_certificates(args.output)
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\n⏹️ Operation cancelled by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        logger.info(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
