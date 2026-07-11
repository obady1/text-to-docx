"""نافذة 'حول البرنامج'."""

import customtkinter as ctk

from utils.i18n import get_i18n

_i18n = get_i18n()


class AboutDialog(ctk.CTkToplevel):
    """نافذة حول البرنامج تعرض معلومات الإصدار والمطور."""

    def __init__(self, parent, **kwargs) -> None:
        super().__init__(parent, **kwargs)

        self.title(_i18n.t("about_title"))
        self.geometry("420x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._build_ui()

        # توسيط النافذة بالنسبة للأب
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _build_ui(self) -> None:
        """بناء عناصر النافذة."""
        padding = {"padx": 30, "pady": 8}

        # أيقونة / عنوان
        icon_label = ctk.CTkLabel(
            self,
            text="📖",
            font=ctk.CTkFont(size=48),
        )
        icon_label.pack(pady=(30, 10))

        title_label = ctk.CTkLabel(
            self,
            text=_i18n.t("app_title"),
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_label.pack(**padding)

        version_label = ctk.CTkLabel(
            self,
            text=_i18n.t("about_version"),
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        version_label.pack()

        # الفاصل
        sep = ctk.CTkFrame(self, height=1, fg_color="gray40")
        sep.pack(fill="x", padx=40, pady=12)

        # الوصف
        desc_label = ctk.CTkLabel(
            self,
            text=_i18n.t("about_desc"),
            font=ctk.CTkFont(size=12),
            justify="center",
            wraplength=350,
        )
        desc_label.pack(**padding)

        # المطور
        dev_label = ctk.CTkLabel(
            self,
            text=_i18n.t("about_dev"),
            font=ctk.CTkFont(size=11),
            text_color="gray",
        )
        dev_label.pack(pady=(0, 10))

        # زر الإغلاق
        close_btn = ctk.CTkButton(
            self,
            text=_i18n.t("close"),
            width=120,
            command=self.destroy,
        )
        close_btn.pack(pady=(5, 20))