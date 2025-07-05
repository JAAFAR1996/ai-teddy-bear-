뿃뻃#!/usr/bin/env python3਍ഀ
"""਍ഀ
Advanced Data Cleanup Service for AI Teddy Bear Project਍ഀ
Refactored and optimized for maintainability and performance਍ഀ
"""਍ഀ
਍ഀ
import asyncio਍ഀ
import logging਍ഀ
from pathlib import Path਍ഀ
from typing import Optional਍ഀ
from contextlib import asynccontextmanager਍ഀ
਍ഀ
# Third-party imports਍ഀ
try:਍ഀ
    from sqlalchemy.orm import sessionmaker਍ഀ
    from sqlalchemy import create_engine਍ഀ
    SQLALCHEMY_AVAILABLE = True਍ഀ
except ImportError:਍ഀ
    SQLALCHEMY_AVAILABLE = False਍ഀ
਍ഀ
# Import enhanced emotion analyzer for database integration਍ഀ
try:਍ഀ
    from ..domain.services.advanced_emotion_analyzer import DatabaseEmotionService਍ഀ
    EMOTION_DB_AVAILABLE = True਍ഀ
except ImportError:਍ഀ
    EMOTION_DB_AVAILABLE = False਍ഀ
਍ഀ
# Domain models਍ഀ
from ...domain.cleanup.models import DataRetentionPolicy, CleanupReport਍ഀ
਍ഀ
# Application services਍ഀ
from .cleanup.backup_service import BackupService਍ഀ
from .cleanup.target_identification_service import TargetIdentificationService਍ഀ
from .cleanup.cleanup_execution_service import CleanupExecutionService਍ഀ
from .cleanup.notification_service import NotificationService਍ഀ
਍ഀ
਍ഀ
class AdvancedDataCleanupService:਍ഀ
    """਍ഀ
    خدمة تنظيف البيانات المتقدمة - مُعاد تنظيمها وتحسينها਍ഀ
    ਍ഀ
    Features:਍ഀ
    - استخدام معمارية الخدمات المُقسمة਍ഀ
    - تنظيم أفضل وقابلية صيانة عالية਍ഀ
    - فصل المسؤوليات (SRP)਍ഀ
    - سهولة في الاختبار والتطوير਍ഀ
    """਍ഀ
    ਍ഀ
    def __init__(਍ഀ
        self, ਍ഀ
        database_url: str = "sqlite:///teddy_cleanup.db",਍ഀ
        policy: Optional[DataRetentionPolicy] = None,਍ഀ
        backup_directory: str = "data_backups",਍ഀ
        log_directory: str = "cleanup_logs"਍ഀ
    ):਍ഀ
        self.database_url = database_url਍ഀ
        self.policy = policy or DataRetentionPolicy()਍ഀ
        ਍ഀ
        # Initialize database connection਍ഀ
        self._init_database()਍ഀ
        ਍ഀ
        # Setup logging਍ഀ
        self._setup_logging()਍ഀ
        ਍ഀ
        # Initialize emotion database service if available਍ഀ
        self.emotion_db_service = None਍ഀ
        if EMOTION_DB_AVAILABLE:਍ഀ
            try:਍ഀ
                self.emotion_db_service = DatabaseEmotionService(database_url)਍ഀ
            except Exception as e:਍ഀ
                self.logger.warning(f"Could not initialize emotion database: {e}")਍ഀ
        ਍ഀ
        # Initialize service components਍ഀ
        self.backup_service = BackupService(backup_directory)਍ഀ
        self.target_service = TargetIdentificationService(self.emotion_db_service)਍ഀ
        self.execution_service = CleanupExecutionService(self.emotion_db_service)਍ഀ
        self.notification_service = NotificationService(log_directory)਍ഀ
    ਍ഀ
    def _init_database(self):਍ഀ
        """تهيئة اتصال قاعدة البيانات"""਍ഀ
        if SQLALCHEMY_AVAILABLE:਍ഀ
            self.engine = create_engine(਍ഀ
                self.database_url,਍ഀ
                pool_pre_ping=True,਍ഀ
                pool_recycle=300,਍ഀ
                echo=False਍ഀ
            )਍ഀ
            self.SessionLocal = sessionmaker(਍ഀ
                autocommit=False,਍ഀ
                autoflush=False,਍ഀ
                bind=self.engine਍ഀ
            )਍ഀ
        else:਍ഀ
            self.engine = None਍ഀ
            self.SessionLocal = None਍ഀ
    ਍ഀ
    def _setup_logging(self):਍ഀ
        """إعداد نظام التسجيل"""਍ഀ
        self.logger = logging.getLogger(self.__class__.__name__)਍ഀ
    ਍ഀ
    @asynccontextmanager਍ഀ
    async def get_db_session(self):਍ഀ
        """الحصول على جلسة قاعدة البيانات"""਍ഀ
        if not self.SessionLocal:਍ഀ
            raise RuntimeError("Database not initialized")਍ഀ
        ਍ഀ
        session = self.SessionLocal()਍ഀ
        try:਍ഀ
            yield session਍ഀ
            session.commit()਍ഀ
        except Exception as e:਍ഀ
            session.rollback()਍ഀ
            raise e਍ഀ
        finally:਍ഀ
            session.close()਍ഀ
    ਍ഀ
    async def delete_old_data(self, days: int = 30, dry_run: bool = False) -> CleanupReport:਍ഀ
        """਍ഀ
        حذف البيانات القديمة਍ഀ
        ਍ഀ
        Args:਍ഀ
            days: عدد الأيام للاحتفاظ بالبيانات਍ഀ
            dry_run: تشغيل تجريبي بدون حذف فعلي਍ഀ
        ਍ഀ
        Returns:਍ഀ
            CleanupReport: تقرير شامل لعملية التنظيف਍ഀ
        """਍ഀ
        ਍ഀ
        # Create custom policy for this operation਍ഀ
        custom_policy = DataRetentionPolicy(਍ഀ
            conversations_retention_days=days,਍ഀ
            messages_retention_days=days,਍ഀ
            emotional_states_retention_days=days,਍ഀ
            audio_files_retention_days=days਍ഀ
        )਍ഀ
        ਍ഀ
        return await self.run_comprehensive_cleanup(custom_policy, dry_run=dry_run)਍ഀ
    ਍ഀ
    async def run_comprehensive_cleanup(਍ഀ
        self, ਍ഀ
        policy: Optional[DataRetentionPolicy] = None,਍ഀ
        dry_run: bool = False਍ഀ
    ) -> CleanupReport:਍ഀ
        """਍ഀ
        تشغيل عملية تنظيف شاملة - الآن مُعاد تنظيمها਍ഀ
        ਍ഀ
        Args:਍ഀ
            policy: سياسة الاحتفاظ بالبيانات਍ഀ
            dry_run: تشغيل تجريبي بدون حذف فعلي਍ഀ
        ਍ഀ
        Returns:਍ഀ
            CleanupReport: تقرير العملية਍ഀ
        """਍ഀ
        ਍ഀ
        cleanup_policy = policy or self.policy਍ഀ
        report = CleanupReport(policy=cleanup_policy)਍ഀ
        ਍ഀ
        self.logger.info(f"Starting {'DRY RUN' if dry_run else 'LIVE'} cleanup operation")਍ഀ
        ਍ഀ
        try:਍ഀ
            # Phase 1: Identify targets for cleanup਍ഀ
            targets = await self.target_service.identify_cleanup_targets(਍ഀ
                cleanup_policy, ਍ഀ
                report, ਍ഀ
                self.get_db_session਍ഀ
            )਍ഀ
            ਍ഀ
            # Phase 2: Notify parents if required਍ഀ
            if not dry_run and cleanup_policy.notify_parents_before_delete:਍ഀ
                await self.notification_service.notify_parents_before_cleanup(targets, report)਍ഀ
            ਍ഀ
            # Phase 3: Create backups if required਍ഀ
            if not dry_run and cleanup_policy.backup_before_delete:਍ഀ
                await self.backup_service.create_backups(targets, report, self.get_db_session)਍ഀ
            ਍ഀ
            # Phase 4: Execute cleanup਍ഀ
            if not dry_run:਍ഀ
                await self.execution_service.execute_cleanup(targets, report, self.get_db_session)਍ഀ
            else:਍ഀ
                self.logger.info(f"DRY RUN: Would delete {len(targets)} records")਍ഀ
            ਍ഀ
            # Phase 5: Generate parent notifications਍ഀ
            if not dry_run:਍ഀ
                await self.notification_service.generate_parent_cleanup_reports(report)਍ഀ
            ਍ഀ
            report.mark_completed()਍ഀ
            self.logger.info(f"Cleanup operation completed successfully")਍ഀ
            ਍ഀ
        except Exception as e:਍ഀ
            error_msg = f"Cleanup operation failed: {str(e)}"਍ഀ
            self.logger.error(error_msg, exc_info=True)਍ഀ
            report.mark_failed(error_msg)਍ഀ
        ਍ഀ
        # Save cleanup report਍ഀ
        await self.notification_service.save_cleanup_report(report)਍ഀ
        ਍ഀ
        return report਍ഀ
    ਍ഀ
    async def get_cleanup_preview(਍ഀ
        self, ਍ഀ
        policy: Optional[DataRetentionPolicy] = None਍ഀ
    ) -> dict:਍ഀ
        """معاينة البيانات المرشحة للحذف بدون حذف فعلي"""਍ഀ
        ਍ഀ
        cleanup_policy = policy or self.policy਍ഀ
        ਍ഀ
        try:਍ഀ
            # Get targets without executing cleanup਍ഀ
            targets = await self.target_service.identify_cleanup_targets(਍ഀ
                cleanup_policy, ਍ഀ
                CleanupReport(policy=cleanup_policy), ਍ഀ
                self.get_db_session਍ഀ
            )਍ഀ
            ਍ഀ
            # Generate preview using notification service਍ഀ
            return await self.notification_service.get_cleanup_preview(targets, cleanup_policy)਍ഀ
            ਍ഀ
        except Exception as e:਍ഀ
            self.logger.error(f"Error generating cleanup preview: {e}")਍ഀ
            return {਍ഀ
                "error": str(e),਍ഀ
                "total_records": 0,਍ഀ
                "policy": cleanup_policy.to_dict()਍ഀ
            }਍ഀ
    ਍ഀ
    async def schedule_automatic_cleanup(self, interval_hours: int = 24):਍ഀ
        """جدولة التنظيف التلقائي"""਍ഀ
        ਍ഀ
        self.logger.info(f"Scheduling automatic cleanup every {interval_hours} hours")਍ഀ
        ਍ഀ
        while True:਍ഀ
            try:਍ഀ
                await asyncio.sleep(interval_hours * 3600)਍ഀ
                ਍ഀ
                self.logger.info("Running scheduled automatic cleanup")਍ഀ
                report = await self.run_comprehensive_cleanup()਍ഀ
                ਍ഀ
                if report.status == "completed":਍ഀ
                    self.logger.info(f"Automatic cleanup completed: {report.total_records_deleted} records deleted")਍ഀ
                else:਍ഀ
                    self.logger.warning(f"Automatic cleanup failed: {report.errors}")਍ഀ
            ਍ഀ
            except asyncio.CancelledError:਍ഀ
                self.logger.info("Automatic cleanup schedule cancelled")਍ഀ
                break਍ഀ
            except Exception as e:਍ഀ
                self.logger.error(f"Error in automatic cleanup: {e}")਍ഀ
                # Continue with schedule despite errors਍ഀ
    ਍ഀ
