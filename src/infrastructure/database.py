#!/usr/bin/env python3
"""
🗄️ Database Module for HUME AI Emotion Analysis
قاعدة البيانات لحفظ وإدارة نتائج تحليل المشاعر
"""
import structlog
logger = structlog.get_logger(__name__)


from sqlalchemy import create_engine, Column, String, DateTime, Float, Integer, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import os

# إعداد قاعدة البيانات
Base = declarative_base()

# إنشاء مجلد البيانات إذا لم يكن موجوداً
os.makedirs("data", exist_ok=True)

# الاتصال بقاعدة البيانات
DATABASE_URL = "sqlite:///data/emotion.db"
engine = create_engine(DATABASE_URL, echo=False)  # echo=True للتصحيح
Session = sessionmaker(bind=engine)

class SessionRecord(Base):
    """
    📊 جدول جلسات التحليل
    يحفظ معلومات كل جلسة تحليل مشاعر
    """
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    udid = Column(String(100), nullable=False, index=True)  # معرف الجهاز
    child_name = Column(String(100))  # اسم الطفل
    child_age = Column(Integer)  # عمر الطفل
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    mode = Column(String(20))  # "batch" أو "stream"
    audio_file = Column(String(255))  # مسار الملف الصوتي
    job_id = Column(String(100))  # معرف المهمة في HUME
    status = Column(String(20), default="pending")  # "success", "error", "pending"
    error_message = Column(Text)  # رسالة الخطأ إن وجدت
    
    # العلاقات
    emotions = relationship("Emotion", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SessionRecord(id={self.id}, udid='{self.udid}', mode='{self.mode}', status='{self.status}')>"

class Emotion(Base):
    """
    🎭 جدول المشاعر المكتشفة
    يحفظ تفاصيل كل مشاعر مكتشفة في الجلسة
    """
    __tablename__ = "emotions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False, index=True)
    name = Column(String(50), nullable=False)  # اسم المشاعر (Joy, Sadness, etc.)
    score = Column(Float, nullable=False)  # درجة المشاعر (0.0 - 1.0)
    confidence = Column(Float)  # مستوى الثقة
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # العلاقات
    session = relationship("SessionRecord", back_populates="emotions")
    
    def __repr__(self):
        return f"<Emotion(name='{self.name}', score={self.score}, session_id={self.session_id})>"

class ChildProfile(Base):
    """
    👶 جدول ملفات الأطفال
    يحفظ معلومات الأطفال ومعرفاتهم
    """
    __tablename__ = "child_profiles"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    udid = Column(String(100), unique=True, nullable=False, index=True)
    child_name = Column(String(100), nullable=False)
    child_age = Column(Integer)
    parent_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # معلومات إضافية
    preferences = Column(JSON)  # تفضيلات الطفل
    notes = Column(Text)  # ملاحظات الوالدين
    
    def __repr__(self):
        return f"<ChildProfile(udid='{self.udid}', name='{self.child_name}', age={self.child_age})>"

class EmotionSummary(Base):
    """
    📈 جدول ملخص المشاعر اليومي
    لتحسين الأداء والتقارير السريعة
    """
    __tablename__ = "emotion_summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    udid = Column(String(100), nullable=False, index=True)
    date = Column(DateTime, nullable=False, index=True)  # تاريخ اليوم
    
    # إحصائيات المشاعر
    total_sessions = Column(Integer, default=0)
    dominant_emotion = Column(String(50))  # المشاعر الأكثر شيوعاً
    avg_joy = Column(Float, default=0.0)
    avg_sadness = Column(Float, default=0.0)
    avg_anger = Column(Float, default=0.0)
    avg_fear = Column(Float, default=0.0)
    avg_excitement = Column(Float, default=0.0)
    avg_calmness = Column(Float, default=0.0)
    
    # معلومات إضافية
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<EmotionSummary(udid='{self.udid}', date='{self.date.date()}', dominant='{self.dominant_emotion}')>"


class DatabaseManager:
    """
    🗄️ مدير قاعدة البيانات
    يوفر واجهات سهلة للتعامل مع قاعدة البيانات
    """
    
    def __init__(self):
        self.engine = engine
        self.Session = Session
        print("🗄️ Database Manager initialized")
    
    def create_tables(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            Base.metadata.create_all(self.engine)
            print("✅ Database tables created successfully")
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error creating database tables: {e}")
    
    def save_session(
        self, 
        udid: str, 
        child_name: str = None, 
        child_age: int = None,
        mode: str = "stream", 
        audio_file: str = None,
        job_id: str = None
    ) -> SessionRecord:
        """
        💾 حفظ جلسة تحليل جديدة
        
        Returns:
            SessionRecord: سجل الجلسة المحفوظ
        """
        session = self.Session()
        try:
            # إنشاء سجل جلسة جديد
            session_record = SessionRecord(
                udid=udid,
                child_name=child_name,
                child_age=child_age,
                mode=mode,
                audio_file=audio_file,
                job_id=job_id,
                status="pending"
            )
            
            session.add(session_record)
            session.commit()
            
            print(f"✅ Session saved: ID={session_record.id}, UDID={udid}")
            return session_record
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving session: {e}")
            raise
        finally:
            session.close()
    
    def save_emotions(self, session_id: int, emotions_data: List[Dict[str, Any]]):
        """
        🎭 حفظ المشاعر المكتشفة
        
        Args:
            session_id: معرف الجلسة
            emotions_data: قائمة المشاعر [{"name": "Joy", "score": 0.85}, ...]
        """
        session = self.Session()
        try:
            for emotion_data in emotions_data:
                emotion = Emotion(
                    session_id=session_id,
                    name=emotion_data.get("name"),
                    score=emotion_data.get("score", 0.0),
                    confidence=emotion_data.get("confidence")
                )
                session.add(emotion)
            
            session.commit()
            print(f"✅ Saved {len(emotions_data)} emotions for session {session_id}")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving emotions: {e}")
            raise
        finally:
            session.close()
    
    def update_session_status(self, session_id: int, status: str, error_message: str = None):
        """
        📝 تحديث حالة الجلسة
        """
        session = self.Session()
        try:
            session_record = session.query(SessionRecord).filter_by(id=session_id).first()
            if session_record:
                session_record.status = status
                if error_message:
                    session_record.error_message = error_message
                session.commit()
                print(f"✅ Session {session_id} status updated to: {status}")
            else:
                print(f"⚠️ Session {session_id} not found")
                
        except Exception as e:
            session.rollback()
            print(f"❌ Error updating session status: {e}")
        finally:
            session.close()
    
    def get_child_sessions(self, udid: str, days: int = 7) -> List[SessionRecord]:
        """
        📊 استرجاع جلسات الطفل خلال فترة معينة
        """
        session = self.Session()
        try:
            from datetime import timedelta
            since_date = datetime.utcnow() - timedelta(days=days)
            
            sessions = session.query(SessionRecord).filter(
                SessionRecord.udid == udid,
                SessionRecord.timestamp >= since_date
            ).order_by(SessionRecord.timestamp.desc()).all()
            
            print(f"📊 Found {len(sessions)} sessions for UDID {udid} in last {days} days")
            return sessions
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error getting child sessions: {e}")
            return []
        finally:
            session.close()
    
    def get_session_emotions(self, session_id: int) -> List[Emotion]:
        """
        🎭 استرجاع مشاعر جلسة معينة
        """
        session = self.Session()
        try:
            emotions = session.query(Emotion).filter_by(session_id=session_id).all()
            return emotions
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error getting session emotions: {e}")
            return []
        finally:
            session.close()
    
    def get_emotion_statistics(self, udid: str, days: int = 7) -> Dict[str, Any]:
        """
        📈 إحصائيات المشاعر للطفل
        """
        session = self.Session()
        try:
            from datetime import timedelta
            since_date = datetime.utcnow() - timedelta(days=days)
            
            # استعلام معقد للحصول على إحصائيات المشاعر
            stats = session.query(
                Emotion.name,
                func.avg(Emotion.score).label('avg_score'),
                func.count(Emotion.id).label('count')
            ).join(SessionRecord).filter(
                SessionRecord.udid == udid,
                SessionRecord.timestamp >= since_date,
                SessionRecord.status == 'success'
            ).group_by(Emotion.name).all()
            
            # تحويل النتائج إلى dictionary
            emotion_stats = {}
            for stat in stats:
                emotion_stats[stat.name] = {
                    'average_score': round(stat.avg_score, 3),
                    'frequency': stat.count
                }
            
            return {
                'period_days': days,
                'emotions': emotion_stats,
                'total_sessions': len(self.get_child_sessions(udid, days))
            }
            
        except Exception as e:
    logger.error(f"Error: {e}")f"❌ Error getting emotion statistics: {e}")
            return {}
        finally:
            session.close()
    
    def save_child_profile(self, udid: str, child_name: str, child_age: int = None, parent_name: str = None):
        """
        👶 حفظ أو تحديث ملف الطفل
        """
        session = self.Session()
        try:
            # البحث عن الملف الموجود
            profile = session.query(ChildProfile).filter_by(udid=udid).first()
            
            if profile:
                # تحديث الملف الموجود
                profile.child_name = child_name
                if child_age:
                    profile.child_age = child_age
                if parent_name:
                    profile.parent_name = parent_name
                profile.updated_at = datetime.utcnow()
                print(f"✅ Child profile updated: {child_name} (UDID: {udid})")
            else:
                # إنشاء ملف جديد
                profile = ChildProfile(
                    udid=udid,
                    child_name=child_name,
                    child_age=child_age,
                    parent_name=parent_name
                )
                session.add(profile)
                print(f"✅ New child profile created: {child_name} (UDID: {udid})")
            
            session.commit()
            return profile
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving child profile: {e}")
            raise
        finally:
            session.close()


# إنشاء مثيل مدير قاعدة البيانات
db_manager = DatabaseManager()

# إنشاء الجداول عند استيراد الوحدة
db_manager.create_tables()

if __name__ == "__main__":
    print("🗄️ Database module loaded successfully")
    print(f"📁 Database location: {DATABASE_URL}")
    
    # اختبار بسيط
    try:
        # إنشاء ملف طفل تجريبي
        profile = db_manager.save_child_profile(
            udid="TEST_ESP32_001",
            child_name="أحمد الاختبار",
            child_age=6,
            parent_name="والد الاختبار"
        )
        
        # إنشاء جلسة تجريبية
        session_record = db_manager.save_session(
            udid="TEST_ESP32_001",
            child_name="أحمد الاختبار",
            child_age=6,
            mode="stream",
            audio_file="test.wav"
        )
        
        # حفظ مشاعر تجريبية
        test_emotions = [
            {"name": "Joy", "score": 0.85, "confidence": 0.92},
            {"name": "Excitement", "score": 0.72, "confidence": 0.88},
            {"name": "Curiosity", "score": 0.65, "confidence": 0.75}
        ]
        
        db_manager.save_emotions(session_record.id, test_emotions)
        db_manager.update_session_status(session_record.id, "success")
        
        # استرجاع الإحصائيات
        stats = db_manager.get_emotion_statistics("TEST_ESP32_001", 7)
        print(f"📊 Test statistics: {stats}")
        
        print("✅ Database test completed successfully!")
        
    except Exception as e:
    logger.error(f"Error: {e}")f"❌ Database test failed: {e}") 