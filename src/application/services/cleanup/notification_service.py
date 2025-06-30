#!/usr/bin/env python3
"""
Notification Service for Cleanup Operations
Handles parent notifications and cleanup reports
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

from ....domain.cleanup.models.cleanup_target import CleanupTarget
from ....domain.cleanup.models.cleanup_report import CleanupReport


class NotificationService:
    """خدمة إشعارات الوالدين وتقارير التنظيف"""
    
    def __init__(self, log_directory: str = "cleanup_logs"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def notify_parents_before_cleanup(
        self, 
        targets: List[CleanupTarget], 
        report: CleanupReport
    ):
        """إشعار الوالدين قبل الحذف"""
        
        try:
            # Group targets by child
            children_data = self._group_targets_by_child(targets)
            
            # Send notifications
            for child_id, data in children_data.items():
                notification_sent = await self._send_parent_cleanup_notification(
                    child_id, data, report.policy.notification_days_before
                )
                
                if notification_sent:
                    report.parents_notified.add(child_id)
            
            self.logger.info(f"Sent cleanup notifications to {len(report.parents_notified)} parents")
        
        except Exception as e:
            report.add_error(f"Error sending parent notifications: {str(e)}")
            self.logger.error(f"Error sending notifications: {e}")
    
    def _group_targets_by_child(self, targets: List[CleanupTarget]) -> Dict[str, Dict[str, Any]]:
        """تجميع الأهداف حسب الطفل"""
        
        children_data = {}
        
        for target in targets:
            if target.child_id:
                if target.child_id not in children_data:
                    children_data[target.child_id] = {
                        'conversations': 0,
                        'messages': 0,
                        'emotions': 0,
                        'files': 0,
                        'total_size': 0
                    }
                
                if target.data_type == "conversation":
                    children_data[target.child_id]['conversations'] += 1
                elif target.data_type == "message":
                    children_data[target.child_id]['messages'] += 1
                elif target.data_type == "emotional_state":
                    children_data[target.child_id]['emotions'] += 1
                elif "file" in target.data_type:
                    children_data[target.child_id]['files'] += 1
                
                children_data[target.child_id]['total_size'] += target.size_bytes
        
        return children_data
    
    async def _send_parent_cleanup_notification(
        self, 
        child_id: str, 
        data: Dict[str, Any], 
        days_before: int
    ) -> bool:
        """إرسال إشعار واحد للوالدين"""
        
        try:
            # Create notification content
            notification = {
                "type": "data_cleanup_notice",
                "child_id": child_id,
                "scheduled_date": (datetime.utcnow() + timedelta(days=days_before)).isoformat(),
                "data_summary": {
                    "conversations": data['conversations'],
                    "messages": data['messages'],
                    "emotions": data['emotions'],
                    "files": data['files'],
                    "total_size_mb": round(data['total_size'] / 1024 / 1024, 2)
                },
                "message": f"Data cleanup scheduled for {child_id} in {days_before} days. "
                          f"This includes {data['conversations']} conversations, "
                          f"{data['messages']} messages, and {data['emotions']} emotion records.",
                "action_required": "None - automatic process. Contact support to modify retention policy.",
                "generated_at": datetime.utcnow().isoformat()
            }
            
            # Save notification (implement your notification service here)
            notification_file = self.log_directory / f"parent_notification_{child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(notification_file, 'w', encoding='utf-8') as f:
                json.dump(notification, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Created parent notification for child {child_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error creating parent notification for {child_id}: {e}")
            return False
    
    async def generate_parent_cleanup_reports(self, report: CleanupReport):
        """إنتاج تقارير للوالدين بعد التنظيف"""
        
        try:
            # Generate summary for each affected child
            for child_id in report.children_affected:
                cleanup_summary = {
                    "child_id": child_id,
                    "cleanup_date": report.completed_at.isoformat() if report.completed_at else datetime.utcnow().isoformat(),
                    "policy_used": report.policy.to_dict(),
                    "data_removed": {
                        "conversations": report.conversations_deleted,
                        "messages": report.messages_deleted,
                        "emotions": report.emotional_states_deleted,
                        "files": report.audio_files_deleted
                    },
                    "retention_info": {
                        "conversations_kept_days": report.policy.conversations_retention_days,
                        "emotions_kept_days": report.policy.emotional_states_retention_days,
                        "next_cleanup": (datetime.utcnow() + timedelta(days=30)).isoformat()
                    },
                    "privacy_compliance": {
                        "gdpr_compliant": report.policy.gdpr_compliant,
                        "backup_created": report.policy.backup_before_delete,
                        "parent_notified": child_id in report.parents_notified
                    },
                    "performance": report.get_performance_summary()
                }
                
                # Save individual child report
                child_report_file = self.log_directory / f"cleanup_report_{child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                with open(child_report_file, 'w', encoding='utf-8') as f:
                    json.dump(cleanup_summary, f, indent=2, ensure_ascii=False)
                
                self.logger.info(f"Generated cleanup report for child {child_id}")
        
        except Exception as e:
            report.add_error(f"Error generating parent reports: {str(e)}")
            self.logger.error(f"Error generating parent reports: {e}")
    
    async def save_cleanup_report(self, report: CleanupReport):
        """حفظ تقرير التنظيف الرئيسي"""
        
        try:
            report_file = self.log_directory / f"cleanup_report_{report.cleanup_id}.json"
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report.to_dict(), f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Saved cleanup report: {report_file}")
        
        except Exception as e:
            self.logger.error(f"Error saving cleanup report: {e}")
    
    async def get_cleanup_preview(
        self, 
        targets: List[CleanupTarget], 
        policy
    ) -> Dict[str, Any]:
        """إنشاء معاينة لعملية التنظيف"""
        
        try:
            # Summarize by type
            summary = {
                "total_records": len(targets),
                "by_type": {},
                "by_child": {},
                "total_size_mb": 0,
                "children_affected": set(),
                "policy": policy.to_dict()
            }
            
            for target in targets:
                # By type
                if target.data_type not in summary["by_type"]:
                    summary["by_type"][target.data_type] = {
                        "count": 0,
                        "size_bytes": 0
                    }
                summary["by_type"][target.data_type]["count"] += 1
                summary["by_type"][target.data_type]["size_bytes"] += target.size_bytes
                
                # By child
                if target.child_id:
                    summary["children_affected"].add(target.child_id)
                    if target.child_id not in summary["by_child"]:
                        summary["by_child"][target.child_id] = {
                            "count": 0,
                            "size_bytes": 0
                        }
                    summary["by_child"][target.child_id]["count"] += 1
                    summary["by_child"][target.child_id]["size_bytes"] += target.size_bytes
                
                summary["total_size_mb"] += target.size_bytes
            
            summary["total_size_mb"] = round(summary["total_size_mb"] / 1024 / 1024, 2)
            summary["children_affected"] = list(summary["children_affected"])
            
            return summary
        
        except Exception as e:
            self.logger.error(f"Error generating cleanup preview: {e}")
            return {
                "error": str(e),
                "total_records": 0,
                "policy": policy.to_dict()
            } 