਍ഀ
    ਍ഀ
਍ഀ
    ਍ഀ
# Convenience functions and global service instance਍ഀ
਍ഀ
# Global service instance਍ഀ
_cleanup_service_instance = None਍ഀ
਍ഀ
def get_cleanup_service(਍ഀ
    database_url: str = "sqlite:///teddy_cleanup.db",਍ഀ
    policy: Optional[DataRetentionPolicy] = None਍ഀ
) -> AdvancedDataCleanupService:਍ഀ
    """الحصول على مثيل خدمة التنظيف"""਍ഀ
    global _cleanup_service_instance਍ഀ
    ਍ഀ
    if _cleanup_service_instance is None:਍ഀ
        _cleanup_service_instance = AdvancedDataCleanupService(database_url, policy)਍ഀ
    ਍ഀ
    return _cleanup_service_instance਍ഀ
਍ഀ
਍ഀ
async def delete_old_data(days: int = 30, dry_run: bool = False) -> CleanupReport:਍ഀ
    """਍ഀ
    دالة ملائمة لحذف البيانات القديمة਍ഀ
    ਍ഀ
    Args:਍ഀ
        days: عدد الأيام للاحتفاظ بالبيانات਍ഀ
        dry_run: تشغيل تجريبي بدون حذف فعلي਍ഀ
    ਍ഀ
    Returns:਍ഀ
        CleanupReport: تقرير العملية਍ഀ
    """਍ഀ
    service = get_cleanup_service()਍ഀ
    return await service.delete_old_data(days, dry_run)਍ഀ
