from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
from datetime import datetime, timedelta
import random
import json
import asyncio
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

class GameCategory(Enum):
    """فئات الألعاب حسب نوع الموهبة"""
    LANGUAGE = "لغوية"           # تطوير اللغة والمفردات
    MATHEMATICAL = "رياضية"      # الرياضيات والمنطق
    CREATIVE = "إبداعية"        # الإبداع والخيال
    SOCIAL = "اجتماعية"         # المهارات الاجتماعية
    PHYSICAL = "حركية"          # التناسق الحركي
    MUSICAL = "موسيقية"         # المواهب الموسيقية
    SCIENTIFIC = "علمية"        # الاستكشاف العلمي
    EMOTIONAL = "عاطفية"        # الذكاء العاطفي
    MEMORY = "ذاكرة"           # تقوية الذاكرة
    PROBLEM_SOLVING = "حل_مشاكل" # حل المشاكل

class SkillLevel(Enum):
    """مستويات المهارة"""
    BEGINNER = "مبتدئ"
    INTERMEDIATE = "متوسط"
    ADVANCED = "متقدم"
    EXPERT = "خبير"

class DifficultyLevel(Enum):
    """مستويات الصعوبة"""
    VERY_EASY = "سهل_جداً"
    EASY = "سهل"
    MEDIUM = "متوسط"
    HARD = "صعب"
    VERY_HARD = "صعب_جداً"

@dataclass
class GameStats:
    """إحصائيات اللعبة"""
    games_played: int = 0
    total_score: int = 0
    best_score: int = 0
    avg_score: float = 0.0
    completion_rate: float = 0.0
    skill_improvements: Dict[str, int] = None
    
    def __post_init__(self):
        if self.skill_improvements is None:
            self.skill_improvements = {}

@dataclass
class PlayerProgress:
    """تقدم اللاعب"""
    child_name: str
    age: int
    friends: List[str] = None
    current_level: SkillLevel = SkillLevel.BEGINNER
    total_points: int = 0
    streak_days: int = 0
    badges_earned: List[str] = None
    game_stats: Dict[str, GameStats] = None
    favorite_games: List[str] = None
    last_played: Optional[datetime] = None
    
    def __post_init__(self):
        if self.friends is None:
            self.friends = []
        if self.badges_earned is None:
            self.badges_earned = []
        if self.game_stats is None:
            self.game_stats = {}
        if self.favorite_games is None:
            self.favorite_games = []

class BaseGame(ABC):
    """الفئة الأساسية للألعاب"""
    
    def __init__(self, name: str, category: GameCategory, min_age: int, max_age: int):
        self.name = name
        self.category = category
        self.min_age = min_age
        self.max_age = max_age
        self.difficulty_levels = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]
        
    @abstractmethod
    async def start_game(self, player: PlayerProgress) -> Dict[str, Any]:
        """بدء اللعبة"""
        pass
        
    @abstractmethod
    async def process_answer(self, answer: str, game_state: Dict) -> Dict[str, Any]:
        """معالجة إجابة اللاعب"""
        pass
        
    def is_age_appropriate(self, age: int) -> bool:
        """فحص مناسبة اللعبة للعمر"""
        return self.min_age <= age <= self.max_age
        
    def calculate_points(self, correct: bool, difficulty: DifficultyLevel, time_taken: float) -> int:
        """حساب النقاط"""
        base_points = {
            DifficultyLevel.VERY_EASY: 5,
            DifficultyLevel.EASY: 10,
            DifficultyLevel.MEDIUM: 20,
            DifficultyLevel.HARD: 35,
            DifficultyLevel.VERY_HARD: 50
        }
        
        if not correct:
            return 0
            
        points = base_points[difficulty]
        
        # مكافأة السرعة
        if time_taken < 10:
            points += 5
        elif time_taken < 20:
            points += 2
            
        return points

# ============ ألعاب اللغة ============

