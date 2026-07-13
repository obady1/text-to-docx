"""النافذة الرئيسية لتطبيق محوّل النصوص إلى Word."""

import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

import customtkinter as ctk

from config.settings import SettingsManager
from core.model import BookSettings, ARABIC_FONTS, LATIN_FONTS
from core.file_reader import FileReader
from core.text_processor import TextProcessor
from core.docx_builder import DocxBuilder
from styles.theme import ThemeManager
from utils.logger import get_logger, setup_logger
from utils.i18n import get_i18n
from utils.thread_worker import ConversionWorker
from ui.widgets import FolderSelector, LogWidget, ProgressPanel
from ui.settings_dialog import SettingsDialog
from ui.about_dialog import AboutDialog
from ui.preview_dialog import PreviewDialog

logger = get_logger(__name__)
_i18n = get_i18n()


class MainApplication(ctk.CTk):
    """النافذة الرئيسية للتطبيق.

    تجمع بين جميع عناصر الواجهة وتنسق بينها وبين منطق الأعمال.
    """

    def __init__(self, settings: BookSettings, config_dir: Path) -> None:
        super().__init__()

        self._settings = settings
        self._config_dir = config_dir
        self._theme = ThemeManager(settings.theme)
        self._settings_manager = SettingsManager(config_dir)
        self._worker: Optional[ConversionWorker] = None
        self._file_count = 0

        # إعداد النافذة
        self._setup_window()
        self._setup_menu()
        self._build_ui()
        self._apply_theme()

        logger.info("تم تشغيل التطبيق بنجاح")

    # ══════════════════════════════════════════════
    #  إعداد النافذة
    # ══════════════════════════════════════════════

    def _setup_window(self) -> None:
        """إعداد خصائص النافذة الأساسية."""
        self.title(_i18n.t("app_title"))
        self.geometry("780x680")
        self.minsize(650, 550)

        # تعيين الأيقونة
        icon_path = self._config_dir / "icon.ico"
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        # إعداد السمة
        ctk.set_appearance_mode(self._theme.current)
        ctk.set_default_color_theme("blue")

    def _setup_menu(self) -> None:
        """إعداد قائمة النافذة."""
        # ملاحظة: CustomTkinter لا يدعم القوائم الأصلية مباشرة
        # نستخدم tkinter.Menu كحل بديل
        menubar = self._get_native_menu()

        # قائمة ملف
        file_menu = self._add_menu(menubar, _i18n.t("menu_file"))
        file_menu.add_command(
            label=_i18n.t("menu_preview"),
            command=self._show_preview,
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=_i18n.t("exit"),
            command=self._on_close,
        )

        # قائمة إعدادات
        settings_menu = self._add_menu(menubar, _i18n.t("menu_settings"))
        settings_menu.add_command(
            label=_i18n.t("menu_settings"),
            command=self._show_settings,
        )
        settings_menu.add_separator()

        # قائمة فرعية للسمة
        theme_menu = self._add_submenu(settings_menu, _i18n.t("menu_theme"))
        theme_menu.add_command(
            label=_i18n.t("menu_dark"),
            command=lambda: self._change_theme("dark"),
        )
        theme_menu.add_command(
            label=_i18n.t("menu_light"),
            command=lambda: self._change_theme("light"),
        )

        settings_menu.add_separator()

        # قائمة فرعية للغة
        lang_menu = self._add_submenu(settings_menu, _i18n.t("menu_language"))
        lang_menu.add_command(
            label="العربية",
            command=lambda: self._change_language("ar"),
        )
        lang_menu.add_command(
            label="English",
            command=lambda: self._change_language("en"),
        )

        # قائمة مساعدة
        help_menu = self._add_menu(menubar, _i18n.t("menu_help"))
        help_menu.add_command(
            label=_i18n.t("menu_about"),
            command=self._show_about,
        )

        self.configure(menu=menubar)

    def _get_native_menu(self):
        """الحصول على قائمة أصلية حسب النظام."""
        from tkinter import Menu
        return Menu(self)

    def _add_menu(self, parent, label: str):
        """إضافة قائمة رئيسية."""
        menu = self._create_submenu(parent)
        parent.add_cascade(label=label, menu=menu)
        return menu

    def _add_submenu(self, parent, label: str):
        """إضافة قائمة فرعية."""
        menu = self._create_submenu(parent)
        parent.add_cascade(label=label, menu=menu)
        return menu

    def _create_submenu(self, parent):
        """إنشاء قائمة فرعية."""
        from tkinter import Menu
        return Menu(parent, tearoff=0)

    # ══════════════════════════════════════════════
    #  بناء الواجهة
    # ══════════════════════════════════════════════

    def _build_ui(self) -> None:
        """بناء جميع عناصر الواجهة."""
        # الحاوية الرئيسية مع تمرير
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=15, pady=10)

        # ── القسم العلوي: المجلدات والمعلومات ──
        top_frame = ctk.CTkFrame(main_frame)
        top_frame.pack(fill="x", pady=(0, 10))

        # مجلد الإدخال
        self._input_selector = FolderSelector(
            top_frame,
            label_text=_i18n.t("input_folder"),
            on_select=self._on_input_selected,
        )
        self._input_selector.pack(fill="x", padx=10, pady=(10, 5))

        # مجلد الإخراج واسم الملف
        output_row = ctk.CTkFrame(top_frame, fg_color="transparent")
        output_row.pack(fill="x", padx=10, pady=(5, 10))

        self._output_selector = FolderSelector(
            output_row,
            label_text=_i18n.t("output_folder"),
            on_select=self._on_output_selected,
        )
        self._output_selector.pack(side="left", fill="x", expand=True, padx=(0, 8))

        # حقل اسم الملف
        name_frame = ctk.CTkFrame(output_row, fg_color="transparent")
        name_frame.pack(side="right")

        self._filename_label = ctk.CTkLabel(
            name_frame, text=_i18n.t("output_filename"), anchor="w"
        )
        self._filename_label.pack(anchor="w")

        self._filename_entry = ctk.CTkEntry(name_frame, width=200, placeholder_text="book.docx")
        self._filename_entry.pack(fill="x")

        # اسم الكتاب والمؤلف
        info_row = ctk.CTkFrame(top_frame, fg_color="transparent")
        info_row.pack(fill="x", padx=10, pady=(0, 10))

        book_frame = ctk.CTkFrame(info_row, fg_color="transparent")
        book_frame.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._book_label = ctk.CTkLabel(
            book_frame, text=_i18n.t("book_name"), anchor="w"
        )
        self._book_label.pack(anchor="w")

        self._book_entry = ctk.CTkEntry(book_frame, placeholder_text=_i18n.t("book_name"))
        self._book_entry.pack(fill="x")

        author_frame = ctk.CTkFrame(info_row, fg_color="transparent")
        author_frame.pack(side="right", fill="x", expand=True)

        self._author_label = ctk.CTkLabel(
            author_frame, text=_i18n.t("author_name"), anchor="w"
        )
        self._author_label.pack(anchor="w")

        self._author_entry = ctk.CTkEntry(author_frame, placeholder_text=_i18n.t("author_name"))
        self._author_entry.pack(fill="x")

        # ── شريط التقدم ──
        self._progress_panel = ProgressPanel(main_frame)
        self._progress_panel.pack(fill="x", pady=(0, 10))

        # ── السجل ──
        log_label = ctk.CTkLabel(
            main_frame, text=_i18n.t("log"), anchor="w", font=ctk.CTkFont(weight="bold")
        )
        log_label.pack(fill="x", pady=(0, 4))

        self._log_widget = LogWidget(main_frame, height=150)
        self._log_widget.pack(fill="both", expand=True, pady=(0, 10))

        # ── الأزرار ──
        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(fill="x")

        self._open_btn = ctk.CTkButton(
            btn_frame,
            text=_i18n.t("open_file"),
            width=120,
            fg_color="gray40",
            hover_color="gray30",
            command=self._open_output_file,
            state="disabled",
        )
        self._open_btn.pack(side="right", padx=(8, 0))

        self._stop_btn = ctk.CTkButton(
            btn_frame,
            text=_i18n.t("stop"),
            width=100,
            fg_color="#c0392b",
            hover_color="#a93226",
            command=self._stop_conversion,
            state="disabled",
        )
        self._stop_btn.pack(side="right", padx=(8, 0))

        self._start_btn = ctk.CTkButton(
            btn_frame,
            text=_i18n.t("start"),
            width=160,
            command=self._start_conversion,
        )
        self._start_btn.pack(side="right")

        # استعادة المسارات الأخيرة
        self._restore_last_paths()

    # ══════════════════════════════════════════════
    #  معالجات الأحداث
    # ══════════════════════════════════════════════

    def _on_input_selected(self, path: str) -> None:
        """عند اختيار مجلد الإدخال."""
        try:
            reader = FileReader()
            files = reader.get_txt_files(path)
            self._file_count = len(files)
            self._log_widget.log(
                _i18n.t("files_found", count=self._file_count), "success"
            )
            # اقتراح اسم الملف من اسم المجلد
            folder_name = Path(path).name
            if not self._filename_entry.get():
                self._filename_entry.delete(0, "end")
                self._filename_entry.insert(0, f"{folder_name}.docx")
            if not self._book_entry.get():
                self._book_entry.delete(0, "end")
                self._book_entry.insert(0, folder_name)
        except Exception as e:
            self._log_widget.log(str(e), "error")

    def _on_output_selected(self, path: str) -> None:
        """عند اختيار مجلد الإخراج."""
        self._log_widget.log(f"📁 {path}", "info")

    def _restore_last_paths(self) -> None:
        """استعادة المسارات الأخيرة من الإعدادات."""
        s = self._settings
        if s.last_input_folder and Path(s.last_input_folder).is_dir():
            self._input_selector.set_path(s.last_input_folder)
        if s.last_output_folder and Path(s.last_output_folder).is_dir():
            self._output_selector.set_path(s.last_output_folder)
        if s.book_title:
            self._book_entry.delete(0, "end")
            self._book_entry.insert(0, s.book_title)
        if s.author_name:
            self._author_entry.delete(0, "end")
            self._author_entry.insert(0, s.author_name)

    # ══════════════════════════════════════════════
    #  عملية التحويل
    # ══════════════════════════════════════════════

    def _start_conversion(self) -> None:
        """بدء عملية التحويل."""
        # التحقق من المدخلات
        input_path = self._input_selector.get_path()
        if not input_path or not Path(input_path).is_dir():
            self._log_widget.log(_i18n.t("select_folder_first"), "warning")
            return

        output_folder = self._output_selector.get_path()
        if not output_folder or not Path(output_folder).is_dir():
            self._log_widget.log(_i18n.t("select_output_first"), "warning")
            return

        filename = self._filename_entry.get().strip()
        if not filename:
            filename = "output.docx"
        if not filename.lower().endswith(".docx"):
            filename += ".docx"

        output_path = str(Path(output_folder) / filename)

        # تحديث إعدادات الكتاب من الحقول
        self._settings.book_title = self._book_entry.get().strip()
        self._settings.author_name = self._author_entry.get().strip()
        self._settings.last_input_folder = input_path
        self._settings.last_output_folder = output_folder

        # حفظ الإعدادات
        try:
            self._settings_manager.save(self._settings)
        except Exception as e:
            logger.warning("تعذّر حفظ الإعدادات: %s", e)

        # تحديث حالة الأزرار
        self._start_btn.configure(state="disabled")
        self._stop_btn.configure(state="normal")
        self._open_btn.configure(state="disabled")
        self._progress_panel.reset()

        self._log_widget.log("🚀 بدء عملية التحويل...", "info")

        # بدء خيط العمل
        self._worker = ConversionWorker(
            target=self._conversion_task,
            on_progress=self._on_progress,
            on_complete=self._on_complete,
            on_log=lambda msg: self._log_widget.log(msg),
        )
        self._worker.start(input_path, output_path)

    def _conversion_task(self, input_path: str, output_path: str) -> dict:
        """المهمة الرئيسية للتحويل (تُنفذ في خيط منفصل)."""
        reader = FileReader()
        processor = TextProcessor(
            first_line_indent_cm=self._settings.first_line_indent_cm
        )

        # قراءة الدروس
        self._worker._safe_log("📖 جارٍ قراءة الملفات...")
        lessons = reader.read_lessons(input_path)

        if not lessons:
            return {
                "success": False,
                "error": _i18n.t("no_files"),
                "output_path": "",
            }

        # معالجة النصوص
        self._worker._safe_log("🧹 جارٍ تنظيف ومعالجة النصوص...")
        lessons = processor.process_lessons(lessons)

        # بناء المستند
        self._worker._safe_log("📝 جارٍ بناء مستند Word...")
        builder = DocxBuilder(
            settings=self._settings,
            progress_callback=self._worker._safe_progress,
            stop_check=self._worker.stop_check,
        )

        stats = builder.build(lessons)

        if stats.cancelled:
            return {
                "success": False,
                "error": _i18n.t("cancelled"),
                "output_path": "",
                "stats": {
                    "processed": stats.processed_files,
                    "failed": stats.failed_files,
                    "elapsed": stats.elapsed_seconds,
                },
            }

        if stats.failed_files > 0 and stats.processed_files == 0:
            return {
                "success": False,
                "error": f"فشلت جميع الملفات ({stats.failed_files})",
                "output_path": "",
            }

        # حفظ المستند
        builder.save(output_path)

        return {
            "success": True,
            "output_path": output_path,
            "stats": {
                "total": stats.total_files,
                "processed": stats.processed_files,
                "failed": stats.failed_files,
                "failed_names": stats.failed_filenames,
                "elapsed": stats.elapsed_seconds,
            },
        }

    def _on_progress(self, current: int, total: int, name: str) -> None:
        """تحديث التقدم من خيط العمل."""
        # يجب تحديث الواجهة من الخيط الرئيسي
        self.after(0, self._progress_panel.update_progress, current, total, name)

    def _on_complete(self, result) -> None:
        """عند انتهاء عملية التحويل."""
        # العودة إلى الخيط الرئيسي لتحديث الواجهة
        self.after(0, self._handle_result, result)

    def _handle_result(self, result) -> None:
        """معالجة نتيجة التحويل وتحديث الواجهة."""
        self._start_btn.configure(state="normal")
        self._stop_btn.configure(state="disabled")

        if result.success:
            self._log_widget.log(_i18n.t("complete"), "success")
            self._log_widget.log(
                _i18n.t("file_saved", path=result.output_path), "success"
            )
            if result.stats:
                s = result.stats
                self._log_widget.log(
                    f"📊 {s.get('processed', 0)} ملف تم بنجاح | "
                    f"{s.get('failed', 0)} فشل | "
                    f"{s.get('elapsed', 0):.1f} ثانية",
                    "info",
                )
                if s.get("failed_names"):
                    for name in s["failed_names"]:
                        self._log_widget.log(f"  ⚠️ {name}", "warning")

            self._last_output_path = result.output_path
            self._open_btn.configure(state="normal")
            self._progress_panel.update_progress(1, 1, "")
        else:
            self._log_widget.log(result.error_message or _i18n.t("failed"), "error")
            self._progress_panel.reset()

        self._worker = None

    def _stop_conversion(self) -> None:
        """طلب إيقاف عملية التحويل."""
        if self._worker and self._worker.is_running:
            self._worker.stop()

    def _open_output_file(self) -> None:
        """فتح الملف الناتج بالبرنامج الافتراضي."""
        path = getattr(self, "_last_output_path", "")
        if not path or not Path(path).exists():
            return

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", path], check=True)
            else:  # Linux
                subprocess.run(["xdg-open", path], check=True)
            self._log_widget.log(f"📂 تم فتح: {path}", "info")
        except Exception as e:
            self._log_widget.log(f"تعذّر فتح الملف: {e}", "error")

    # ══════════════════════════════════════════════
    #  النوافذ المنبثقة
    # ══════════════════════════════════════════════

    def _show_settings(self) -> None:
        """فتح نافذة الإعدادات."""
        dialog = SettingsDialog(
            self,
            settings=self._settings,
            on_save=self._on_settings_saved,
        )

    def _on_settings_saved(self, settings: BookSettings) -> None:
        """عند حفظ الإعدادات من نافذة الإعدادات."""
        self._settings = settings
        try:
            self._settings_manager.save(settings)
            self._log_widget.log(_i18n.t("settings_saved"), "success")
        except Exception as e:
            self._log_widget.log(f"خطأ في الحفظ: {e}", "error")

        # تحديث الحقول
        if settings.book_title:
            self._book_entry.delete(0, "end")
            self._book_entry.insert(0, settings.book_title)
        if settings.author_name:
            self._author_entry.delete(0, "end")
            self._author_entry.insert(0, settings.author_name)

    def _show_about(self) -> None:
        """فتح نافذة حول البرنامج."""
        AboutDialog(self)

    def _show_preview(self) -> None:
        """فتح نافذة المعاينة."""
        self._sync_settings_from_ui()
        PreviewDialog(self, self._settings, self._file_count)

    # ══════════════════════════════════════════════
    #  السمة واللغة
    # ══════════════════════════════════════════════

    def _change_theme(self, theme: str) -> None:
        """تغيير سمة الواجهة."""
        self._theme.set_theme(theme)
        self._apply_theme()
        self._settings.theme = theme
        self._save_settings_silent()

    def _apply_theme(self) -> None:
        """تطبيق السمة الحالية على الواجهة."""
        ctk.set_appearance_mode(self._theme.current)

    def _change_language(self, lang: str) -> None:
        """تغيير لغة الواجهة (يتطلب إعادة تشغيل)."""
        if lang != self._settings.language:
            self._settings.language = lang
            self._save_settings_silent()
            self._log_widget.log(
                "🔄 تم تغيير اللغة. يُرجى إعادة تشغيل البرنامج.",
                "warning",
            )

    def _sync_settings_from_ui(self) -> None:
        """مزامنة إعدادات الكتاب من حقول الواجهة."""
        self._settings.book_title = self._book_entry.get().strip()
        self._settings.author_name = self._author_entry.get().strip()

    def _save_settings_silent(self) -> None:
        """حفظ الإعدادات بصمت (بدون رسالة)."""
        try:
            self._settings_manager.save(self._settings)
        except Exception as e:
            logger.warning("تعذّر حفظ الإعدادات: %s", e)

    # ══════════════════════════════════════════════
    #  أحداث النافذة
    # ══════════════════════════════════════════════

    def _on_close(self) -> None:
        """معالجة إغلاق النافذة."""
        if self._worker and self._worker.is_running:
            self._worker.stop()
            self.after(500, self._on_close)
            return
        self._sync_settings_from_ui()
        self._save_settings_silent()
        self.destroy()

    def destroy(self) -> None:
        """تدمير النافذة بأمان."""
        try:
            super().destroy()
        except Exception:
            pass