਍ഀ
਍ഀ
async def run_cleanup_preview(policy: Optional[DataRetentionPolicy] = None) -> Dict[str, Any]:਍ഀ
    """معاينة البيانات المرشحة للحذف"""਍ഀ
    service = get_cleanup_service()਍ഀ
    return await service.get_cleanup_preview(policy)਍ഀ
਍ഀ
਍ഀ
async def run_full_cleanup(਍ഀ
    policy: Optional[DataRetentionPolicy] = None,਍ഀ
    dry_run: bool = False਍ഀ
) -> CleanupReport:਍ഀ
    """تشغيل تنظيف شامل"""਍ഀ
    service = get_cleanup_service()਍ഀ
    return await service.run_comprehensive_cleanup(policy, dry_run)਍ഀ
਍ഀ
਍ഀ
# CLI and Testing Functions਍ഀ
਍ഀ
async def emergency_cleanup(max_size_gb: float = 5.0) -> CleanupReport:਍ഀ
    """਍ഀ
    تنظيف طارئ عند امتلاء التخزين਍ഀ
    ਍ഀ
    Args:਍ഀ
        max_size_gb: الحد الأقصى لحجم قاعدة البيانات بالجيجابايت਍ഀ
    ਍ഀ
    Returns:਍ഀ
        CleanupReport: تقرير العملية਍ഀ
    """਍ഀ
    emergency_policy = DataRetentionPolicy(਍ഀ
        conversations_retention_days=7,਍ഀ
        messages_retention_days=7,਍ഀ
        emotional_states_retention_days=14,਍ഀ
        audio_files_retention_days=1,਍ഀ
        backup_before_delete=False,  # No backup in emergency਍ഀ
        notify_parents_before_delete=False਍ഀ
    )਍ഀ
    ਍ഀ
    service = get_cleanup_service()਍ഀ
    service.logger.warning(f"Running EMERGENCY cleanup - database size limit: {max_size_gb}GB")਍ഀ
    ਍ഀ
    return await service.run_comprehensive_cleanup(emergency_policy, dry_run=False)਍ഀ