class WordBuilderGame(BaseGame):
    """لعبة بناء الكلمات - تطوير المفردات"""
    
    def __init__(self):
        super().__init__("بناء_الكلمات", GameCategory.LANGUAGE, 4, 12)
        self.word_lists = {
            DifficultyLevel.EASY: ["قط", "كلب", "بيت", "شمس", "قمر"],
            DifficultyLevel.MEDIUM: ["مدرسة", "حديقة", "طائرة", "كتاب", "صديق"],
            DifficultyLevel.HARD: ["مغامرة", "اكتشاف", "إبداع", "تحدي", "استكشاف"]
        }
    
    async def start_game(self, player: PlayerProgress) -> Dict[str, Any]:
        difficulty = self._select_difficulty(player.age)
        words = self.word_lists[difficulty]
        target_word = random.choice(words)
        scrambled = self._scramble_word(target_word)
        
        friends_mention = ""
        if player.friends:
            friend = random.choice(player.friends)
            friends_mention = f"مثل صديقك {friend}"
            
        return {
            "message": f"مرحباً {player.child_name}! رتب هذه الحروف لتكوين كلمة صحيحة {friends_mention}: {scrambled}",
            "scrambled_word": scrambled,
            "target_word": target_word,
            "difficulty": difficulty.value,
            "points_possible": self.calculate_points(True, difficulty, 15)
        }
    
    async def process_answer(self, answer: str, game_state: Dict) -> Dict[str, Any]:
        correct = answer.strip().lower() == game_state["target_word"].lower()
        points = self.calculate_points(correct, DifficultyLevel(game_state["difficulty"]), 15)
        
        if correct:
            encouragement = random.choice([
                "رائع! أحسنت!", "ممتاز جداً!", "أنت ذكي!", "واو! هذا صحيح!"
            ])
        else:
            encouragement = f"محاولة جيدة! الكلمة الصحيحة هي: {game_state['target_word']}"
            
        return {
            "correct": correct,
            "points_earned": points,
            "message": encouragement,
            "skill_improved": "المفردات" if correct else None
        }
    
    def _select_difficulty(self, age: int) -> DifficultyLevel:
        if age <= 6:
            return DifficultyLevel.EASY
        elif age <= 9:
            return DifficultyLevel.MEDIUM
        else:
            return DifficultyLevel.HARD
    
    def _scramble_word(self, word: str) -> str:
        letters = list(word)
        random.shuffle(letters)
        return " - ".join(letters)

class StorytellingGame(BaseGame):
    """لعبة الحكايات - تطوير الخيال والسرد"""
    
    def __init__(self):
        super().__init__("الحكايات", GameCategory.CREATIVE, 5, 14)
        self.story_prompts = [
            "حيوان صغير يريد أن يطير",
            "طفل يكتشف كنزاً مخفياً",
            "نجمة تهبط من السماء",
            "شجرة سحرية تتكلم",
            "طائر يساعد الأطفال"
        ]
    
    async def start_game(self, player: PlayerProgress) -> Dict[str, Any]:
        prompt = random.choice(self.story_prompts)
        friends_mention = ""
        if player.friends:
            friends_mention = f" يمكنك إضافة أصدقائك {', '.join(player.friends[:2])} في القصة"
            
        return {
            "message": f"يا {player.child_name}، احك لي قصة عن: {prompt}{friends_mention}",
            "story_prompt": prompt,
            "difficulty": DifficultyLevel.MEDIUM.value
        }
    
    async def process_answer(self, answer: str, game_state: Dict) -> Dict[str, Any]:
        # تقييم القصة بناءً على الطول والإبداع
        story_length = len(answer.split())
        creativity_score = self._evaluate_creativity(answer)
        
        if story_length > 20 and creativity_score > 0.5:
            points = 25
            message = "قصة رائعة جداً! أنت موهوب في الحكايات!"
        elif story_length > 10:
            points = 15
            message = "قصة جميلة! حاول إضافة المزيد من التفاصيل المرة القادمة"
        else:
            points = 5
            message = "بداية جيدة! حاول أن تجعل قصتك أطول وأكثر تفصيلاً"
            
        return {
            "correct": True,
            "points_earned": points,
            "message": message,
            "skill_improved": "الإبداع والخيال"
        }
    
    def _evaluate_creativity(self, story: str) -> float:
        creative_words = ["سحري", "مغامرة", "عجيب", "رائع", "مدهش", "جميل"]
        word_count = len(story.split())
        creative_count = sum(1 for word in creative_words if word in story)
        return creative_count / max(word_count / 10, 1)

# ============ ألعاب الرياضيات ============

