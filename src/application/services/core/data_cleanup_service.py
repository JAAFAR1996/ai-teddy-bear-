from .cleanup.notification_service import NotificationService
from .cleanup.cleanup_execution_service import CleanupExecutionService
from .cleanup.target_identification_service import TargetIdentificationService
from .cleanup.backup_service import BackupService
from ...domain.cleanup.models import DataRetentionPolicy, CleanupReport
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
import asyncio
import json
import sys
import argparse


try:
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import create_engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

try:
    from ...domain.services.advanced_emotion_analyzer import DatabaseEmotionService
    EMOTION_DB_AVAILABLE = True
except ImportError:
    EMOTION_DB_AVAILABLE = False


class AdvancedDataCleanupService:
    """
    Advanced data cleanup service - refactored and improved.
    """

    def __init__(
        self,
        database_url: str = "sqlite:///teddy_cleanup.db",
        policy: Optional[DataRetentionPolicy] = None,
        backup_directory: str = "data_backups",
        log_directory: str = "cleanup_logs"
    ):
        self.database_url = database_url
        self.policy = policy or DataRetentionPolicy()
        self._init_database()
        self._setup_logging()
        self.emotion_db_service = None
        if EMOTION_DB_AVAILABLE:
            try:
                self.emotion_db_service = DatabaseEmotionService(database_url)
            except Exception as e:
                self.logger.warning(
                    f"Could not initialize emotion database: {e}")

        self.backup_directory = Path(backup_directory)
        self.backup_service = BackupService(backup_directory)
        self.target_service = TargetIdentificationService(
            self.emotion_db_service)
        self.execution_service = CleanupExecutionService(
            self.emotion_db_service)
        self.notification_service = NotificationService(log_directory)

    def _init_database(self):
        """Initializes the database connection."""
        if SQLALCHEMY_AVAILABLE:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                pool_recycle=300,
                echo=False
            )
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
        else:
            self.engine = None
            self.SessionLocal = None

    def _setup_logging(self):
        """Sets up logging."""
        self.logger = logging.getLogger(self.__class__.__name__)

    @asynccontextmanager
    async def get_db_session(self):
        """Gets a database session."""
        if not self.SessionLocal:
            raise RuntimeError("Database not initialized")
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    async def delete_old_data(self, days: int = 30, dry_run: bool = False) -> CleanupReport:
        custom_policy = DataRetentionPolicy(
            conversations_retention_days=days,
            messages_retention_days=days,
            emotional_states_retention_days=days,
            audio_files_retention_days=days
        )
        return await self.run_comprehensive_cleanup(custom_policy, dry_run=dry_run)

    async def run_comprehensive_cleanup(
        self,
        policy: Optional[DataRetentionPolicy] = None,
        dry_run: bool = False
    ) -> CleanupReport:
        cleanup_policy = policy or self.policy
        report = CleanupReport(policy=cleanup_policy)
        self.logger.info(
            f"Starting {'DRY RUN' if dry_run else 'LIVE'} cleanup operation")
        try:
            targets = await self.target_service.identify_cleanup_targets(
                cleanup_policy,
                report,
                self.get_db_session
            )
            if not dry_run and cleanup_policy.notify_parents_before_delete:
                await self.notification_service.notify_parents_before_cleanup(targets, report)
            if not dry_run and cleanup_policy.backup_before_delete:
                await self.backup_service.create_backups(targets, report, self.get_db_session)
            if not dry_run:
                await self.execution_service.execute_cleanup(targets, report, self.get_db_session)
            else:
                self.logger.info(
                    f"DRY RUN: Would delete {len(targets)} records")
            if not dry_run:
                await self.notification_service.generate_parent_cleanup_reports(report)
            report.mark_completed()
            self.logger.info("Cleanup operation completed successfully")
        except Exception as e:
            error_msg = f"Cleanup operation failed: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            report.mark_failed(error_msg)
        await self.notification_service.save_cleanup_report(report)
        return report

    async def get_cleanup_preview(
        self,
        policy: Optional[DataRetentionPolicy] = None
    ) -> dict:
        cleanup_policy = policy or self.policy
        try:
            targets = await self.target_service.identify_cleanup_targets(
                cleanup_policy,
                CleanupReport(policy=cleanup_policy),
                self.get_db_session
            )
            return await self.notification_service.get_cleanup_preview(targets, cleanup_policy)
        except Exception as e:
            self.logger.error(f"Error generating cleanup preview: {e}")
            return {
                "error": str(e),
                "total_records": 0,
                "policy": cleanup_policy.to_dict()
            }

    async def schedule_automatic_cleanup(self, interval_hours: int = 24):
        self.logger.info(
            f"Scheduling automatic cleanup every {interval_hours} hours")
        while True:
            try:
                await asyncio.sleep(interval_hours * 3600)
                self.logger.info("Running scheduled automatic cleanup")
                report = await self.run_comprehensive_cleanup()
                if report.status == "completed":
                    self.logger.info(
                        f"Automatic cleanup completed: {report.total_records_deleted} records deleted")
                else:
                    self.logger.warning(
                        f"Automatic cleanup failed: {report.errors}")
            except asyncio.CancelledError:
                self.logger.info("Automatic cleanup schedule cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error in automatic cleanup: {e}")