਍ഀ
਍ഀ
async def compliance_cleanup(regulation: str = "gdpr") -> CleanupReport:਍ഀ
    """਍ഀ
    تنظيف للامتثال للوائح الخصوصية਍ഀ
    ਍ഀ
    Args:਍ഀ
        regulation: نوع اللائحة (gdpr, coppa, ccpa)਍ഀ
    ਍ഀ
    Returns:਍ഀ
        CleanupReport: تقرير العملية਍ഀ
    """਍ഀ
    ਍ഀ
    if regulation.lower() == "gdpr":਍ഀ
        # GDPR requires data minimization਍ഀ
        policy = DataRetentionPolicy(਍ഀ
            conversations_retention_days=30,਍ഀ
            messages_retention_days=30,਍ഀ
            emotional_states_retention_days=30,਍ഀ
            audio_files_retention_days=7,਍ഀ
            backup_before_delete=True,਍ഀ
            notify_parents_before_delete=True,਍ഀ
            gdpr_compliant=True਍ഀ
        )਍ഀ
    elif regulation.lower() == "coppa":਍ഀ
        # COPPA for children under 13਍ഀ
        policy = DataRetentionPolicy(਍ഀ
            conversations_retention_days=14,਍ഀ
            messages_retention_days=14,਍ഀ
            emotional_states_retention_days=30,਍ഀ
            audio_files_retention_days=3,਍ഀ
            backup_before_delete=True,਍ഀ
            notify_parents_before_delete=True,਍ഀ
            coppa_compliant=True਍ഀ
        )਍ഀ
    else:਍ഀ
        # Default conservative policy਍ഀ
        policy = DataRetentionPolicy(਍ഀ
            conversations_retention_days=21,਍ഀ
            messages_retention_days=21,਍ഀ
            emotional_states_retention_days=45,਍ഀ
            audio_files_retention_days=5਍ഀ
        )਍ഀ
    ਍ഀ
    service = get_cleanup_service()਍ഀ
    service.logger.info(f"Running {regulation.upper()} compliance cleanup")਍ഀ
    ਍ഀ
    return await service.run_comprehensive_cleanup(policy, dry_run=False)਍ഀ
਍ഀ
਍ഀ
def create_custom_policy(**kwargs) -> DataRetentionPolicy:਍ഀ
    """إنشاء سياسة مخصصة للاحتفاظ بالبيانات"""਍ഀ
    return DataRetentionPolicy(**kwargs)਍ഀ