class MathChallengeGame(BaseGame):
    """تحدي الرياضيات - تطوير المهارات الحسابية"""
    
    def __init__(self):
        super().__init__("تحدي_الرياضيات", GameCategory.MATHEMATICAL, 5, 15)
    
    async def start_game(self, player: PlayerProgress) -> Dict[str, Any]:
        difficulty = self._select_difficulty(player.age)
        problem = self._generate_problem(difficulty, player.age)
        
        return {
            "message": f"يا {player.child_name}، احسب هذه المسألة: {problem['question']}",
            "problem": problem,
            "difficulty": difficulty.value
        }
    
    def _generate_problem(self, difficulty: DifficultyLevel, age: int) -> Dict:
        if age <= 7:
            # عمليات جمع وطرح بسيطة
            a, b = random.randint(1, 10), random.randint(1, 10)
            if random.choice([True, False]):
                return {"question": f"{a} + {b}", "answer": a + b}
            else:
                a, b = max(a, b), min(a, b)  # تأكد من أن النتيجة موجبة
                return {"question": f"{a} - {b}", "answer": a - b}
        elif age <= 10:
            # ضرب وقسمة بسيطة
            if difficulty == DifficultyLevel.EASY:
                a, b = random.randint(1, 12), random.randint(1, 12)
                return {"question": f"{a} × {b}", "answer": a * b}
            else:
                a = random.randint(2, 10)
                b = random.randint(2, 10)
                result = a * b
                return {"question": f"{result} ÷ {a}", "answer": b}
        else:
            # مسائل أكثر تعقيداً
            a, b, c = random.randint(10, 50), random.randint(5, 25), random.randint(2, 10)
            return {"question": f"({a} + {b}) × {c}", "answer": (a + b) * c}
    
    async def process_answer(self, answer: str, game_state: Dict) -> Dict[str, Any]:
        try:
            user_answer = float(answer.strip())
            correct_answer = game_state["problem"]["answer"]
            correct = abs(user_answer - correct_answer) < 0.01
            
            difficulty = DifficultyLevel(game_state["difficulty"])
            points = self.calculate_points(correct, difficulty, 20)
            
            if correct:
                message = random.choice([
                    "ممتاز! إجابة صحيحة!", "أحسنت! أنت بارع في الرياضيات!",
                    "رائع جداً! استمر هكذا!"
                ])
            else:
                message = f"قريب! الإجابة الصحيحة هي {correct_answer}"
                
            return {
                "correct": correct,
                "points_earned": points,
                "message": message,
                "skill_improved": "الرياضيات" if correct else None
            }
        except ValueError:
            return {
                "correct": False,
                "points_earned": 0,
                "message": "من فضلك أدخل رقماً صحيحاً",
                "skill_improved": None
            }

# ============ ألعاب الموسيقى ============

class RhythmGame(BaseGame):
    """لعبة الإيقاع - تطوير الحس الموسيقي"""
    
    def __init__(self):
        super().__init__("الإيقاع", GameCategory.MUSICAL, 4, 12)
        self.rhythm_patterns = {
            DifficultyLevel.EASY: ["تا تا تا", "تا تي تا"],
            DifficultyLevel.MEDIUM: ["تا تي تي تا", "تي تا تي تا"],
            DifficultyLevel.HARD: ["تا تي تا تي تي", "تي تي تا تا تي"]
        }
    
    async def start_game(self, player: PlayerProgress) -> Dict[str, Any]:
        difficulty = self._select_difficulty(player.age)
        pattern = random.choice(self.rhythm_patterns[difficulty])
        
        return {
            "message": f"يا {player.child_name}، اسمع هذا الإيقاع وكرره: {pattern}",
            "rhythm_pattern": pattern,
            "difficulty": difficulty.value
        }
    
    async def process_answer(self, answer: str, game_state: Dict) -> Dict[str, Any]:
        pattern = game_state["rhythm_pattern"]
        correct = self._compare_rhythm(answer, pattern)
        
        difficulty = DifficultyLevel(game_state["difficulty"])
        points = self.calculate_points(correct, difficulty, 15)
        
        if correct:
            message = "إيقاع رائع! لديك حس موسيقي ممتاز!"
        else:
            message = f"حاول مرة أخرى! الإيقاع الصحيح هو: {pattern}"
            
        return {
            "correct": correct,
            "points_earned": points,
            "message": message,
            "skill_improved": "الموسيقى" if correct else None
        }
    
    def _compare_rhythm(self, user_input: str, target: str) -> bool:
        # مقارنة بسيطة للإيقاع
        return user_input.strip().lower() == target.lower()

# ============ ألعاب العلوم ============

