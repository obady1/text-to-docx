"""Detailed configuration control dashboard panel detailing user system setup flags."""

import customtkinter as ctk

from core.model import BookSettings, ARABIC_FONTS, LATIN_FONTS, PAGE_DIMENSIONS_CM
from utils.i18n import get_i18n

_i18n = get_i18n()


class SettingsDialog(ctk.CTkToplevel):
    """Comprehensive multi-tabbed layout settings dialogue frame window."""

    def __init__(
        self, parent, settings: BookSettings, on_save=None, **kwargs
    ) -> None:
        super().__init__(parent, **kwargs)

        self.title(_i18n.t("settings_title"))
        self.geometry("600x580")
        self.resizable(False, True)
        self.transient(parent)
        self.grab_set()

        self._settings = settings
        self._on_save = on_save
        self._widgets: dict[str, ctk.CTkBaseClass] = {}

        self._build_ui()
        self._load_settings()
        self._center_on_parent(parent)

    def _center_on_parent(self, parent) -> None:
        """Centers widget position geometry parameters targeting root frames safely."""
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    # ──────────────────────────────────────────────
    # UI Layout Construction Details
    # ──────────────────────────────────────────────

    def _build_ui(self) -> None:
        """Draws visual nodes structure trees along system tab pages views."""
        # Tab view wrapper element container
        self._tabview = ctk.CTkTabview(self)
        self._tabview.pack(fill="both", expand=True, padx=15, pady=(15, 5))

        tab_general = self._tabview.add(_i18n.t("tab_general"))
        tab_page = self._tabview.add(_i18n.t("tab_page"))
        tab_components = self._tabview.add(_i18n.t("tab_components"))
        tab_advanced = self._tabview.add(_i18n.t("tab_advanced"))

        self._build_general_tab(tab_general)
        self._build_page_tab(tab_page)
        self._build_components_tab(tab_components)
        self._build_advanced_tab(tab_advanced)

        # Control panel execution operations buttons layout wrapper row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=15, pady=10)

        reset_btn = ctk.CTkButton(
            btn_frame,
            text=_i18n.t("reset"),
            width=100,
            fg_color="gray40",
            hover_color="gray30",
            command=self._reset,
        )
        reset_btn.pack(side="right", padx=(8, 0))

        save_btn = ctk.CTkButton(
            btn_frame,
            text=_i18n.t("save"),
            width=120,
            command=self._save,
        )
        save_btn.pack(side="right")

    def _build_general_tab(self, parent) -> None:
        """Builds typography adjustments selectors fields: Fonts, Sizes, Orientations."""
        fonts = ARABIC_FONTS + LATIN_FONTS

        # Text Body typography font definitions selector properties
        self._add_labeled_option(
            parent, _i18n.t("font"), "font_name", fonts, row=0
        )

        # Text Body typography point font sizes inputs parameter
        self._add_labeled_entry(
            parent, _i18n.t("font_size"), "font_size", row=1
        )

        # Heading elements typography font type selectors
        self._add_labeled_option(
            parent, _i18n.t("heading_font"), "heading_font_name", fonts, row=2
        )

        # Heading structural dimensions point text sizing values entries
        self._add_labeled_entry(
            parent, _i18n.t("heading_size"), "heading_font_size", row=3
        )

        # Reading workflow text direction orientation selector configs
        self._add_labeled_option(
            parent,
            _i18n.t("text_direction"),
            "text_direction",
            ["RTL", "LTR"],
            row=4,
        )

    def _build_page_tab(self, parent) -> None:
        """Configures systemic paper size layout sheets parameters and margin spaces fields."""
        page_sizes = list(PAGE_DIMENSIONS_CM.keys())

        self._add_labeled_option(
            parent, _i18n.t("page_size"), "page_size", page_sizes, row=0
        )

        # Document Margin spatial dimensions fields layout blocks wrapper
        margin_frame = ctk.CTkFrame(parent, fg_color="transparent")
        margin_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(15, 5), padx=10)

        ctk.CTkLabel(
            margin_frame, text=_i18n.t("margins"), font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w")

        margins_grid = ctk.CTkFrame(margin_frame, fg_color="transparent")
        margins_grid.pack(fill="x", pady=5)

        self._add_margin_field(margins_grid, _i18n.t("margin_top"), "margin_top_cm", 0, 0)
        self._add_margin_field(margins_grid, _i18n.t("margin_bottom"), "margin_bottom_cm", 0, 1)
        self._add_margin_field(margins_grid, _i18n.t("margin_left"), "margin_left_cm", 1, 0)
        self._add_margin_field(margins_grid, _i18n.t("margin_right"), "margin_right_cm", 1, 1)

        # Line spacing scale height configuration factors metrics parameters
        self._add_labeled_entry(
            parent, _i18n.t("line_spacing"), "line_spacing", row=2
        )

        # Segment structural space separation heights metrics definitions
        self._add_labeled_entry(
            parent, _i18n.t("para_spacing"), "paragraph_spacing_after_cm", row=3
        )

        # First line indentation distance scales values metrics inputs controls
        self._add_labeled_entry(
            parent, _i18n.t("first_indent"), "first_line_indent_cm", row=4
        )

    def _build_components_tab(self, parent) -> None:
        """Draws optional architectural structural composition switches sections blocks."""
        switches = [
            ("add_cover", _i18n.t("add_cover")),
            ("add_copyright", _i18n.t("add_copyright")),
            ("add_toc", _i18n.t("add_toc")),
            ("add_page_numbers", _i18n.t("add_page_numbers")),
            ("add_header", _i18n.t("add_header")),
            ("add_footer", _i18n.t("add_footer")),
        ]

        for i, (key, text) in enumerate(switches):
            switch = ctk.CTkSwitch(parent, text=text)
            switch.grid(row=i, column=0, columnspan=2, sticky="w", padx=10, pady=4)
            self._widgets[key] = switch

        # Dynamic template textual context string textboxes inputs fields
        self._add_labeled_textbox(
            parent, _i18n.t("header_text"), "header_text", row=len(switches)
        )
        self._add_labeled_textbox(
            parent, _i18n.t("footer_text"), "footer_text", row=len(switches) + 1
        )
        self._add_labeled_textbox(
            parent, _i18n.t("copyright_text"), "copyright_text", row=len(switches) + 2
        )

    def _build_advanced_tab(self, parent) -> None:
        """Deploys advanced macro metadata textual segment blocks content editors maps."""
        self._add_labeled_textbox(
            parent, _i18n.t("intro_text"), "intro_text", row=0, height=120
        )
        self._add_labeled_textbox(
            parent, _i18n.t("conclusion_text"), "conclusion_text", row=1, height=120
        )

    # ──────────────────────────────────────────────
    # Layout Component Generator Toolkits Helpers
    # ──────────────────────────────────────────────

    def _add_labeled_option(
        self, parent, label: str, key: str, options: list, row: int
    ) -> None:
        """Appends descriptive titles stacked alongside specialized OptionMenu select fields safely."""
        ctk.CTkLabel(parent, text=label, anchor="w").grid(
            row=row, column=0, sticky="w", padx=10, pady=6
        )
        combo = ctk.CTkOptionMenu(parent, values=options, width=200)
        combo.grid(row=row, column=1, sticky="ew", padx=10, pady=6)
        parent.grid_columnconfigure(1, weight=1)
        self._widgets[key] = combo

    def _add_labeled_entry(
        self, parent, label: str, key: str, row: int
    ) -> None:
        """Appends standard label headings alongside single-line active text entry inputs elements."""
        ctk.CTkLabel(parent, text=label, anchor="w").grid(
            row=row, column=0, sticky="w", padx=10, pady=6
        )
        entry = ctk.CTkEntry(parent, width=200)
        entry.grid(row=row, column=1, sticky="ew", padx=10, pady=6)
        parent.grid_columnconfigure(1, weight=1)
        self._widgets[key] = entry

    def _add_labeled_textbox(
        self, parent, label: str, key: str, row: int, height: int = 80
    ) -> None:
        """Appends field titles context stacked on top of multi-line large Textbox area nodes fields."""
        ctk.CTkLabel(parent, text=label, anchor="w").grid(
            row=row, column=0, sticky="nw", padx=10, pady=6
        )
        textbox = ctk.CTkTextbox(parent, height=height, width=300)
        textbox.grid(row=row, column=1, sticky="ew", padx=10, pady=6)
        parent.grid_columnconfigure(1, weight=1)
        self._widgets[key] = textbox

    def _add_margin_field(
        self, parent, label: str, key: str, row: int, col: int
    ) -> None:
        """Draws individual single margins metrics parameter field controls within grid alignments blocks."""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=8, pady=4, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(frame, text=label, font=ctk.CTkFont(size=11)).pack(anchor="w")
        entry = ctk.CTkEntry(frame, width=100)
        entry.pack(fill="x")
        self._widgets[key] = entry

    # ──────────────────────────────────────────────
    # Data Population Synchronization Engines
    # ──────────────────────────────────────────────

    def _load_settings(self) -> None:
        """Loads and maps saved settings profiles to active UI input component elements fields."""
        s = self._settings

        for key, widget in self._widgets.items():
            value = getattr(s, key, None)
            if value is None:
                continue

            if isinstance(widget, ctk.CTkOptionMenu):
                options = widget.cget("values")
                if value in options:
                    widget.set(value)
                elif isinstance(value, str) and value in options:
                    widget.set(value)
            elif isinstance(widget, ctk.CTkEntry):
                widget.delete(0, "end")
                widget.insert(0, str(value))
            elif isinstance(widget, ctk.CTkSwitch):
                widget.configure(
                    on=bool(value) if not isinstance(value, bool) else value
                )
                if value:
                    widget.select()
                else:
                    widget.deselect()
            elif isinstance(widget, ctk.CTkTextbox):
                widget.delete("1.0", "end")
                widget.insert("1.0", str(value))

    def _collect_settings(self) -> BookSettings:
        """Collects field value configurations data maps to generate structural tracking objects updates."""
        s = self._settings

        for key, widget in self._widgets.items():
            try:
                if isinstance(widget, ctk.CTkOptionMenu):
                    setattr(s, key, widget.get())
                elif isinstance(widget, ctk.CTkEntry):
                    text = widget.get().strip()
                    current_type = type(getattr(s, key, ""))
                    if current_type == float:
                        setattr(s, key, float(text) if text else 0.0)
                    elif current_type == int:
                        setattr(s, key, int(text) if text else 0)
                    else:
                        setattr(s, key, text)
                elif isinstance(widget, ctk.CTkSwitch):
                    setattr(s, key, widget.get() == 1)
                elif isinstance(widget, ctk.CTkTextbox):
                    setattr(s, key, widget.get("1.0", "end").strip())
            except (ValueError, AttributeError) as e:
                from utils.logger import get_logger
                get_logger(__name__).warning("Error capturing parameter field target metrics key: %s: %s", key, e)

        return s

    def _save(self) -> None:
        """Triggers tracking variables changes flush savings routines updates and destroys dialogue modals."""
        self._settings = self._collect_settings()
        if self._on_save:
            self._on_save(self._settings)
        self.destroy()

    def _reset(self) -> None:
        """Resets configurations values variables entries parameters targeting baseline parameters profiles defaults."""
        defaults = BookSettings()
        self._settings = defaults
        self._load_settings()