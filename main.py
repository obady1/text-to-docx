"""نقطة الدخول الرئيسية لتطبيق محوّل النصوص إلى Word.

يقوم بتهيئة جميع المكونات وبدء التطبيق:
1. إنشاء مجلد الإعدادات
2. توليد أيقونة التطبيق
3. إعداد نظام السجلات
4. تحميل إعدادات المستخدم
5. بدء واجهة المستخدم
"""

import sys
from pathlib import Path

# التأكد من أن مجلد المشروع في مسار البحث
PROJECT_ROOT = Path(__file__).parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def generate_icon(config_dir: Path) -> None:
    """توليد أيقونة بسيطة للتطبيق إذا لم تكن موجودة.

    Args:
        config_dir: مجلد الإعدادات لحفظ الأيقونة فيه.
    """
    icon_path = config_dir / "icon.ico"
    if icon_path.exists():
        return

    try:
        from PIL import Image, ImageDraw, ImageFont

        # إنشاء صورة 64x64
        size = 64
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # خلفية مستديرة
        draw.rounded_rectangle(
            [(2, 2), (size - 2, size - 2)],
            radius=12,
            fill=(26, 35, 126, 255),  # أزرق داكن
        )

        # حرف "W" أبيض (لـ Word)
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except (OSError, IOError):
            font = ImageFont.load_default()

        text = "W"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        x = (size - text_w) // 2
        y = (size - text_h) // 2 - 2
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

        # حفظ كـ ICO
        img.save(str(icon_path), format="ICO", sizes=[(32, 32), (64, 64)])
        print(f"تم إنشاء أيقونة التطبيق: {icon_path}")

    except ImportError:
        print("مكتبة Pillow غير متاحة، سيتم تخطي إنشاء الأيقونة.")
    except Exception as e:
        print(f"تعذّر إنشاء الأيقونة: {e}")


def main() -> None:
    """الدالة الرئيسية: تهيئة وتشغيل التطبيق."""
    # ── 1. إنشاء مجلد الإعدادات ──
    config_dir = Path.home() / ".txt_to_docx"
    config_dir.mkdir(parents=True, exist_ok=True)

    # ── 2. توليد الأيقونة ──
    generate_icon(config_dir)

    # ── 3. إعداد السجلات ──
    log_file = config_dir / "app.log"
    from utils.logger import setup_logger
    setup_logger(log_file=str(log_file))

    # ── 4. تحميل الإعدادات ──
    from config.settings import SettingsManager
    from core.model import BookSettings

    settings_mgr = SettingsManager(config_dir)
    settings = settings_mgr.load()

    # ── 5. تعيين لغة الواجهة ──
    from utils.i18n import get_i18n
    i18n = get_i18n(settings.language)

    # ── 6. بدء واجهة المستخدم ──
    import customtkinter as ctk
    from ui.app import MainApplication

    app = MainApplication(settings=settings, config_dir=config_dir)
    app.protocol("WM_DELETE_WINDOW", app._on_close)
    app.mainloop()


if __name__ == "__main__":
    main()