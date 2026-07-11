"""النماذج والهياكل الأساسية المستخدمة في المشروع."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PageSize(str, Enum):
    """أحجام الورق المدعومة."""
    A4 = "A4"
    A5 = "A5"
    LETTER = "Letter"
    B5 = "B5"
    LEGAL = "Legal"


class TextDirection(str, Enum):
    """اتجاه النص."""
    RTL = "RTL"
    LTR = "LTR"


@dataclass
class BookSettings:
    """إعدادات الكتاب والمستند بالكامل.

    تحتوي جميع القيم القابلة للتعديل من قبل المستخدم
    مع قيم افتراضية مناسبة للكتب العربية.
    """
    # ── المعلومات الأساسية ──
    book_title: str = ""
    author_name: str = ""
    header_text: str = ""
    footer_text: str = ""

    # ── الخط ──
    font_name: str = "Simplified Arabic"
    font_size: int = 14
    heading_font_size: int = 26
    heading_font_name: str = "Simplified Arabic"

    # ── الصفحة ──
    page_size: str = "A4"
    margin_top_cm: float = 2.0
    margin_bottom_cm: float = 2.0
    margin_left_cm: float = 2.5
    margin_right_cm: float = 2.5
    text_direction: str = "RTL"

    # ── المسافات ──
    line_spacing: float = 1.5
    paragraph_spacing_after_cm: float = 0.3
    first_line_indent_cm: float = 0.0

    # ── المكونات الاختيارية ──
    add_cover: bool = True
    add_copyright: bool = True
    add_toc: bool = True
    add_page_numbers: bool = True
    add_header: bool = True
    add_footer: bool = True

    # ── النصوص الإضافية ──
    copyright_text: str = "جميع الحقوق محفوظة © {year} {author}"
    intro_text: str = ""
    conclusion_text: str = ""
    cover_image_path: str = ""

    # ── واجهة المستخدم ──
    language: str = "ar"
    theme: str = "dark"

    # ── المسارات الأخيرة ──
    last_input_folder: str = ""
    last_output_folder: str = ""


@dataclass
class Lesson:
    """يمثل درسًا واحدًا مستخلصًا من ملف TXT."""
    title: str
    paragraphs: list[str] = field(default_factory=list)
    file_path: str = ""
    file_index: int = 0


@dataclass
class ConversionStats:
    """إحصائيات عملية التحويل."""
    total_files: int = 0
    processed_files: int = 0
    failed_files: int = 0
    failed_filenames: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    output_path: str = ""
    cancelled: bool = False


# قواميس أحجام الورق بالسنتيمتر
PAGE_DIMENSIONS_CM: dict[str, tuple[float, float]] = {
    "A4": (21.0, 29.7),
    "A5": (14.8, 21.0),
    "Letter": (21.59, 27.94),
    "B5": (17.6, 25.0),
    "Legal": (21.59, 35.56),
}

# الخطوط العربية المقترحة
ARABIC_FONTS = [
    "Simplified Arabic",
    "Traditional Arabic",
    "Amiri",
    "Noto Naskh Arabic",
    "Scheherazade New",
    "Arial",
    "Times New Roman",
]

# الخطوط اللاتينية المقترحة
LATIN_FONTS = [
    "Times New Roman",
    "Garamond",
    "Calibri",
    "Arial",
    "Georgia",
    "Palatino",
]