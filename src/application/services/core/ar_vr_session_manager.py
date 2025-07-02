#!/usr/bin/env python3
"""
⏱️ مدير جلسات AR/VR
مسؤول عن إدارة الجلسات فقط
"""

import logging
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


class ARVRSessionManager:
    """مدير الجلسات - مسؤولية واحدة فقط"""

    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.session_history: Dict[str, List[Dict]] = {}  # child_id -> sessions

    def create_ar_session(
        self, 
        child_id: str, 
        experience_id: str, 
        duration_minutes: int
    ) -> Dict:
        """إنشاء جلسة AR جديدة"""
        session_id = f"ar_{child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = {
            "session_id": session_id,
            "child_id": child_id,
            "experience_id": experience_id,
            "type": "ar",
            "start_time": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "status": "active",
            "interaction_log": [],
            "learning_progress": {},
            "safety_alerts": [],
        }

        self.active_sessions[session_id] = session
        self._add_to_history(child_id, session)
        
        return session

    def create_vr_session(
        self, 
        child_id: str, 
        environment_id: str, 
        max_duration: int,
        comfort_settings: Dict
    ) -> Dict:
        """إنشاء جلسة VR جديدة"""
        session_id = f"vr_{child_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = {
            "session_id": session_id,
            "child_id": child_id,
            "environment_id": environment_id,
            "type": "vr",
            "start_time": datetime.now().isoformat(),
            "max_duration": max_duration,
            "comfort_settings": comfort_settings,
            "status": "active",
            "interaction_log": [],
            "comfort_breaks": [],
            "learning_achievements": [],
        }

        self.active_sessions[session_id] = session
        self._add_to_history(child_id, session)
        
        return session

    def log_interaction(self, session_id: str, interaction_data: Dict) -> bool:
        """تسجيل تفاعل في الجلسة"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False

        interaction_data["timestamp"] = datetime.now().isoformat()
        session["interaction_log"].append(interaction_data)

        # تحديث التقدم التعليمي
        if interaction_data.get("learning_objective"):
            objective = interaction_data["learning_objective"]
            if objective not in session["learning_progress"]:
                session["learning_progress"][objective] = 0
            session["learning_progress"][objective] += 1

        return True

    def end_session(self, session_id: str) -> Dict:
        """إنهاء جلسة"""
        session = self.active_sessions.get(session_id)
        if not session or session["status"] != "active":
            return {"error": "الجلسة غير موجودة أو منتهية بالفعل"}

        session["status"] = "completed"
        session["end_time"] = datetime.now().isoformat()

        # حساب المدة الفعلية
        start_time = datetime.fromisoformat(session["start_time"])
        end_time = datetime.fromisoformat(session["end_time"])
        actual_duration = (end_time - start_time).total_seconds() / 60
        session["actual_duration_minutes"] = actual_duration

        # إزالة من الجلسات النشطة
        del self.active_sessions[session_id]

        return {
            "session_id": session_id,
            "total_interactions": len(session["interaction_log"]),
            "duration_minutes": actual_duration,
            "learning_progress": session.get("learning_progress", {}),
        }

    def get_active_sessions(self, child_id: str = None) -> List[Dict]:
        """الحصول على الجلسات النشطة"""
        sessions = list(self.active_sessions.values())
        
        if child_id:
            sessions = [s for s in sessions if s["child_id"] == child_id]
            
        return sessions

    def get_session_by_id(self, session_id: str) -> Dict:
        """الحصول على جلسة محددة"""
        # البحث في الجلسات النشطة أولاً
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # البحث في التاريخ
        for child_sessions in self.session_history.values():
            for session in child_sessions:
                if session["session_id"] == session_id:
                    return session
        
        return None

    def get_child_sessions(self, child_id: str) -> List[Dict]:
        """الحصول على جميع جلسات الطفل"""
        return self.session_history.get(child_id, [])

    def analyze_session_performance(self, session: Dict) -> Dict:
        """تحليل أداء الجلسة"""
        interactions = session["interaction_log"]

        performance = {
            "engagement_level": "medium",
            "learning_effectiveness": "good",
            "comfort_level": "high",
            "technical_issues": 0,
        }

        if interactions:
            # تحليل مستوى التفاعل
            interaction_rate = len(interactions) / max(
                session.get("actual_duration_minutes", 1), 1
            )
            if interaction_rate > 3:
                performance["engagement_level"] = "high"
            elif interaction_rate < 1:
                performance["engagement_level"] = "low"

            # تحليل المشاكل التقنية
            technical_issues = sum(
                1 for interaction in interactions 
                if interaction.get("type") == "error"
            )
            performance["technical_issues"] = technical_issues

            # تحليل مؤشرات عدم الراحة
            comfort_issues = sum(
                1 for interaction in interactions
                if interaction.get("comfort_issue", False)
            )
            if comfort_issues > 0:
                performance["comfort_level"] = "medium" if comfort_issues < 3 else "low"

        return performance

    def _add_to_history(self, child_id: str, session: Dict) -> None:
        """إضافة جلسة للتاريخ"""
        if child_id not in self.session_history:
            self.session_history[child_id] = []
        
        # إضافة نسخة من الجلسة (تجنب التعديل المباشر)
        self.session_history[child_id].append(session.copy())

    def get_session_statistics(self, child_id: str) -> Dict:
        """إحصائيات الجلسات للطفل"""
        sessions = self.get_child_sessions(child_id)
        
        if not sessions:
            return {"message": "لا توجد جلسات"}

        ar_sessions = [s for s in sessions if s["type"] == "ar"]
        vr_sessions = [s for s in sessions if s["type"] == "vr"]

        total_time_ar = sum(s.get("actual_duration_minutes", 0) for s in ar_sessions)
        total_time_vr = sum(s.get("actual_duration_minutes", 0) for s in vr_sessions)

        return {
            "total_ar_sessions": len(ar_sessions),
            "total_vr_sessions": len(vr_sessions),
            "total_time_ar_minutes": total_time_ar,
            "total_time_vr_minutes": total_time_vr,
            "average_session_duration": (
                (total_time_ar + total_time_vr) / len(sessions) if sessions else 0
            ),
            "total_interactions": sum(
                len(s.get("interaction_log", [])) for s in sessions
            ),
        } 