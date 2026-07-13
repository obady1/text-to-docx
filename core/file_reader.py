"""قراءة ملفات TXT واكتشاف الترميز وترتيب الملفات."""

import os
import re
from pathlib import Path
from typing import Optional

import chardet

from core.model import Lesson
from utils.logger import get_logger

logger = get_logger(__name__)


class FileReader:
    """مسؤول عن قراءة ملفات النصوص واكتشاف ترميزها وترتيبها."""

    # الترميزات المراد تجربتها بالترتيب إذا فشل chardet
    FALLBACK_ENCODINGS = ["utf-8-sig", "utf-8", "windows-1256", "windows-1252", "iso-8859-6"]

    def __init__(self) -> None:
        self._detected_encodings: dict[str, str] = {}

    # ──────────────────────────────────────────────
    # اكتشاف الترميز
    # ──────────────────────────────────────────────

    def detect_encoding(self, file_path: str | Path) -> str:
        """اكتشاف ترميز الملف تلقائيًا باستخدام chardet.

        Args:
            file_path: مسار الملف.

        Returns:
            اسم الترميز كنص (مثال: 'utf-8').
        """
        file_path = Path(file_path)
        if file_path.name in self._detected_encodings:
            return self._detected_encodings[file_path.name]

        try:
            raw = file_path.read_bytes()
            # قراءة أول 64 كيلوبايت لتسريع الكشف
            sample = raw[:65536]
            if not sample.strip():
                self._detected_encodings[file_path.name] = "utf-8"
                return "utf-8"

            result = chardet.detect(sample)
            encoding = result.get("encoding", "utf-8") or "utf-8"
            confidence = result.get("confidence", 0.0)

            # إذا كانت الثقة منخفضة جدًا، نجرب الترميزات البديلة
            if confidence < 0.6:
                encoding = self._try_fallback_encodings(raw) or encoding

            # تطبيع اسم الترميز
            encoding = encoding.lower().replace("-", "")
            if encoding == "utf8sig":
                encoding = "utf-8-sig"
            elif encoding == "utf8":
                encoding = "utf-8"
            elif encoding == "ascii":
                encoding = "utf-8"

            self._detected_encodings[file_path.name] = encoding
            logger.debug("ترميز %s: %s (ثقة: %.1f%%)", file_path.name, encoding, confidence * 100)
            return encoding

        except OSError as e:
            logger.warning("فشل في قراءة %s للكشف عن الترميز: %s", file_path.name, e)
            return "utf-8"

    def _try_fallback_encodings(self, raw: bytes) -> Optional[str]:
        """تجربة الترميزات البديلة على البيانات الخام.

        Args:
            raw: البيانات الخام للملف.

        Returns:
            اسم الترميز الناجح أو None.
        """
        for enc in self.FALLBACK_ENCODINGS:
            try:
                raw.decode(enc)
                return enc
            except (UnicodeDecodeError, LookupError):
                continue
        return None

    # ──────────────────────────────────────────────
    # قراءة الملف
    # ──────────────────────────────────────────────

    def read_file(self, file_path: str | Path) -> str:
        """قراءة محتوى ملف نصي بالترميز الصحيح.

        Args:
            file_path: مسار الملف.

        Returns:
            المحتوى النصي للملف.

        Raises:
            FileNotFoundError: إذا لم يكن الملف موجودًا.
            OSError: إذا فشلت القراءة بجميع الترميزات.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"الملف غير موجود: {file_path}")

        encoding = self.detect_encoding(file_path)

        # محاولة القراءة بالترميز المكتشف
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            pass

        # محاولة القراءة بالترميزات البديلة
        raw = file_path.read_bytes()
        for enc in self.FALLBACK_ENCODINGS:
            try:
                return raw.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue

        # الحل الأخير: تجاهل الأخطاء
        logger.warning("تعذرت قراءة %s بأي ترميز، سيتم تجاهل الأحرف غير الصالحة", file_path.name)
        return raw.decode("utf-8", errors="replace")

    # ──────────────────────────────────────────────
    # استكشاف وترتيب الملفات
    # ──────────────────────────────────────────────

    def get_txt_files(self, folder_path: str | Path) -> list[Path]:
        """الحصول على جميع ملفات TXT في المجلد مرتبة ترتيبًا طبيعيًا.

        الترتيب الطبيعي يعني أن 001 يسبق 002 يسبق 010
        (وليس الترتيب الأبجدي الذي يجعل 010 قبل 002).

        Args:
            folder_path: مسار المجلد.

        Returns:
            قائمة بمسارات الملفات مرتبة.
        """
        folder_path = Path(folder_path)
        if not folder_path.is_dir():
            raise NotADirectoryError(f"المسار ليس مجلدًا: {folder_path}")

        txt_files = sorted(
            [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() == ".txt"],
            key=self._natural_sort_key,
        )
        logger.info("تم العثور على %d ملف TXT في %s", len(txt_files), folder_path.name)
        return txt_files

    @staticmethod
    def _natural_sort_key(path: Path) -> list:
        """مفتاح ترتيب طبيعي يتعامل مع الأرقام داخل أسماء الملفات.

        مثال: 'lesson_002.txt' < 'lesson_010.txt' < 'lesson_100.txt'

        Args:
            path: مسار الملف.

        Returns:
            قائمة تحتوي أجزاء النص والأرقام مفككة.
        """
        name = path.stem
        return [int(part) if part.isdigit() else part.lower()
                for part in re.split(r"(\d+)", name)]

    # ──────────────────────────────────────────────
    # قراءة الدروس
    # ──────────────────────────────────────────────

    def read_lessons(self, folder_path: str | Path) -> list[Lesson]:
        """قراءة جميع ملفات TXT وتحويلها إلى كائنات Lesson.

        Args:
            folder_path: مسار المجلد المحتوي على الملفات.

        Returns:
            قائمة مرتبة من كائنات Lesson.
        """
        files = self.get_txt_files(folder_path)
        lessons: list[Lesson] = []

        for index, file_path in enumerate(files):
            try:
                content = self.read_file(file_path)
                title = file_path.stem  # اسم الملف بدون الامتداد
                lessons.append(Lesson(
                    title=title,
                    paragraphs=[],  # سيتم ملؤها لاحقًا بواسطة TextProcessor
                    file_path=str(file_path),
                    file_index=index,
                ))
            except Exception as e:
                logger.error("فشل في قراءة %s: %s", file_path.name, e)

        return lessons