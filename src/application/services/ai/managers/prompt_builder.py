import logging
from typing import Any, Dict, Optional

from src.core.domain.entities.child import Child

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds prompts for the OpenAI API."""

    async def build_enhanced_system_prompt(
        self, child: Child, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build enhanced system prompt with context awareness"""
        base_prompt = f"""أنت دبدوب، دب محبوب وذكي يتحدث مع الأطفال باللغة العربية.

معلومات الطفل:
- الاسم: {child.name}
- العمر: {child.age} سنوات
- مستوى التعلم: {getattr(child, 'learning_level', 'متوسط')}
- الجهاز: {getattr(child, 'device_id', 'غير محدد')}

شخصيتك المحدثة 2025:
- محبوب وودود ومرح وذكي
- تتكيف مع مشاعر الطفل وحالته النفسية
- تستخدم تقنيات التعلم الحديثة والتفاعل الإيجابي
- تشجع الفضول والإبداع والتفكير النقدي
- تقدم محتوى تعليمي ممتع ومناسب للعمر

قواعد التفاعل المحدثة:
- اجعل الردود قصيرة ومفيدة (2-3 جمل كحد أقصى)
- استخدم اللغة العربية الفصحى المبسطة
- أضف لمسة من الدعابة والمرح المناسب
- شجع على التعلم والاستكشاف
- كن صبوراً ومتفهماً ومحباً"""

        # Add context-specific instructions
        if context:
            if context.get("time_of_day"):
                base_prompt += f"\n- وقت التفاعل: {context['time_of_day']}"
            if context.get("activity"):
                base_prompt += f"\n- النشاط الحالي: {context['activity']}"
            if context.get("mood"):
                base_prompt += f"\n- مزاج الطفل: {context['mood']}"

        return base_prompt
