"""نافذة معاينة الإعدادات قبل التصدير."""

import customtkinter as ctk

from core.models import BookSettings, PAGE_DIMENSIONS_CM
from utils.i18n import get_i18n

_i18n = get_i18n()


class PreviewDialog(ctk.CTkToplevel):
    """نافذة تعرض ملخصًا لجميع الإعدادات قبل بدء التحويل."""

    def __init__(self, parent, settings: BookSettings, file_count: int = 0, **kwargs) -> None:
        super().__init__(parent, **kwargs)

        self.title(_i18n.t("preview_title"))
        self.geometry("520x600")
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()

        self._settings = settings
        self._file_count = file_count
        self._build_ui()

        # توسيط
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self) -> None:
        """بناء واجهة المعاينة."""
        s = self._settings

        # العنوان
        header = ctk.CTkLabel(
            self,
            text=_i18n.t("preview_summary"),
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        )
        header.pack(fill="x", padx=20, pady=(20, 10))

        # إطار التمرير
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # بناء أقسام المعاينة
        self._add_section(scroll, "📋 المعلومات الأساسية", [
            (_i18n.t("book_name"), s.book_title or "—"),
            (_i18n.t("author_name"), s.author_name or "—"),
            ("عدد الملفات", str(self._file_count)),
        ])

        self._add_section(scroll, "🔤 الخط", [
            (_i18n.t("font"), s.font_name),
            (_i18n.t("font_size"), f"{s.font_size} pt"),
            (_i18n.t("heading_font"), s.heading_font_name),
            (_i18n.t("heading_size"), f"{s.heading_font_size} pt"),
        ])

        self._add_section(scroll, "📄 الصفحة", [
            (_i18n.t("page_size"), s.page_size),
            (_i18n.t("margin_top"), f"{s.margin_top_cm} cm"),
            (_i18n.t("margin_bottom"), f"{s.margin_bottom_cm} cm"),
            (_i18n.t("margin_left"), f"{s.margin_left_cm} cm"),
            (_i18n.t("margin_right"), f"{s.margin_right_cm} cm"),
            (_i18n.t("text_direction"), s.text_direction),
            (_i18n.t("line_spacing"), f"{s.line_spacing}"),
        ])

        components = []
        if s.add_cover:
            components.append("غلاف")
        if s.add_copyright:
            components.append("حقوق نشر")
        if s.add_toc:
            components.append("فهرس")
        if s.add_page_numbers:
            components.append("ترقيم صفحات")
        if s.add_header:
            components.append(f"ترويسة: {s.header_text or '—'}")
        if s.add_footer:
            components.append(f"تذييل: {s.footer_text or '—'}")
        if s.intro_text.strip():
            components.append("مقدمة")
        if s.conclusion_text.strip():
            components.append("خاتمة")

        self._add_section(
            scroll,
            "🧩 المكونات",
            [("المفعّلة", "، ".join(components) if components else "لا يوجد")],
        )

        # زر الإغلاق
        close_btn = ctk.CTkButton(
            self,
            text=_i18n.t("close"),
            width=120,
            command=self.destroy,
        )
        close_btn.pack(pady=(5, 20))

    def _add_section(
        self, parent, title: str, items: list[tuple[str, str]]
    ) -> None:
        """إضافة قسم للمعاينة."""
        # عنوان القسم
        sec_label = ctk.CTkLabel(
            parent,
            text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
            text_color="#4a90d9",
        )
        sec_label.pack(fill="x", pady=(12, 4))

        # عناصر القسم
        for key, value in items:
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=10, pady=1)

            key_label = ctk.CTkLabel(
                row,
                text=f"{key}: ",
                font=ctk.CTkFont(size=12),
                anchor="w",
                width=140,
                text_color="gray",
            )
            key_label.pack(side="right")

            val_label = ctk.CTkLabel(
                row,
                text=value,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w",
            )
            val_label.pack(side="right", fill="x", expand=True)

        # فاصل
        sep = ctk.CTkFrame(parent, height=1, fg_color="gray30")
        sep.pack(fill="x", padx=5, pady=4)