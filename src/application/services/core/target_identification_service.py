#!/usr/bin/env python3
"""
Target Identification Service
Identifies data targets for cleanup based on retention policies
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List
from sqlalchemy import text

from ....domain.cleanup.models.cleanup_target import CleanupTarget
from ....domain.cleanup.models.cleanup_report import CleanupReport
from ....domain.cleanup.models.retention_policy import DataRetentionPolicy


class TargetIdentificationService:
    """خدمة تحديد البيانات المرشحة للحذف"""
    
    def __init__(self, emotion_db_service=None):
        self.emotion_db_service = emotion_db_service
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def identify_cleanup_targets(
        self, 
        policy: DataRetentionPolicy, 
        report: CleanupReport,
        session_manager
    ) -> List[CleanupTarget]:
        """تحديد البيانات المرشحة للحذف"""
        
        targets = []
        
        try:
            # Use emotion database service if available
            if self.emotion_db_service:
                targets.extend(await self._identify_emotion_targets(policy, report, session_manager))
            
            # Identify file targets
            targets.extend(await self._identify_file_targets(policy, report))
            
            report.total_records_scanned = len(targets)
            self.logger.info(f"Identified {len(targets)} records for cleanup")
            
        except Exception as e:
            report.add_error(f"Error identifying cleanup targets: {str(e)}")
            self.logger.error(f"Error identifying cleanup targets: {e}", exc_info=True)
        
        return targets
    
    async def _identify_emotion_targets(
        self, 
        policy: DataRetentionPolicy, 
        report: CleanupReport,
        session_manager
    ) -> List[CleanupTarget]:
        """تحديد البيانات من قاعدة بيانات المشاعر"""
        
        targets = []
        
        if not self.emotion_db_service:
            return targets
        
        try:
            async with session_manager() as session:
                # Calculate cutoff dates
                conversations_cutoff = datetime.utcnow() - timedelta(days=policy.conversations_retention_days)
                messages_cutoff = datetime.utcnow() - timedelta(days=policy.messages_retention_days)
                emotions_cutoff = datetime.utcnow() - timedelta(days=policy.emotional_states_retention_days)
                
                # Find old conversations
                targets.extend(await self._find_old_conversations(session, conversations_cutoff, report))
                
                # Find old messages
                targets.extend(await self._find_old_messages(session, messages_cutoff, report))
                
                # Find old emotional states
                targets.extend(await self._find_old_emotions(session, emotions_cutoff, report))
        
        except Exception as e:
            report.add_error(f"Error identifying emotion database targets: {str(e)}")
            self.logger.error(f"Error with emotion database: {e}")
        
        return targets
    
    async def _find_old_conversations(self, session, cutoff_date, report) -> List[CleanupTarget]:
        """البحث عن المحادثات القديمة"""
        targets = []
        
        old_conversations = session.execute(text("""
            SELECT id, child_id, created_at, session_id
            FROM conversations 
            WHERE created_at < :cutoff
        """), {"cutoff": cutoff_date}).fetchall()
        
        for conv in old_conversations:
            targets.append(CleanupTarget(
                table_name="conversations",
                record_id=conv[0],
                child_id=conv[1],
                created_at=conv[2] if isinstance(conv[2], datetime) else datetime.fromisoformat(conv[2]),
                data_type="conversation",
                foreign_key_refs=["messages", "emotional_states"]
            ))
            report.children_affected.add(conv[1])
        
        return targets
    
    async def _find_old_messages(self, session, cutoff_date, report) -> List[CleanupTarget]:
        """البحث عن الرسائل القديمة"""
        targets = []
        
        old_messages = session.execute(text("""
            SELECT id, conversation_id, created_at, content
            FROM messages 
            WHERE created_at < :cutoff
        """), {"cutoff": cutoff_date}).fetchall()
        
        for msg in old_messages:
            targets.append(CleanupTarget(
                table_name="messages",
                record_id=msg[0],
                created_at=msg[2] if isinstance(msg[2], datetime) else datetime.fromisoformat(msg[2]),
                data_type="message",
                size_bytes=len(msg[3].encode('utf-8')) if msg[3] else 0,
                foreign_key_refs=["emotional_states"]
            ))
        
        return targets
    
    async def _find_old_emotions(self, session, cutoff_date, report) -> List[CleanupTarget]:
        """البحث عن البيانات العاطفية القديمة"""
        targets = []
        
        old_emotions = session.execute(text("""
            SELECT id, child_id, analysis_timestamp, primary_emotion
            FROM emotional_states 
            WHERE analysis_timestamp < :cutoff
        """), {"cutoff": cutoff_date}).fetchall()
        
        for emotion in old_emotions:
            targets.append(CleanupTarget(
                table_name="emotional_states",
                record_id=emotion[0],
                child_id=emotion[1],
                created_at=emotion[2] if isinstance(emotion[2], datetime) else datetime.fromisoformat(emotion[2]),
                data_type="emotional_state"
            ))
            if emotion[1]:
                report.children_affected.add(emotion[1])
        
        return targets
    
    async def _identify_file_targets(
        self, 
        policy: DataRetentionPolicy, 
        report: CleanupReport
    ) -> List[CleanupTarget]:
        """تحديد الملفات المرشحة للحذف"""
        
        targets = []
        
        try:
            # Audio files
            targets.extend(await self._find_old_audio_files(policy))
            
            # Backup files
            targets.extend(await self._find_old_backup_files())
            
        except Exception as e:
            report.add_error(f"Error identifying file targets: {str(e)}")
            self.logger.error(f"Error identifying files: {e}")
        
        return targets
    
    async def _find_old_audio_files(self, policy: DataRetentionPolicy) -> List[CleanupTarget]:
        """البحث عن ملفات الصوت القديمة"""
        targets = []
        
        audio_directories = [
            Path("audio-files"),
            Path("uploads"),
            Path("cache/audio"),
            Path("data/audio")
        ]
        
        audio_cutoff = datetime.utcnow() - timedelta(days=policy.audio_files_retention_days)
        
        for audio_dir in audio_directories:
            if audio_dir.exists():
                for audio_file in audio_dir.rglob("*"):
                    if audio_file.is_file():
                        # Check file modification time
                        file_mtime = datetime.fromtimestamp(audio_file.stat().st_mtime)
                        if file_mtime < audio_cutoff:
                            targets.append(CleanupTarget(
                                table_name="files",
                                record_id=str(audio_file),
                                created_at=file_mtime,
                                data_type="audio_file",
                                size_bytes=audio_file.stat().st_size,
                                related_files=[str(audio_file)]
                            ))
        
        return targets
    
    async def _find_old_backup_files(self) -> List[CleanupTarget]:
        """البحث عن ملفات النسخ الاحتياطي القديمة"""
        targets = []
        
        backup_cutoff = datetime.utcnow() - timedelta(days=30)  # Keep backups for 30 days
        backup_directory = Path("data_backups")
        
        if backup_directory.exists():
            for backup_file in backup_directory.rglob("*"):
                if backup_file.is_file():
                    file_mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)
                    if file_mtime < backup_cutoff:
                        targets.append(CleanupTarget(
                            table_name="files",
                            record_id=str(backup_file),
                            created_at=file_mtime,
                            data_type="backup_file",
                            size_bytes=backup_file.stat().st_size,
                            related_files=[str(backup_file)]
                        ))
        
        return targets 