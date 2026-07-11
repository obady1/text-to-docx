"""نظام تعدد اللغات (Arabic / English)."""

from typing import Optional


class I18n:
    """مدير الترجمة البسيط.

    يدعم العربية والإنجليزية مع إمكانية إضافة لغات أخرى.
    """

    _translations: dict[str, dict[str, str]] = {
        "ar": {
            # ── عام ──
            "app_title": "محوّل النصوص إلى Word",
            "start": "بدء التحويل",
            "stop": "إيقاف",
            "open_file": "فتح الملف",
            "close": "إغلاق",
            "ok": "موافق",
            "cancel": "إلغاء",
            "save": "حفظ",
            "reset": "إعادة تعيين",
            "browse": "استعراض...",
            "exit": "خروج",

            # ── الواجهة الرئيسية ──
            "input_folder": "مجلد ملفات TXT:",
            "output_folder": "مجلد الحفظ:",
            "output_filename": "اسم الملف:",
            "book_name": "اسم الكتاب:",
            "author_name": "اسم المؤلف:",
            "progress": "التقدم:",
            "log": "السجل:",
            "files_found": "تم العثور على {count} ملف",
            "processing": "جارٍ معالجة: {name}",
            "complete": "اكتمل التحويل بنجاح!",
            "failed": "فشل التحويل!",
            "cancelled": "تم إلغاء العملية.",
            "time_remaining": "الوقت المتبقي: {time}",
            "files_processed": "الملفات المنجزة: {current}/{total}",
            "no_files": "لم يتم العثور على ملفات TXT في المجلد المحدد.",
            "select_folder_first": "يرجى اختيار مجلد الملفات أولاً.",
            "select_output_first": "يرجى اختيار مجلد الحفظ أولاً.",
            "drag_hint": "أو اسحب وأفلت المجلد هنا",
            "elapsed": "الوقت المنقضي: {time}",
            "file_saved": "تم حفظ الملف في: {path}",

            # ── القائمة ──
            "menu_file": "ملف",
            "menu_settings": "إعدادات",
            "menu_help": "مساعدة",
            "menu_about": "حول البرنامج",
            "menu_preview": "معاينة قبل التصدير",
            "menu_theme": "السمة",
            "menu_language": "اللغة",
            "menu_dark": "داكن",
            "menu_light": "فاتح",

            # ── الإعدادات ──
            "settings_title": "إعدادات المستند",
            "tab_general": "عام",
            "tab_page": "الصفحة",
            "tab_components": "المكونات",
            "tab_advanced": "متقدم",
            "font": "الخط:",
            "font_size": "حجم الخط:",
            "heading_font": "خط العناوين:",
            "heading_size": "حجم العناوين:",
            "page_size": "حجم الورق:",
            "margins": "الهوامش (سم):",
            "margin_top": "أعلى:",
            "margin_bottom": "أسفل:",
            "margin_left": "يسار:",
            "margin_right": "يمين:",
            "text_direction": "اتجاه النص:",
            "line_spacing": "تباعد الأسطر:",
            "para_spacing": "مسافة بعد الفقرة (سم):",
            "first_indent": "إزاحة السطر الأول (سم):",
            "add_cover": "إضافة صفحة غلاف",
            "add_copyright": "إضافة صفحة حقوق النشر",
            "add_toc": "إضافة جدول محتويات",
            "add_page_numbers": "إضافة ترقيم الصفحات",
            "add_header": "إضافة ترويسة (Header)",
            "add_footer": "إضافة تذييل (Footer)",
            "copyright_text": "نص حقوق النشر:",
            "intro_text": "نص المقدمة:",
            "conclusion_text": "نص الخاتمة:",
            "header_text": "نص الترويسة:",
            "footer_text": "نص التذييل:",
            "cover_image": "صورة الغلاف (اختياري):",
            "settings_saved": "تم حفظ الإعدادات بنجاح.",
            "settings_reset": "تم إعادة التعيين إلى القيم الافتراضية.",

            # ── حول ──
            "about_title": "حول البرنامج",
            "about_version": "الإصدار 1.0.0",
            "about_desc": (
                "برنامج احترافي لتحويل مئات ملفات النصوص (TXT)\n"
                "إلى ملف Word (.docx) منسق وجاهز للطباعة والنشر.\n\n"
                "يدعم اللغة العربية والإنجليزية بالكامل\n"
                "مع إمكانية تخصيص الخطوط والهوامش والصفحات."
            ),
            "about_dev": "التطوير بواسطة: فريق التطوير",

            # ── المعاينة ──
            "preview_title": "معاينة الإعدادات",
            "preview_summary": "ملخص الإعدادات الحالية قبل التصدير:",
        },
        "en": {
            # ── General ──
            "app_title": "TXT to Word Converter",
            "start": "Start Conversion",
            "stop": "Stop",
            "open_file": "Open File",
            "close": "Close",
            "ok": "OK",
            "cancel": "Cancel",
            "save": "Save",
            "reset": "Reset",
            "browse": "Browse...",
            "exit": "Exit",

            # ── Main UI ──
            "input_folder": "TXT Folder:",
            "output_folder": "Output Folder:",
            "output_filename": "File Name:",
            "book_name": "Book Title:",
            "author_name": "Author Name:",
            "progress": "Progress:",
            "log": "Log:",
            "files_found": "Found {count} files",
            "processing": "Processing: {name}",
            "complete": "Conversion completed successfully!",
            "failed": "Conversion failed!",
            "cancelled": "Operation cancelled.",
            "time_remaining": "Time remaining: {time}",
            "files_processed": "Files processed: {current}/{total}",
            "no_files": "No TXT files found in the selected folder.",
            "select_folder_first": "Please select an input folder first.",
            "select_output_first": "Please select an output folder first.",
            "drag_hint": "or drag & drop a folder here",
            "elapsed": "Elapsed time: {time}",
            "file_saved": "File saved to: {path}",

            # ── Menu ──
            "menu_file": "File",
            "menu_settings": "Settings",
            "menu_help": "Help",
            "menu_about": "About",
            "menu_preview": "Preview Before Export",
            "menu_theme": "Theme",
            "menu_language": "Language",
            "menu_dark": "Dark",
            "menu_light": "Light",

            # ── Settings ──
            "settings_title": "Document Settings",
            "tab_general": "General",
            "tab_page": "Page",
            "tab_components": "Components",
            "tab_advanced": "Advanced",
            "font": "Font:",
            "font_size": "Font Size:",
            "heading_font": "Heading Font:",
            "heading_size": "Heading Size:",
            "page_size": "Page Size:",
            "margins": "Margins (cm):",
            "margin_top": "Top:",
            "margin_bottom": "Bottom:",
            "margin_left": "Left:",
            "margin_right": "Right:",
            "text_direction": "Text Direction:",
            "line_spacing": "Line Spacing:",
            "para_spacing": "Paragraph Spacing (cm):",
            "first_indent": "First Line Indent (cm):",
            "add_cover": "Add Cover Page",
            "add_copyright": "Add Copyright Page",
            "add_toc": "Add Table of Contents",
            "add_page_numbers": "Add Page Numbers",
            "add_header": "Add Header",
            "add_footer": "Add Footer",
            "copyright_text": "Copyright Text:",
            "intro_text": "Introduction Text:",
            "conclusion_text": "Conclusion Text:",
            "header_text": "Header Text:",
            "footer_text": "Footer Text:",
            "cover_image": "Cover Image (optional):",
            "settings_saved": "Settings saved successfully.",
            "settings_reset": "Reset to default values.",

            # ── About ──
            "about_title": "About",
            "about_version": "Version 1.0.0",
            "about_desc": (
                "Professional tool to convert hundreds of text files (TXT)\n"
                "into a formatted Word document (.docx) ready for print and publishing.\n\n"
                "Full Arabic and English support\n"
                "with customizable fonts, margins, and page layouts."
            ),
            "about_dev": "Developed by: Dev Team",

            # ── Preview ──
            "preview_title": "Settings Preview",
            "preview_summary": "Current settings summary before export:",
        },
    }

    def __init__(self, language: str = "ar") -> None:
        self._language = language

    @property
    def language(self) -> str:
        """اللغة الحالية."""
        return self._language

    @language.setter
    def language(self, value: str) -> None:
        """تغيير اللغة."""
        if value in self._translations:
            self._language = value

    def t(self, key: str, **kwargs) -> str:
        """ترجمة مفتاح نصي مع استبدال المتغيرات.

        Args:
            key: مفتاح الترجمة.
            **kwargs: متغيرات الاستبدال (مثال: count=5).

        Returns:
            النص المترجم أو المفتاح نفسه إذا لم يُوجد.
        """
        lang_dict = self._translations.get(self._language, {})
        text = lang_dict.get(key, self._translations.get("ar", {}).get(key, key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text

    def available_languages(self) -> list[str]:
        """قائمة اللغات المتاحة."""
        return list(self._translations.keys())


# نسخة عامة واحدة
_i18n_instance: Optional[I18n] = None


def get_i18n(language: str = "ar") -> I18n:
    """الحصول على نسخة واحدة من مدير الترجمة."""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18n(language)
    return _i18n_instance