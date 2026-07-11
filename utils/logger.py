"""نظام السجلات الموحد للمشروع."""

import logging
import sys
from pathlib import Path
from typing import Optional


# مستوى السجل الافتراضي
DEFAULT_LEVEL = logging.DEBUG


def setup_logger(
    name: str = "txt_to_docx",
    level: int = DEFAULT_LEVEL,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """إعداد وإنشاء مسجل جديد مع معالجات ملائمة.

    Args:
        name: اسم المسجل.
        level: مستوى السجل (logging.DEBUG, logging.INFO, ...).
        log_file: مسار ملف السجل الاختياري.

    Returns:
        كائن المسجل المُعد.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # تجنب تكرار المعالجات
    if logger.handlers:
        return logger

    # تنسيق الرسائل
    formatter = logging.Formatter(
        fmt="%(asctime)s │ %(levelname)-8s │ %(name)-25s │ %(message)s",
        datefmt="%H:%M:%S",
    )

    # معالج الكونسول
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # معالج الملف (اختياري)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """الحصول على مسجل بوحدة معينة.

        name: اسم الوحدة (يُستخدم كاسم المسجل الفرعي).

    Returns:
        كائن المسجل.
    """
    # التأكد من أن المسجل الرئيسي مُعد
    root_logger = logging.getLogger("txt_to_docx")
    if not root_logger.handlers:
        setup_logger()

    child_name = f"txt_to_docx.{name}" if not name.startswith("txt_to_docx.") else name
    return logging.getLogger(child_name)