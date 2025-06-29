#!/usr/bin/env python3
"""
🤖 mTLS Automation Scripts
==========================

Comprehensive automation scripts for mTLS certificate management,
deployment, monitoring, and maintenance in production environments.
"""

import argparse
import asyncio
import logging
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from infrastructure.security.mtls.mtls_manager import get_mtls_manager, ServiceType
from infrastructure.security.mtls.kubernetes_mtls_integration import get_mtls_orchestrator
from infrastructure.security.mtls.certificate_monitoring import get_certificate_monitoring_dashboard

logger = logging.getLogger(__name__)


class MTLSAutomationCLI:
    """Command-line interface for mTLS automation"""
    
    def __init__(self):
        self.mtls_manager = get_mtls_manager()
        self.orchestrator = get_mtls_orchestrator()
        self.monitoring = get_certificate_monitoring_dashboard()
    
    async def bootstrap_cluster(self, config_file: Optional[str] = None) -> bool:
        """Bootstrap mTLS for entire cluster"""
        
        print("🚀 Bootstrapping cluster-wide mTLS...")
        
        try:
            # Load configuration
            config = await self._load_config(config_file)
            
            # Bootstrap cluster
            success = await self.orchestrator.bootstrap_cluster_mtls()
            
            if success:
                print("✅ Cluster mTLS bootstrap completed successfully")
                
                # Start monitoring
                await self.monitoring.start_monitoring()
                print("📊 Certificate monitoring started")
                
                return True
            else:
                print("❌ Cluster mTLS bootstrap failed")
                return False
                
        except Exception as e:
            logger.error(f"Bootstrap failed: {e}")
            print(f"❌ Bootstrap error: {e}")
            return False
    
    async def generate_service_certificate(
        self, 
        service_name: str, 
        service_type: str,
        additional_sans: Optional[List[str]] = None
    ) -> bool:
        """Generate certificate for a specific service"""
        
        print(f"🔐 Generating certificate for service: {service_name}")
        
        try:
            # Parse service type
            try:
                svc_type = ServiceType(service_type.lower())
            except ValueError:
                print(f"❌ Invalid service type: {service_type}")
                print(f"Valid types: {[t.value for t in ServiceType]}")
                return False
            
            # Generate certificate
            bundle = await self.mtls_manager.initialize_service_certificate(
                service_name=service_name,
                service_type=svc_type,
                additional_sans=additional_sans
            )
            
            print(f"✅ Certificate generated successfully")
            print(f"   Serial: {bundle.metadata.serial_number}")
            print(f"   Expires: {bundle.metadata.expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   SAN domains: {len(bundle.metadata.san_domains)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Certificate generation failed: {e}")
            print(f"❌ Certificate generation error: {e}")
            return False
    
    async def rotate_certificates(self, service_names: Optional[List[str]] = None) -> bool:
        """Rotate certificates for specified services or all services"""
        
        if service_names:
            print(f"🔄 Rotating certificates for services: {', '.join(service_names)}")
        else:
            print(f"🔄 Rotating all certificates...")
        
        try:
            if service_names:
                # Rotate specific services
                for service_name in service_names:
                    await self.orchestrator.mtls_manager.rotation_manager.schedule_rotation(
                        service_name, datetime.utcnow()
                    )
            
            # Perform rotation check
            rotated = await self.orchestrator.mtls_manager.rotation_manager.check_and_rotate_certificates()
            
            if rotated:
                print(f"✅ Rotated certificates for: {', '.join(rotated)}")
                
                # Update Kubernetes secrets
                for service_name in rotated:
                    await self.orchestrator.k8s_integration.deploy_certificate_as_secret(service_name)
                
                print(f"📦 Updated Kubernetes secrets")
                return True
            else:
                print(f"ℹ️ No certificates needed rotation")
                return True
                
        except Exception as e:
            logger.error(f"Certificate rotation failed: {e}")
            print(f"❌ Rotation error: {e}")
            return False
    
    async def check_certificate_health(self, output_format: str = "text") -> bool:
        """Check health of all certificates"""
        
        print("🏥 Checking certificate health...")
        
        try:
            dashboard_data = await self.monitoring.get_dashboard_data()
            
            if output_format.lower() == "json":
                print(json.dumps(dashboard_data, indent=2, default=str))
            else:
                # Text format
                health = dashboard_data.get('health', {})
                summary = health.get('summary', {})
                
                print(f"\n📊 Health Summary:")
                print(f"   Total Services: {summary.get('total_services', 0)}")
                print(f"   Healthy Services: {summary.get('healthy_services', 0)}")
                print(f"   Health Percentage: {summary.get('health_percentage', 0):.1f}%")
                
                # Show issues
                critical_issues = health.get('critical_issues', [])
                if critical_issues:
                    print(f"\n🚨 Critical Issues:")
                    for issue in critical_issues:
                        print(f"   - {issue}")
                
                # Certificate status
                certificates = dashboard_data.get('certificates', {})
                expiring_soon = []
                expired = []
                
                for service, cert_info in certificates.items():
                    days = cert_info['days_until_expiry']
                    if days <= 0:
                        expired.append(service)
                    elif days <= 30:
                        expiring_soon.append((service, days))
                
                if expired:
                    print(f"\n❌ Expired Certificates:")
                    for service in expired:
                        print(f"   - {service}")
                
                if expiring_soon:
                    print(f"\n⚠️ Expiring Soon:")
                    for service, days in sorted(expiring_soon, key=lambda x: x[1]):
                        print(f"   - {service}: {days} days")
            
            return len(dashboard_data.get('health', {}).get('critical_issues', [])) == 0
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            print(f"❌ Health check error: {e}")
            return False
    
    async def export_certificates(self, output_dir: str, format: str = "pem") -> bool:
        """Export certificates to specified directory"""
        
        print(f"📦 Exporting certificates to: {output_dir}")
        
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
                        "certificate": bundle.certificate.decode('utf-8'),
                        "private_key": bundle.private_key.decode('utf-8'),
                        "ca_certificate": bundle.ca_certificate.decode('utf-8'),
                        "metadata": {
                            "serial_number": bundle.metadata.serial_number,
                            "expires_at": bundle.metadata.expires_at.isoformat(),
                            "status": bundle.metadata.status.value,
                            "san_domains": bundle.metadata.san_domains
                        }
                    }
                    
                    (service_dir / "certificate.json").write_text(
                        json.dumps(cert_data, indent=2)
                    )
            
            print(f"✅ Exported {len(certificates)} certificates in {format.upper()} format")
            return True
            
        except Exception as e:
            logger.error(f"Certificate export failed: {e}")
            print(f"❌ Export error: {e}")
            return False
    
    async def monitor_certificates(self, duration_hours: int = 24) -> bool:
        """Monitor certificates for specified duration"""
        
        print(f"📊 Starting certificate monitoring for {duration_hours} hours...")
        
        try:
            await self.monitoring.start_monitoring()
            
            end_time = datetime.utcnow() + timedelta(hours=duration_hours)
            
            while datetime.utcnow() < end_time:
                # Get current status
                dashboard_data = await self.monitoring.get_dashboard_data()
                
                # Print status update
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                alerts = dashboard_data.get('alerts', {})
                health = dashboard_data.get('health', {}).get('summary', {})
                
                print(f"\n[{timestamp}] Status Update:")
                print(f"   Health: {health.get('health_percentage', 0):.1f}%")
                print(f"   Active Alerts: {alerts.get('total', 0)}")
                
                # Show any critical alerts
                recent_alerts = alerts.get('recent', [])
                critical_alerts = [a for a in recent_alerts if a['level'] == 'critical']
                if critical_alerts:
                    print(f"   🚨 Critical Alerts: {len(critical_alerts)}")
                
                # Wait 5 minutes
                await asyncio.sleep(300)
            
            print(f"✅ Monitoring completed")
            return True
            
        except Exception as e:
            logger.error(f"Monitoring failed: {e}")
            print(f"❌ Monitoring error: {e}")
            return False
    
    async def backup_certificates(self, backup_dir: str) -> bool:
        """Backup all certificates and CA"""
        
        print(f"💾 Backing up certificates to: {backup_dir}")
        
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_path / f"mtls_backup_{timestamp}.json"
            
            # Export CA
            ca_data = {
                "ca_certificate": self.mtls_manager.ca.export_ca_certificate().decode('utf-8'),
                "ca_key": self.mtls_manager.ca.export_ca_key().decode('utf-8')
            }
            
            # Export all certificates
            certificates = await self.mtls_manager.list_all_certificates()
            cert_data = {}
            
            for service_name in certificates.keys():
                bundle = await self.mtls_manager.store.load_certificate(service_name)
                if bundle:
                    cert_data[service_name] = {
                        "certificate": bundle.certificate.decode('utf-8'),
                        "private_key": bundle.private_key.decode('utf-8'),
                        "metadata": {
                            "serial_number": bundle.metadata.serial_number,
                            "expires_at": bundle.metadata.expires_at.isoformat(),
                            "status": bundle.metadata.status.value,
                            "san_domains": bundle.metadata.san_domains
                        }
                    }
            
            backup_data = {
                "backup_timestamp": datetime.utcnow().isoformat(),
                "ca_data": ca_data,
                "certificates": cert_data
            }
            
            backup_file.write_text(json.dumps(backup_data, indent=2))
            
            print(f"✅ Backed up {len(cert_data)} certificates")
            print(f"   Backup file: {backup_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            print(f"❌ Backup error: {e}")
            return False
    
    async def _load_config(self, config_file: Optional[str]) -> Dict[str, Any]:
        """Load configuration file"""
        
        if not config_file:
            return {}
        
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")
        
        if config_path.suffix.lower() in ['.yaml', '.yml']:
            return yaml.safe_load(config_path.read_text())
        elif config_path.suffix.lower() == '.json':
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
        """
    )
    
    # Global options
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    parser.add_argument('--config', '-c', type=str,
                       help='Configuration file path')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Bootstrap command
    bootstrap_parser = subparsers.add_parser('bootstrap', 
                                           help='Bootstrap cluster mTLS')
    bootstrap_parser.add_argument('--config', type=str,
                                help='Cluster configuration file')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate',
                                          help='Generate service certificate')
    generate_parser.add_argument('--service', required=True,
                               help='Service name')
    generate_parser.add_argument('--type', required=True,
                               help='Service type')
    generate_parser.add_argument('--sans', nargs='*',
                               help='Additional SAN domains')
    
    # Rotate command
    rotate_parser = subparsers.add_parser('rotate',
                                        help='Rotate certificates')
    rotate_parser.add_argument('--services', type=str,
                             help='Comma-separated service names (all if not specified)')
    
    # Health command
    health_parser = subparsers.add_parser('health',
                                        help='Check certificate health')
    health_parser.add_argument('--format', choices=['text', 'json'], default='text',
                             help='Output format')
    
    # Export command
    export_parser = subparsers.add_parser('export',
                                        help='Export certificates')
    export_parser.add_argument('--output', required=True,
                             help='Output directory')
    export_parser.add_argument('--format', choices=['pem', 'json'], default='pem',
                             help='Export format')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor',
                                         help='Monitor certificates')
    monitor_parser.add_argument('--duration', type=int, default=24,
                              help='Monitoring duration in hours')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup',
                                        help='Backup certificates')
    backup_parser.add_argument('--output', required=True,
                             help='Backup directory')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Initialize CLI
    cli = MTLSAutomationCLI()
    
    try:
        success = False
        
        if args.command == 'bootstrap':
            success = await cli.bootstrap_cluster(args.config)
        
        elif args.command == 'generate':
            success = await cli.generate_service_certificate(
                args.service, args.type, args.sans
            )
        
        elif args.command == 'rotate':
            services = args.services.split(',') if args.services else None
            success = await cli.rotate_certificates(services)
        
        elif args.command == 'health':
            success = await cli.check_certificate_health(args.format)
        
        elif args.command == 'export':
            success = await cli.export_certificates(args.output, args.format)
        
        elif args.command == 'monitor':
            success = await cli.monitor_certificates(args.duration)
        
        elif args.command == 'backup':
            success = await cli.backup_certificates(args.output)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        print(f"💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main())) 