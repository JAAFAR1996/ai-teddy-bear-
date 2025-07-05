#!/usr/bin/env python3
"""
Cleanup Execution Service
Handles the actual deletion of data and files
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from sqlalchemy import text

from ....domain.cleanup.models.cleanup_report import CleanupReport
from ....domain.cleanup.models.cleanup_target import CleanupTarget


class CleanupExecutionService:
    """خدمة تنفيذ عملية الحذف الفعلية"""

    def __init__(self, emotion_db_service=None):
        self.emotion_db_service = emotion_db_service
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute_cleanup(
            self,
            targets: List[CleanupTarget],
            report: CleanupReport,
            session_manager):
        """تنفيذ عملية الحذف الفعلية"""

        try:
            # Group by table for efficient deletion
            targets_by_table = self._group_targets_by_table(targets)

            # Delete in proper order (respecting foreign keys)
            deletion_order = [
                "emotional_states",
                "messages",
                "conversations",
                "files"]

            for table_name in deletion_order:
                if table_name in targets_by_table:
                    deleted_count = await self._delete_table_records(
                        table_name,
                        targets_by_table[table_name],
                        report,
                        session_manager,
                    )

                    # Update report counts
                    self._update_report_counts(
                        table_name, deleted_count, report)
                    report.total_records_deleted += deleted_count

            # Clean up orphaned files
            await self._cleanup_orphaned_files(report)

            self.logger.info(
                f"Cleanup completed: {report.total_records_deleted} records deleted"
            )

        except Exception as e:
            report.add_error(f"Error executing cleanup: {str(e)}")
            self.logger.error(f"Error executing cleanup: {e}")

    def _group_targets_by_table(
        self, targets: List[CleanupTarget]
    ) -> Dict[str, List[CleanupTarget]]:
        """تجميع الأهداف حسب الجدول"""
        targets_by_table = {}
        for target in targets:
            if target.table_name not in targets_by_table:
                targets_by_table[target.table_name] = []
            targets_by_table[target.table_name].append(target)
        return targets_by_table

    async def _delete_table_records(
        self,
        table_name: str,
        targets: List[CleanupTarget],
        report: CleanupReport,
        session_manager,
    ) -> int:
        """حذف سجلات من جدول محدد"""

        deleted_count = 0

        try:
            if table_name == "files":
                return await self._delete_files(targets, report)

            if not self.emotion_db_service:
                return 0

            async with session_manager() as session:
                record_ids = [target.record_id for target in targets]

                if not record_ids:
                    return 0

                # Delete records based on table
                query = self._get_deletion_query(table_name)
                if query:
                    result = session.execute(
                        query, {"record_ids": tuple(record_ids)})
                    deleted_count = result.rowcount
                    report.database_operations_count += 1

                    # Calculate freed space
                    for target in targets:
                        report.total_size_freed_bytes += target.size_bytes

                    self.logger.info(
                        f"Deleted {deleted_count} records from {table_name}"
                    )

        except Exception as e:
            report.add_error(f"Error deleting from {table_name}: {str(e)}")
            self.logger.error(f"Error deleting from {table_name}: {e}")

        return deleted_count

    def _get_deletion_query(self, table_name: str):
        """الحصول على query الحذف حسب نوع الجدول"""

        if table_name == "conversations":
            return text("DELETE FROM conversations WHERE id IN :record_ids")
        elif table_name == "messages":
            return text("DELETE FROM messages WHERE id IN :record_ids")
        elif table_name == "emotional_states":
            return text("DELETE FROM emotional_states WHERE id IN :record_ids")
        else:
            self.logger.warning(f"Unknown table for deletion: {table_name}")
            return None

    async def _delete_files(
        self, file_targets: List[CleanupTarget], report: CleanupReport
    ) -> int:
        """حذف الملفات"""

        deleted_count = 0

        for target in file_targets:
            try:
                file_path = Path(target.record_id)
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    file_path.unlink()

                    deleted_count += 1
                    report.total_size_freed_bytes += file_size
                    report.file_operations_count += 1

                    self.logger.debug(f"Deleted file: {file_path}")

            except Exception as e:
                report.add_error(
                    f"Error deleting file {target.record_id}: {str(e)}")
                self.logger.error(f"Error deleting file: {e}")

        return deleted_count

    async def _cleanup_orphaned_files(self, report: CleanupReport):
        """تنظيف الملفات المهجورة"""

        try:
            # Clean up orphaned files
            orphaned_files = []

            # Check cache directories
            cache_dirs = [Path("cache"), Path("temp"), Path("uploads")]

            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    for file_path in cache_dir.rglob("*"):
                        if file_path.is_file():
                            # Check if file is older than 24 hours and small
                            # (likely temp)
                            file_age = datetime.now() - datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            )
                            file_size = file_path.stat().st_size

                            if (
                                file_age.total_seconds() > 86400
                                and file_size < 1024 * 1024
                            ):  # 1MB
                                orphaned_files.append(file_path)

            # Delete orphaned files
            for file_path in orphaned_files:
                try:
                    file_path.unlink()
                    report.file_operations_count += 1
                    self.logger.debug(f"Cleaned up orphaned file: {file_path}")
                except Exception as e:
                    self.logger.warning(
                        f"Could not delete orphaned file {file_path}: {e}"
                    )

            if orphaned_files:
                self.logger.info(
                    f"Cleaned up {len(orphaned_files)} orphaned files")

        except Exception as e:
            report.add_error(f"Error cleaning up related files: {str(e)}")
            self.logger.error(f"Error cleaning up related files: {e}")

    def _update_report_counts(
        self, table_name: str, deleted_count: int, report: CleanupReport
    ):
        """تحديث عدادات التقرير"""

        if table_name == "conversations":
            report.conversations_deleted = deleted_count
        elif table_name == "messages":
            report.messages_deleted = deleted_count
        elif table_name == "emotional_states":
            report.emotional_states_deleted = deleted_count
        elif table_name == "files":
            report.audio_files_deleted = deleted_count
