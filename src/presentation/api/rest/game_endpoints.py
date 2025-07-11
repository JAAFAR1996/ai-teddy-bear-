# [AI-Generated by Amazon Q]: تم إضافة هذا الكود تلقائياً وفق دليل المشروع.
"""
API نقاط نهاية الألعاب - يوفر واجهات لبدء وإدارة وإنهاء الألعاب التفاعلية
يدير جلسات الألعاب ويحفظ الحالة مؤقتاً
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.domain.games.voice_games_engine import GameType, VoiceGameEngine

router = APIRouter(prefix="/games", tags=["games"])


class GameStartRequest(BaseModel):
    game_type: str
    child_name: str
    age: int
    topic: str = "عام"


class GameResponseRequest(BaseModel):
    response: str
    session_id: str


# تخزين جلسات الألعاب (يفضل استخدام Redis في الإنتاج)
game_sessions = {}


@router.post("/start")
async def start_game(request: GameStartRequest):
    """بدء لعبة جديدة"""
    try:
        # إنشاء محرك لعبة جديد
        engine = VoiceGameEngine(openai_key="YOUR_KEY")

        # تحويل نوع اللعبة
        game_type = GameType(request.game_type)

        # بدء اللعبة
        intro = engine.start_game(
            game_type=game_type,
            child_name=request.child_name,
            age=request.age,
            topic=request.topic,
        )

        # حفظ الجلسة
        session_id = f"game_{request.child_name}_{datetime.now().timestamp()}"
        game_sessions[session_id] = engine

        return {"session_id": session_id, "intro": intro, "status": "started"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/respond")
async def process_game_response(request: GameResponseRequest):
    """معالجة رد اللاعب"""
    engine = game_sessions.get(request.session_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Game session not found")

    result = engine.process_game_response(request.response)
    return result


@router.post("/end/{session_id}")
async def end_game(session_id: str):
    """إنهاء اللعبة"""
    engine = game_sessions.get(session_id)
    if not engine:
        raise HTTPException(status_code=404, detail="Game session not found")

    summary = engine.end_game()
    # حذف الجلسة
    del game_sessions[session_id]

    return {"summary": summary}