਍ഀ
਍ഀ
async def get_database_size_info() -> Dict[str, Any]:਍ഀ
    """الحصول على معلومات حجم قاعدة البيانات"""਍ഀ
    ਍ഀ
    try:਍ഀ
        service = get_cleanup_service()਍ഀ
        size_info = {਍ഀ
            "database_files": {},਍ഀ
            "total_size_mb": 0,਍ഀ
            "backup_size_mb": 0,਍ഀ
            "cache_size_mb": 0,਍ഀ
            "recommendations": []਍ഀ
        }਍ഀ
        ਍ഀ
        # Check main database files਍ഀ
        db_files = [਍ഀ
            Path("teddy_cleanup.db"),਍ഀ
            Path("database.db"),਍ഀ
            Path("emotions.db")਍ഀ
        ]਍ഀ
        ਍ഀ
        for db_file in db_files:਍ഀ
            if db_file.exists():਍ഀ
                size_bytes = db_file.stat().st_size਍ഀ
                size_mb = round(size_bytes / 1024 / 1024, 2)਍ഀ
                size_info["database_files"][str(db_file)] = {਍ഀ
                    "size_bytes": size_bytes,਍ഀ
                    "size_mb": size_mb਍ഀ
                }਍ഀ
                size_info["total_size_mb"] += size_mb਍ഀ
        ਍ഀ
        # Check backup directory਍ഀ
        if service.backup_directory.exists():਍ഀ
            backup_size = sum(਍ഀ
                f.stat().st_size ਍ഀ
                for f in service.backup_directory.rglob("*") ਍ഀ
                if f.is_file()਍ഀ
            )਍ഀ
            size_info["backup_size_mb"] = round(backup_size / 1024 / 1024, 2)਍ഀ
        ਍ഀ
        # Check cache directories਍ഀ
        cache_dirs = [Path("cache"), Path("temp"), Path("uploads")]਍ഀ
        cache_size = 0਍ഀ
        for cache_dir in cache_dirs:਍ഀ
            if cache_dir.exists():਍ഀ
                cache_size += sum(਍ഀ
                    f.stat().st_size ਍ഀ
                    for f in cache_dir.rglob("*") ਍ഀ
                    if f.is_file()਍ഀ
                )਍ഀ
        size_info["cache_size_mb"] = round(cache_size / 1024 / 1024, 2)਍ഀ
        ਍ഀ
        # Generate recommendations਍ഀ
        total_size_gb = size_info["total_size_mb"] / 1024਍ഀ
        ਍ഀ
        if total_size_gb > 5.0:਍ഀ
            size_info["recommendations"].append("Database size is large (>5GB). Consider emergency cleanup.")਍ഀ
        ਍ഀ
        if size_info["backup_size_mb"] > 1000:਍ഀ
            size_info["recommendations"].append("Backup directory is large (>1GB). Consider cleaning old backups.")਍ഀ
        ਍ഀ
        if size_info["cache_size_mb"] > 500:਍ഀ
            size_info["recommendations"].append("Cache directory is large (>500MB). Consider cache cleanup.")਍ഀ
        ਍ഀ
        if not size_info["recommendations"]:਍ഀ
            size_info["recommendations"].append("Database size is within normal limits.")਍ഀ
        ਍ഀ
        return size_info਍ഀ
    ਍ഀ
    except Exception as e:਍ഀ
        return {਍ഀ
            "error": str(e),਍ഀ
            "total_size_mb": 0,਍ഀ
            "recommendations": ["Error checking database size"]਍ഀ
        }਍ഀ