_cleanup_service_instance = None


def get_cleanup_service(
    database_url: str = "sqlite:///teddy_cleanup.db",
    policy: Optional[DataRetentionPolicy] = None
) -> "AdvancedDataCleanupService":
    global _cleanup_service_instance
    if _cleanup_service_instance is None:
        _cleanup_service_instance = AdvancedDataCleanupService(
            database_url, policy)
    return _cleanup_service_instance


async def delete_old_data_wrapper(days: int = 30, dry_run: bool = False) -> CleanupReport:
    service = get_cleanup_service()
    return await service.delete_old_data(days, dry_run)


async def run_cleanup_preview_wrapper(policy: Optional[DataRetentionPolicy] = None) -> Dict[str, Any]:
    service = get_cleanup_service()
    return await service.get_cleanup_preview(policy)


async def run_full_cleanup_wrapper(
    policy: Optional[DataRetentionPolicy] = None,
    dry_run: bool = False
) -> CleanupReport:
    service = get_cleanup_service()
    return await service.run_comprehensive_cleanup(policy, dry_run)


async def emergency_cleanup(max_size_gb: float = 5.0) -> CleanupReport:
    emergency_policy = DataRetentionPolicy(
        conversations_retention_days=7,
        messages_retention_days=7,
        emotional_states_retention_days=14,
        audio_files_retention_days=1,
        backup_before_delete=False,
        notify_parents_before_delete=False
    )
    service = get_cleanup_service()
    service.logger.warning(
        f"Running EMERGENCY cleanup - database size limit: {max_size_gb}GB")
    return await service.run_comprehensive_cleanup(emergency_policy, dry_run=False)


async def compliance_cleanup(regulation: str = "gdpr") -> CleanupReport:
    if regulation.lower() == "gdpr":
        policy = DataRetentionPolicy(
            conversations_retention_days=30,
            messages_retention_days=30,
            emotional_states_retention_days=30,
            audio_files_retention_days=7,
            backup_before_delete=True,
            notify_parents_before_delete=True,
            gdpr_compliant=True
        )
    elif regulation.lower() == "coppa":
        policy = DataRetentionPolicy(
            conversations_retention_days=14,
            messages_retention_days=14,
            emotional_states_retention_days=30,
            audio_files_retention_days=3,
            backup_before_delete=True,
            notify_parents_before_delete=True,
            coppa_compliant=True
        )
    else:
        policy = DataRetentionPolicy(
            conversations_retention_days=21,
            messages_retention_days=21,
            emotional_states_retention_days=45,
            audio_files_retention_days=5
        )
    service = get_cleanup_service()
    service.logger.info(f"Running {regulation.upper()} compliance cleanup")
    return await service.run_comprehensive_cleanup(policy, dry_run=False)


def create_custom_policy(**kwargs) -> DataRetentionPolicy:
    return DataRetentionPolicy(**kwargs)


def _calculate_directory_size(path: Path) -> int:
    """Calculates the total size of a directory in bytes."""
    if not path.exists() or not path.is_dir():
        return 0
    return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())


def _get_db_files_size(db_files: List[Path]) -> tuple[Dict[str, Dict[str, Any]], float]:
    """Calculates the size of database files."""
    db_files_info = {}
    total_size_mb = 0
    for db_file in db_files:
        if db_file.exists():
            size_bytes = db_file.stat().st_size
            size_mb = round(size_bytes / (1024 * 1024), 2)
            db_files_info[str(db_file)] = {
                "size_bytes": size_bytes, "size_mb": size_mb}
            total_size_mb += size_mb
    return db_files_info, total_size_mb


def _generate_size_recommendations(total_gb: float, backup_mb: float, cache_mb: float) -> List[str]:
    """Generates recommendations based on storage sizes."""
    recommendations = []
    if total_gb > 5.0:
        recommendations.append(
            "Database size is large (>5GB). Consider emergency cleanup.")
    if backup_mb > 1000:
        recommendations.append(
            "Backup directory is large (>1GB). Consider cleaning old backups.")
    if cache_mb > 500:
        recommendations.append(
            "Cache directory is large (>500MB). Consider cache cleanup.")
    if not recommendations:
        recommendations.append("Database size is within normal limits.")
    return recommendations