class ScienceExplorerGame(BaseGame):
    """مستكشف العلوم - تطوير الفضول العلمي"""
    
    def __init__(self):
        super().__init__("مستكشف_العلوم", GameCategory.SCIENTIFIC, 6, 14)
        self.science_questions = {
            DifficultyLevel.EASY: [
                {"q": "كم عدد أرجل العنكبوت؟", "a": "8"},
                {"q": "ما لون الشمس؟", "a": "أصفر"},
                {"q": "كم عدد ألوان قوس قزح؟", "a": "7"}
            ],
            DifficultyLevel.MEDIUM: [
                {"q": "ما أكبر كوكب في النظام الشمسي؟", "a": "المشتري"},
                {"q": "ما الغاز الذي نتنفسه؟", "a": "الأكسجين"},
                {"q": "كم عدد عظام جسم الإنسان؟", "a": "206"}
            ],
            DifficultyLevel.HARD: [
                {"q": "ما سرعة الضوء؟", "a": "300000 كيلومتر في الثانية"},
                {"q": "ما أصغر وحدة في المادة؟", "a": "الذرة"},
                {"q": "كم عدد قلوب الأخطبوط؟", "a": "3"}
            ]
        }
    
    async def start_game(self, player: PlayerProgress) -> Dict[str, Any]:
        difficulty = self._select_difficulty(player.age)
        question_data = random.choice(self.science_questions[difficulty])
        
        return {
            "message": f"سؤال علمي لك يا {player.child_name}: {question_data['q']}",
            "question": question_data["q"],
            "answer": question_data["a"],
            "difficulty": difficulty.value
        }
    
    async def process_answer(self, answer: str, game_state: Dict) -> Dict[str, Any]:
        correct_answer = game_state["answer"].lower()
        user_answer = answer.strip().lower()
        
        # فحص مرن للإجابة
        correct = (user_answer == correct_answer or 
                  user_answer in correct_answer or 
                  correct_answer in user_answer)
        
        difficulty = DifficultyLevel(game_state["difficulty"])
        points = self.calculate_points(correct, difficulty, 25)
        
        if correct:
            message = "ممتاز! إجابة علمية صحيحة! أنت عالم صغير!"
        else:
            message = f"تعلمنا شيئاً جديداً! الإجابة هي: {game_state['answer']}"
            
        return {
            "correct": correct,
            "points_earned": points,
            "message": message,
            "skill_improved": "العلوم" if correct else None
        }

# ============ ألعاب الذاكرة ============

class MemoryChampionGame(BaseGame):
    """بطل الذاكرة - تقوية الذاكرة"""
    
    def __init__(self):
        super().__init__("بطل_الذاكرة", GameCategory.MEMORY, 4, 14)
        self.memory_sequences = {
            DifficultyLevel.EASY: 3,    # 3 عناصر
            DifficultyLevel.MEDIUM: 5,  # 5 عناصر
            DifficultyLevel.HARD: 7     # 7 عناصر
        }
    
    async def start_game(self, player: PlayerProgress) -> Dict[str, Any]:
        difficulty = self._select_difficulty(player.age)
        sequence_length = self.memory_sequences[difficulty]
        
        # إنشاء تسلسل من الألوان أو الأرقام
        if player.age <= 7:
            items = ["أحمر", "أزرق", "أخضر", "أصفر", "بنفسجي"]
        else:
            items = list(range(1, 10))
            
        sequence = random.sample(items, sequence_length)
        
        return {
            "message": f"يا {player.child_name}، احفظ هذا التسلسل: {' - '.join(map(str, sequence))}",
            "sequence": sequence,
            "difficulty": difficulty.value,
            "instruction": "الآن أعد التسلسل بنفس الترتيب"
        }
    
    async def process_answer(self, answer: str, game_state: Dict) -> Dict[str, Any]:
        original_sequence = game_state["sequence"]
        user_sequence = answer.strip().split()
        
        # تنظيف الإجابة
        user_sequence = [item.strip() for item in user_sequence if item.strip()]
        
        correct = user_sequence == [str(item) for item in original_sequence]
        
        difficulty = DifficultyLevel(game_state["difficulty"])
        points = self.calculate_points(correct, difficulty, 30)
        
        if correct:
            message = "ذاكرة خارقة! أحسنت يا بطل!"
        else:
            message = f"حاول مرة أخرى! التسلسل الصحيح: {' - '.join(map(str, original_sequence))}"
            
        return {
            "correct": correct,
            "points_earned": points,
            "message": message,
            "skill_improved": "الذاكرة" if correct else None
        }

# ============ نظام إدارة الألعاب المتقدم ============