਍ഀ
਍ഀ
# Main execution functions਍ഀ
਍ഀ
async def main():਍ഀ
    """دالة رئيسية لتشغيل خدمة التنظيف"""਍ഀ
    ਍ഀ
    import argparse਍ഀ
    import sys਍ഀ
    ਍ഀ
    parser = argparse.ArgumentParser(description="AI Teddy Bear Data Cleanup Service")਍ഀ
    parser.add_argument("--action", choices=["preview", "cleanup", "emergency", "compliance", "size"], ਍ഀ
                       default="preview", help="Action to perform")਍ഀ
    parser.add_argument("--days", type=int, default=30, help="Days to keep data")਍ഀ
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't delete")਍ഀ
    parser.add_argument("--regulation", choices=["gdpr", "coppa", "ccpa"], default="gdpr",਍ഀ
                       help="Compliance regulation for cleanup")਍ഀ
    parser.add_argument("--schedule", action="store_true", help="Run scheduled cleanup")਍ഀ
    parser.add_argument("--schedule-hours", type=int, default=24, help="Schedule interval in hours")਍ഀ
    ਍ഀ
    args = parser.parse_args()਍ഀ
    ਍ഀ
    try:਍ഀ
        if args.action == "preview":਍ഀ
            print("쌽඘쌊₝䜀攀渀攀爀愀琀椀渀最 挀氀攀愀渀甀瀀 瀀爀攀瘀椀攀眀⸀⸀⸀∀⤀ഀ
਍            瀀爀攀瘀椀攀眀 㴀 愀眀愀椀琀 爀甀渀开挀氀攀愀渀甀瀀开瀀爀攀瘀椀攀眀⠀⤀ഀ
਍            瀀爀椀渀琀⠀樀猀漀渀⸀搀甀洀瀀猀⠀瀀爀攀瘀椀攀眀Ⰰ 椀渀搀攀渀琀㴀㈀Ⰰ 攀渀猀甀爀攀开愀猀挀椀椀㴀䘀愀氀猀攀⤀⤀ഀ
਍        ഀ
਍        攀氀椀昀 愀爀最猀⸀愀挀琀椀漀渀 㴀㴀 ∀挀氀攀愀渀甀瀀∀㨀ഀ
਍            瀀爀椀渀琀⠀昀∀㸀飃맃鷃 Running cleanup (keeping data for {args.days} days)...")਍ഀ
            report = await delete_old_data(args.days, args.dry_run)਍ഀ
            print(f"✅ Cleanup completed: {report.total_records_deleted} records deleted")਍ഀ
            print(f"쌽쎘쎊ₜ匀椀稀攀 昀爀攀攀搀㨀 笀爀漀甀渀搀⠀爀攀瀀漀爀琀⸀琀漀琀愀氀开猀椀稀攀开昀爀攀攀搀开戀礀琀攀猀 ⼀ ㄀　㈀㐀 ⼀ ㄀　㈀㐀Ⰰ ㈀⤀紀 䴀䈀∀⤀ഀ
਍            ഀ
਍            椀昀 爀攀瀀漀爀琀⸀攀爀爀漀爀猀㨀ഀ
਍                瀀爀椀渀琀⠀昀∀숀⚠쌏₾䔀爀爀漀爀猀㨀 笀氀攀渀⠀爀攀瀀漀爀琀⸀攀爀爀漀爀猀⤀紀∀⤀ഀ
਍                昀漀爀 攀爀爀漀爀 椀渀 爀攀瀀漀爀琀⸀攀爀爀漀爀猀嬀ⴀ㌀㨀崀㨀  ⌀ 匀栀漀眀 氀愀猀琀 ㌀ 攀爀爀漀爀猀ഀ
਍                    瀀爀椀渀琀⠀昀∀   ⴀ 笀攀爀爀漀爀紀∀⤀ഀ
਍        ഀ
਍        攀氀椀昀 愀爀最猀⸀愀挀琀椀漀渀 㴀㴀 ∀攀洀攀爀最攀渀挀礀∀㨀ഀ
਍            瀀爀椀渀琀⠀∀㴀飃ꣂ黃 Running EMERGENCY cleanup...")਍ഀ
            report = await emergency_cleanup()਍ഀ
            print(f"✅ Emergency cleanup completed: {report.total_records_deleted} records deleted")਍ഀ
        ਍ഀ
        elif args.action == "compliance":਍ഀ
            print(f"雂༦뻃 Running {args.regulation.upper()} compliance cleanup...")਍ഀ
            report = await compliance_cleanup(args.regulation)਍ഀ
            print(f"✅ Compliance cleanup completed: {report.total_records_deleted} records deleted")਍ഀ
        ਍ഀ
        elif args.action == "size":਍ഀ
            print("쌽쎘쎊ₜ䌀栀攀挀欀椀渀最 搀愀琀愀戀愀猀攀 猀椀稀攀⸀⸀⸀∀⤀ഀ
਍            猀椀稀攀开椀渀昀漀 㴀 愀眀愀椀琀 最攀琀开搀愀琀愀戀愀猀攀开猀椀稀攀开椀渀昀漀⠀⤀ഀ
਍            瀀爀椀渀琀⠀樀猀漀渀⸀搀甀洀瀀猀⠀猀椀稀攀开椀渀昀漀Ⰰ 椀渀搀攀渀琀㴀㈀Ⰰ 攀渀猀甀爀攀开愀猀挀椀椀㴀䘀愀氀猀攀⤀⤀ഀ
਍        ഀ
਍        椀昀 愀爀最猀⸀猀挀栀攀搀甀氀攀㨀ഀ
਍            瀀爀椀渀琀⠀昀∀쌀⎰ Starting scheduled cleanup every {args.schedule_hours} hours...")਍ഀ
            service = get_cleanup_service()਍ഀ
            await service.schedule_automatic_cleanup(args.schedule_hours)਍ഀ
    ਍ഀ
    except KeyboardInterrupt:਍ഀ
        print("\n맃༣뻃 Operation cancelled by user")਍ഀ
        sys.exit(0)਍ഀ
    except Exception as e:਍ഀ
        print(f"❌ Error: {e}")਍ഀ
        sys.exit(1)਍ഀ
਍ഀ
਍ഀ
# Legacy compatibility functions਍ഀ
਍ഀ
cleanup_service = None  # Will be initialized when needed਍ഀ
਍ഀ
async def run_daily_cleanup():਍ഀ
    """تشغيل التنظيف اليومي (legacy function)"""਍ഀ
    return await delete_old_data(30, dry_run=False)਍ഀ
਍ഀ
async def preview_cleanup():਍ഀ
    """معاينة البيانات المرشحة للحذف (legacy function)"""਍ഀ
    return await run_cleanup_preview()਍ഀ
਍ഀ
਍ഀ
# Testing and demo functions਍ഀ
਍ഀ
async def test_cleanup_service():਍ഀ
    """اختبار خدمة التنظيف"""਍ഀ
    ਍ഀ
    print("쌾쎘쎪₝吀攀猀琀椀渀最 䐀愀琀愀 䌀氀攀愀渀甀瀀 匀攀爀瘀椀挀攀⸀⸀⸀∀⤀ഀ
਍    ഀ
਍    琀爀礀㨀ഀ
਍        ⌀ 吀攀猀琀 ㄀㨀 匀攀爀瘀椀挀攀 椀渀椀琀椀愀氀椀稀愀琀椀漀渀ഀ
਍        瀀爀椀渀琀⠀∀㄀⸀ 吀攀猀琀椀渀最 猀攀爀瘀椀挀攀 椀渀椀琀椀愀氀椀稀愀琀椀漀渀⸀⸀⸀∀⤀ഀ
਍        猀攀爀瘀椀挀攀 㴀 最攀琀开挀氀攀愀渀甀瀀开猀攀爀瘀椀挀攀⠀⤀ഀ
਍        愀猀猀攀爀琀 猀攀爀瘀椀挀攀 椀猀 渀漀琀 一漀渀攀ഀ
਍        瀀爀椀渀琀⠀∀   Ԁ‧匀攀爀瘀椀挀攀 椀渀椀琀椀愀氀椀稀攀搀 猀甀挀挀攀猀猀昀甀氀氀礀∀⤀ഀ
਍        ഀ
਍        ⌀ 吀攀猀琀 ㈀㨀 倀爀攀瘀椀攀眀 昀甀渀挀琀椀漀渀愀氀椀琀礀ഀ
਍        瀀爀椀渀琀⠀∀㈀⸀ 吀攀猀琀椀渀最 挀氀攀愀渀甀瀀 瀀爀攀瘀椀攀眀⸀⸀⸀∀⤀ഀ
਍        瀀爀攀瘀椀攀眀 㴀 愀眀愀椀琀 猀攀爀瘀椀挀攀⸀最攀琀开挀氀攀愀渀甀瀀开瀀爀攀瘀椀攀眀⠀⤀ഀ
਍        愀猀猀攀爀琀 椀猀椀渀猀琀愀渀挀攀⠀瀀爀攀瘀椀攀眀Ⰰ 搀椀挀琀⤀ഀ
਍        愀猀猀攀爀琀 ∀琀漀琀愀氀开爀攀挀漀爀搀猀∀ 椀渀 瀀爀攀瘀椀攀眀ഀ
਍        瀀爀椀渀琀⠀昀∀   Ԁ‧倀爀攀瘀椀攀眀 最攀渀攀爀愀琀攀搀㨀 笀瀀爀攀瘀椀攀眀嬀✀琀漀琀愀氀开爀攀挀漀爀搀猀✀崀紀 爀攀挀漀爀搀猀 昀漀甀渀搀∀⤀ഀ
਍        ഀ
਍        ⌀ 吀攀猀琀 ㌀㨀 䐀爀礀 爀甀渀 挀氀攀愀渀甀瀀ഀ
਍        瀀爀椀渀琀⠀∀㌀⸀ 吀攀猀琀椀渀最 搀爀礀 爀甀渀 挀氀攀愀渀甀瀀⸀⸀⸀∀⤀ഀ
਍        爀攀瀀漀爀琀 㴀 愀眀愀椀琀 猀攀爀瘀椀挀攀⸀搀攀氀攀琀攀开漀氀搀开搀愀琀愀⠀搀愀礀猀㴀㄀Ⰰ 搀爀礀开爀甀渀㴀吀爀甀攀⤀ഀ
਍        愀猀猀攀爀琀 椀猀椀渀猀琀愀渀挀攀⠀爀攀瀀漀爀琀Ⰰ 䌀氀攀愀渀甀瀀刀攀瀀漀爀琀⤀ഀ
਍        愀猀猀攀爀琀 爀攀瀀漀爀琀⸀猀琀愀琀甀猀 椀渀 嬀∀挀漀洀瀀氀攀琀攀搀∀Ⰰ ∀昀愀椀氀攀搀∀崀ഀ
਍        瀀爀椀渀琀⠀昀∀   Ԁ‧䐀爀礀 爀甀渀 挀漀洀瀀氀攀琀攀搀㨀 笀爀攀瀀漀爀琀⸀琀漀琀愀氀开爀攀挀漀爀搀猀开猀挀愀渀渀攀搀紀 爀攀挀漀爀搀猀 猀挀愀渀渀攀搀∀⤀ഀ
਍        ഀ
਍        ⌀ 吀攀猀琀 㐀㨀 䐀愀琀愀戀愀猀攀 猀椀稀攀 挀栀攀挀欀ഀ
਍        瀀爀椀渀琀⠀∀㐀⸀ 吀攀猀琀椀渀最 搀愀琀愀戀愀猀攀 猀椀稀攀 挀栀攀挀欀⸀⸀⸀∀⤀ഀ
਍        猀椀稀攀开椀渀昀漀 㴀 愀眀愀椀琀 最攀琀开搀愀琀愀戀愀猀攀开猀椀稀攀开椀渀昀漀⠀⤀ഀ
਍        愀猀猀攀爀琀 椀猀椀渀猀琀愀渀挀攀⠀猀椀稀攀开椀渀昀漀Ⰰ 搀椀挀琀⤀ഀ
਍        瀀爀椀渀琀⠀昀∀   Ԁ‧匀椀稀攀 挀栀攀挀欀 挀漀洀瀀氀攀琀攀搀㨀 笀猀椀稀攀开椀渀昀漀⸀最攀琀⠀✀琀漀琀愀氀开猀椀稀攀开洀戀✀Ⰰ 　⤀紀 䴀䈀∀⤀ഀ
਍        ഀ
਍        ⌀ 吀攀猀琀 㔀㨀 倀漀氀椀挀礀 挀爀攀愀琀椀漀渀ഀ
਍        瀀爀椀渀琀⠀∀㔀⸀ 吀攀猀琀椀渀最 挀甀猀琀漀洀 瀀漀氀椀挀礀 挀爀攀愀琀椀漀渀⸀⸀⸀∀⤀ഀ
਍        挀甀猀琀漀洀开瀀漀氀椀挀礀 㴀 挀爀攀愀琀攀开挀甀猀琀漀洀开瀀漀氀椀挀礀⠀ഀ
਍            挀漀渀瘀攀爀猀愀琀椀漀渀猀开爀攀琀攀渀琀椀漀渀开搀愀礀猀㴀㄀㔀Ⰰഀ
਍            攀洀漀琀椀漀渀愀氀开猀琀愀琀攀猀开爀攀琀攀渀琀椀漀渀开搀愀礀猀㴀㐀㔀ഀ
਍        ⤀ഀ
਍        愀猀猀攀爀琀 挀甀猀琀漀洀开瀀漀氀椀挀礀⸀挀漀渀瘀攀爀猀愀琀椀漀渀猀开爀攀琀攀渀琀椀漀渀开搀愀礀猀 㴀㴀 ㄀㔀ഀ
਍        愀猀猀攀爀琀 挀甀猀琀漀洀开瀀漀氀椀挀礀⸀攀洀漀琀椀漀渀愀氀开猀琀愀琀攀猀开爀攀琀攀渀琀椀漀渀开搀愀礀猀 㴀㴀 㐀㔀ഀ
਍        瀀爀椀渀琀⠀∀   Ԁ‧䌀甀猀琀漀洀 瀀漀氀椀挀礀 挀爀攀愀琀攀搀 猀甀挀挀攀猀猀昀甀氀氀礀∀⤀ഀ
਍        ഀ
਍        瀀爀椀渀琀⠀∀尀渀㰀飃观鿃 All tests passed!")਍ഀ
        return True਍ഀ
    ਍ഀ
    except Exception as e:਍ഀ
        print(f"\n❌ Test failed: {e}")਍ഀ
        import traceback਍ഀ
        traceback.print_exc()਍ഀ
        return False਍ഀ
਍ഀ
਍ഀ
if __name__ == "__main__":਍ഀ
    # Check if running as test਍ഀ
    if len(sys.argv) > 1 and sys.argv[1] == "test":਍ഀ
        asyncio.run(test_cleanup_service())਍ഀ
    else:਍ഀ
        asyncio.run(main())਍ഀ