async def get_database_size_info() -> Dict[str, Any]:
    """Gets database size information."""
    try:
        service = get_cleanup_service()
        db_files = [Path("teddy_cleanup.db"), Path(
            "database.db"), Path("emotions.db")]
        db_files_info, total_db_size_mb = _get_db_files_size(db_files)
        backup_size_mb = round(_calculate_directory_size(
            service.backup_directory) / (1024 * 1024), 2)
        cache_dirs = [Path("cache"), Path("temp"), Path("uploads")]
        cache_size_mb = round(sum(_calculate_directory_size(p)
                              for p in cache_dirs) / (1024 * 1024), 2)
        total_size_mb = total_db_size_mb + backup_size_mb + cache_size_mb
        recommendations = _generate_size_recommendations(
            total_size_mb / 1024, backup_size_mb, cache_size_mb)
        return {
            "database_files": db_files_info,
            "total_size_mb": round(total_size_mb, 2),
            "backup_size_mb": backup_size_mb,
            "cache_size_mb": cache_size_mb,
            "recommendations": recommendations,
        }
    except Exception as e:
        return {
            "error": str(e),
            "total_size_mb": 0,
            "recommendations": ["Error checking database size"]
        }


async def main():
    """Main function to run the cleanup service from CLI."""
    parser = argparse.ArgumentParser(
        description="AI Teddy Bear Data Cleanup Service")
    parser.add_argument("--action", choices=["preview", "cleanup", "emergency",
                        "compliance", "size"], default="preview", help="Action to perform")
    parser.add_argument("--days", type=int, default=30,
                        help="Days to keep data")
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview only, don't delete")
    parser.add_argument("--regulation", choices=["gdpr", "coppa", "ccpa"],
                        default="gdpr", help="Compliance regulation for cleanup")
    parser.add_argument("--schedule", action="store_true",
                        help="Run scheduled cleanup")
    parser.add_argument("--schedule-hours", type=int,
                        default=24, help="Schedule interval in hours")
    args = parser.parse_args()
    try:
        if args.action == "preview":
            print("Generating cleanup preview...")
            preview = await run_cleanup_preview_wrapper()
            print(json.dumps(preview, indent=2, ensure_ascii=False))
        elif args.action == "cleanup":
            print(f"Running cleanup (keeping data for {args.days} days)...")
            report = await delete_old_data_wrapper(args.days, args.dry_run)
            print(
                f"Cleanup completed: {report.total_records_deleted} records deleted")
            print(
                f"Size freed: {round(report.total_size_freed_bytes / 1024 / 1024, 2)} MB")
            if report.errors:
                print(f"Errors: {len(report.errors)}")
                for error in report.errors[-3:]:
                    print(f"    - {error}")
        elif args.action == "emergency":
            print("Running EMERGENCY cleanup...")
            report = await emergency_cleanup()
            print(
                f"Emergency cleanup completed: {report.total_records_deleted} records deleted")
        elif args.action == "compliance":
            print(f"Running {args.regulation.upper()} compliance cleanup...")
            report = await compliance_cleanup(args.regulation)
            print(
                f"Compliance cleanup completed: {report.total_records_deleted} records deleted")
        elif args.action == "size":
            print("Checking database size...")
            size_info = await get_database_size_info()
            print(json.dumps(size_info, indent=2, ensure_ascii=False))
        if args.schedule:
            print(
                f"Starting scheduled cleanup every {args.schedule_hours} hours...")
            service = get_cleanup_service()
            await service.schedule_automatic_cleanup(args.schedule_hours)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


async def test_cleanup_service():
    """Tests the cleanup service."""
    print("Testing Data Cleanup Service...")
    try:
        print("1. Testing service initialization...")
        service = get_cleanup_service()
        assert service is not None
        print("    - Service initialized successfully")
        print("2. Testing cleanup preview...")
        preview = await service.get_cleanup_preview()
        assert isinstance(preview, dict)
        assert "total_records" in preview
        print(
            f"    - Preview generated: {preview['total_records']} records found")
        print("3. Testing dry run cleanup...")
        report = await service.delete_old_data(days=1, dry_run=True)
        assert isinstance(report, CleanupReport)
        assert report.status in ["completed", "failed"]
        print(
            f"    - Dry run completed: {report.total_records_scanned} records scanned")
        print("4. Testing database size check...")
        size_info = await get_database_size_info()
        assert isinstance(size_info, dict)
        print(
            f"    - Size check completed: {size_info.get('total_size_mb', 0)} MB")
        print("5. Testing custom policy creation...")
        custom_policy = create_custom_policy(
            conversations_retention_days=15,
            emotional_states_retention_days=45
        )
        assert custom_policy.conversations_retention_days == 15
        assert custom_policy.emotional_states_retention_days == 45
        print("    - Custom policy created successfully")
        print("\nAll tests passed!")
        return True
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_cleanup_service())
    else:
        asyncio.run(main())