class EnhancedGameSystem:
    """نظام الألعاب المتقدم والشامل"""
    
    def __init__(self):
        self.games: List[BaseGame] = [
            WordBuilderGame(),
            StorytellingGame(),
            MathChallengeGame(),
            RhythmGame(),
            ScienceExplorerGame(),
            MemoryChampionGame()
        ]
        
        self.badges = {
            "عبقري_الكلمات": {"category": GameCategory.LANGUAGE, "threshold": 100},
            "عالم_الرياضيات": {"category": GameCategory.MATHEMATICAL, "threshold": 150},
            "الفنان_الصغير": {"category": GameCategory.CREATIVE, "threshold": 80},
            "الموسيقار": {"category": GameCategory.MUSICAL, "threshold": 60},
            "المكتشف": {"category": GameCategory.SCIENTIFIC, "threshold": 120},
            "بطل_الذاكرة": {"category": GameCategory.MEMORY, "threshold": 90},
            "الملتزم": {"threshold": 7, "type": "streak"},  # 7 أيام متتالية
            "النجم_الصاعد": {"threshold": 500, "type": "total_points"}
        }
        
        self.daily_challenges = self._generate_daily_challenges()
    
    def get_age_appropriate_games(self, age: int) -> List[BaseGame]:
        """الحصول على الألعاب المناسبة للعمر"""
        return [game for game in self.games if game.is_age_appropriate(age)]
    
    def recommend_game(self, player: PlayerProgress) -> Optional[BaseGame]:
        """اقتراح لعبة مناسبة للاعب"""
        appropriate_games = self.get_age_appropriate_games(player.age)
        
        if not appropriate_games:
            return None
            
        # اقتراح لعبة جديدة أو لعبة لم يلعبها لفترة
        unplayed_games = [g for g in appropriate_games if g.name not in player.game_stats]
        
        if unplayed_games:
            return random.choice(unplayed_games)
        
        # اقتراح لعبة بناءً على الأداء الضعيف لتحسينه
        weak_categories = self._identify_weak_categories(player)
        if weak_categories:
            category_games = [g for g in appropriate_games if g.category in weak_categories]
            if category_games:
                return random.choice(category_games)
        
        # اقتراح عشوائي
        return random.choice(appropriate_games)
    
    def _identify_weak_categories(self, player: PlayerProgress) -> List[GameCategory]:
        """تحديد الفئات التي يحتاج الطفل لتحسينها"""
        weak_categories = []
        
        for game_name, stats in player.game_stats.items():
            if stats.avg_score < 15:  # نقاط منخفضة
                game = next((g for g in self.games if g.name == game_name), None)
                if game and game.category not in weak_categories:
                    weak_categories.append(game.category)
        
        return weak_categories
    
    async def play_game(self, game_name: str, player: PlayerProgress) -> Dict[str, Any]:
        """لعب لعبة محددة"""
        game = next((g for g in self.games if g.name == game_name), None)
        
        if not game:
            return {"error": "اللعبة غير موجودة"}
        
        if not game.is_age_appropriate(player.age):
            return {"error": "هذه اللعبة غير مناسبة لعمرك"}
        
        # تحديث آخر لعب
        player.last_played = datetime.now()
        
        # بدء اللعبة
        game_state = await game.start_game(player)
        game_state["game_name"] = game_name
        game_state["start_time"] = datetime.now().isoformat()
        
        return game_state
    
    async def process_game_answer(self, answer: str, game_state: Dict, player: PlayerProgress) -> Dict[str, Any]:
        """معالجة إجابة اللاعب"""
        game_name = game_state.get("game_name")
        game = next((g for g in self.games if g.name == game_name), None)
        
        if not game:
            return {"error": "اللعبة غير موجودة"}
        
        # معالجة الإجابة
        result = await game.process_answer(answer, game_state)
        
        # تحديث إحصائيات اللاعب
        self._update_player_stats(player, game_name, result)
        
        # فحص الشارات الجديدة
        new_badges = self._check_new_badges(player)
        if new_badges:
            result["new_badges"] = new_badges
        
        return result
    
    def _update_player_stats(self, player: PlayerProgress, game_name: str, result: Dict):
        """تحديث إحصائيات اللاعب"""
        # إضافة النقاط
        points = result.get("points_earned", 0)
        player.total_points += points
        
        # تحديث إحصائيات اللعبة
        if game_name not in player.game_stats:
            player.game_stats[game_name] = GameStats()
        
        stats = player.game_stats[game_name]
        stats.games_played += 1
        stats.total_score += points
        
        if points > stats.best_score:
            stats.best_score = points
        
        stats.avg_score = stats.total_score / stats.games_played
        
        # تحديث تحسن المهارات
        skill_improved = result.get("skill_improved")
        if skill_improved:
            if skill_improved not in stats.skill_improvements:
                stats.skill_improvements[skill_improved] = 0
            stats.skill_improvements[skill_improved] += 1
        
        # تحديث الألعاب المفضلة
        if points > 15 and game_name not in player.favorite_games:
            player.favorite_games.append(game_name)
        
        # تحديث تتابع الأيام
        today = datetime.now().date()
        if player.last_played and player.last_played.date() == today - timedelta(days=1):
            player.streak_days += 1
        elif not player.last_played or player.last_played.date() != today:
            player.streak_days = 1
    
    def _check_new_badges(self, player: PlayerProgress) -> List[str]:
        """فحص الشارات الجديدة"""
        new_badges = []
        
        for badge_name, criteria in self.badges.items():
            if badge_name in player.badges_earned:
                continue
            
            if criteria.get("type") == "streak":
                if player.streak_days >= criteria["threshold"]:
                    new_badges.append(badge_name)
                    player.badges_earned.append(badge_name)
            elif criteria.get("type") == "total_points":
                if player.total_points >= criteria["threshold"]:
                    new_badges.append(badge_name)
                    player.badges_earned.append(badge_name)
            else:
                # شارات الفئات
                category = criteria["category"]
                category_points = sum(
                    stats.total_score for game_name, stats in player.game_stats.items()
                    if any(g.category == category and g.name == game_name for g in self.games)
                )
                if category_points >= criteria["threshold"]:
                    new_badges.append(badge_name)
                    player.badges_earned.append(badge_name)
        
        return new_badges
    
    def _generate_daily_challenges(self) -> Dict[str, Any]:
        """توليد تحديات يومية"""
        return {
            "word_master": "اكتشف 5 كلمات جديدة اليوم",
            "math_wizard": "احل 3 مسائل رياضية صعبة",
            "story_teller": "احك قصة مدتها دقيقتان",
            "memory_hero": "احفظ تسلسل من 6 عناصر",
            "science_explorer": "تعلم حقيقة علمية جديدة"
        }
    
    def get_progress_report(self, player: PlayerProgress) -> Dict[str, Any]:
        """تقرير شامل عن تقدم اللاعب"""
        total_games = sum(stats.games_played for stats in player.game_stats.values())
        
        # تحليل نقاط القوة والضعف
        strengths = []
        weaknesses = []
        
        for game_name, stats in player.game_stats.items():
            game = next((g for g in self.games if g.name == game_name), None)
            if game:
                if stats.avg_score > 20:
                    strengths.append(game.category.value)
                elif stats.avg_score < 10:
                    weaknesses.append(game.category.value)
        
        return {
            "player_name": player.child_name,
            "age": player.age,
            "total_points": player.total_points,
            "total_games_played": total_games,
            "streak_days": player.streak_days,
            "badges_count": len(player.badges_earned),
            "badges": player.badges_earned,
            "strengths": list(set(strengths)),
            "areas_for_improvement": list(set(weaknesses)),
            "favorite_games": player.favorite_games,
            "skill_improvements": self._aggregate_skill_improvements(player),
            "recommendations": self._get_recommendations(player)
        }
    
    def _aggregate_skill_improvements(self, player: PlayerProgress) -> Dict[str, int]:
        """تجميع تحسينات المهارات"""
        aggregated = {}
        for stats in player.game_stats.values():
            for skill, count in stats.skill_improvements.items():
                if skill not in aggregated:
                    aggregated[skill] = 0
                aggregated[skill] += count
        return aggregated
    
    def _get_recommendations(self, player: PlayerProgress) -> List[str]:
        """الحصول على توصيات للاعب"""
        recommendations = []
        
        # توصيات بناءً على العمر
        if player.age >= 8 and "تحدي_الرياضيات" not in player.favorite_games:
            recommendations.append("جرب تحدي الرياضيات لتقوية مهاراتك الحسابية")
        
        if player.age >= 6 and "مستكشف_العلوم" not in player.favorite_games:
            recommendations.append("استكشف عالم العلوم مع لعبة المكتشف")
        
        # توصيات بناءً على الأداء
        if player.streak_days < 3:
            recommendations.append("حاول اللعب يومياً لتحسين مهاراتك")
        
        if player.total_points < 100:
            recommendations.append("العب ألعاب أسهل لبناء ثقتك بنفسك")
        
        return recommendations