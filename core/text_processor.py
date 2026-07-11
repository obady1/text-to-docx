"""معالجة وتنظيف النصوص قبل إضافتها إلى المستند."""

import re
from typing import Optional

from core.models import Lesson
from utils.logger import get_logger

logger = get_logger(__name__)


class TextProcessor:
    """مسؤول عن تنظيف النصوص وتقسيمها إلى فقرات."""

    # نمط الأسطر الفارغة المتكررة (ثلاثة أسطر فارغة أو أكثر → سطران فارغان)
    MULTIPLE_BLANK_LINES = re.compile(r"\n{3,}")

    def __init__(self, first_line_indent_cm: float = 0.0) -> None:
        self._first_line_indent_cm = first_line_indent_cm

    # ──────────────────────────────────────────────
    # التنظيف الأساسي
    # ──────────────────────────────────────────────

    def clean_text(self, text: str) -> str:
        """تنظيف النص من المشاكل الشائعة.

        - إزالة الأسطر الفارغة المتكررة
        - إزالة المسافات الزائدة في بداية ونهاية كل سطر
        - توحيد فواصل الأسطر

        Args:
            text: النص الخام.

        Returns:
            النص المنظف.
        """
        if not text:
            return ""

        # إزالة BOM إذا وُجد
        if text.startswith("\ufeff"):
            text = text[1:]

        # تقسيم إلى أسطر وتنظيف كل سطر
        lines = text.split("\n")
        cleaned_lines = [line.strip() for line in lines]

        # إعادة التجميع
        text = "\n".join(cleaned_lines)

        # إزالة الأسطر الفارغة المتكررة (تبقى أسطر فارغة واحدة كحد أقصى بين الفقرات)
        text = self.MULTIPLE_BLANK_LINES.sub("\n\n", text)

        # إزالة الأسطر الفارغة في البداية والنهاية
        text = text.strip()

        return text

    # ──────────────────────────────────────────────
    # تقسيم الفقرات
    # ──────────────────────────────────────────────

    def split_into_paragraphs(self, text: str) -> list[str]:
        """تقسيم النص إلى فقرات منفصلة.

        فقرة = سطر أو أكثر من النص المتصل، مفصولة عن غيرها
        بسطر فارغ واحد على الأقل.

        Args:
            text: النص المنظف.

        Returns:
            قائمة الفقرات (كل عنصر فقرة كاملة).
        """
        if not text:
            return []

        # تقسيم على سطر فارغ واحد أو أكثر
        raw_paragraphs = re.split(r"\n\s*\n", text)

        # توحيد أسطر الفقرة الواحدة وتنظيفها
        paragraphs = []
        for para in raw_paragraphs:
            # توحيد أسطر الفقرة بمسافة واحدة
            unified = " ".join(para.split())
            if unified.strip():
                paragraphs.append(unified.strip())

        return paragraphs

    # ──────────────────────────────────────────────
    # معالجة الدرس الكامل
    # ──────────────────────────────────────────────

    def process_lesson(self, lesson: Lesson) -> Lesson:
        """معالجة درس كامل: تنظيف النص وتقسيمه إلى فقرات.

        Args:
            lesson: كائن الدرس الخام.

        Returns:
            كائن الدرس بعد المعالجة (نفس الكائن مُعدَّل).
        """
        try:
            with open(lesson.file_path, "r", encoding="utf-8", errors="replace") as f:
                raw_text = f.read()
        except OSError:
            raw_text = ""

        cleaned = self.clean_text(raw_text)
        lesson.paragraphs = self.split_into_paragraphs(cleaned)

        logger.debug(
            "درس '%s': %d فقرة",
            lesson.title,
            len(lesson.paragraphs),
        )
        return lesson

    def process_lessons(self, lessons: list[Lesson]) -> list[Lesson]:
        """معالجة مجموعة من الدروس.

        Args:
            lessons: قائمة الدروس الخام.

        Returns:
            قائمة الدروس بعد المعالجة.
        """
        processed = []
        for lesson in lessons:
            processed.append(self.process_lesson(lesson))
        return processed