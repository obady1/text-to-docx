"""Custom functional UI widget component elements toolkit: Selectors, Loggers, Status bars."""

import customtkinter as ctk
from pathlib import Path
from typing import Callable, Optional

from utils.i18n import get_i18n

_i18n = get_i18n()


class FolderSelector(ctk.CTkFrame):
    """Custom folder exploration select panel supporting file path drag-and-drop operations mechanics."""

    def __init__(
        self,
        master,
        label_text: str = "",
        on_select: Optional[Callable[[str], None]] = None,
        **kwargs,
    ) -> None:
        super().__init__(master, **kwargs)

        self._on_select = on_select
        self._path = ""

        # Title Headings labels layouts fields configurations elements
        if label_text:
            self._label = ctk.CTkLabel(self, text=label_text, anchor="w")
            self._label.pack(fill="x", pady=(0, 4))

        # Horizontal alignment row elements box setup wrappers mapping lines
        self._entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self._entry_frame.pack(fill="x")

        self._entry = ctk.CTkEntry(
            self._entry_frame,
            placeholder_text=_i18n.t("drag_hint"),
            state="normal",
        )
        self._entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self._btn = ctk.CTkButton(
            self._entry_frame,
            text=_i18n.t("browse"),
            width=90,
            command=self._browse,
        )
        self._btn.pack(side="right")

        # Initialize cross-framework DnD bindings hooks logic lines safely
        self._setup_drag_drop()

    def _setup_drag_drop(self) -> None:
        """Binds internal field routines context elements directly over system file drop hooks modules."""
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD

            self._entry.drop_target_register(DND_FILES)
            self._entry.dnd_bind("<<Drop>>", self._on_drop)
        except ImportError:
            pass

    def _on_drop(self, event) -> None:
        """Handles structural file system drop operational callback context parameters safely."""
        path = event.data.strip("{}")  # Strips bracket wrappers artifacts typical inside specific OS frames
        if Path(path).is_dir():
            self.set_path(path)

    def _browse(self) -> None:
        """Launches explorer paths prompt interfaces windows selectors fields safely."""
        from tkinter import filedialog
        path = filedialog.askdirectory(title=_i18n.t("browse"))
        if path:
            self.set_path(path)

    def set_path(self, path: str) -> None:
        """Overwrites structural internal monitoring metrics parameters values updating view fields text inputs."""
        self._path = path
        self._entry.delete(0, "end")
        self._entry.insert(0, path)
        if self._on_select:
            self._on_select(path)

    def get_path(self) -> str:
        """Retrieves verified ongoing system selection folder paths strings safely."""
        return self._path

    def clear(self) -> None:
        """Flushes system entries fields inputs parameters data structural modifications text wrappers."""
        self._path = ""
        self._entry.delete(0, "end")


class LogWidget(ctk.CTkTextbox):
    """Categorized logging terminal element displaying contextual activities status traces."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.configure(state="disabled", wrap="word")

    def log(self, message: str, tag: str = "info") -> None:
        """Appends localized textual statement records inside execution terminal blocks fields tracking areas.

        Args:
            message: Raw messaging context text string statement.
            tag: Metric tracing level classification profiles flags (info, success, error, warning).
        """
        self.configure(state="normal")

        # Contextual icon map properties configurations entries logs traces symbols
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️",
            "progress": "📄",
        }
        icon = icons.get(tag, "•")

        self.insert("end", f"{icon} {message}\n")
        self.see("end")
        self.configure(state="disabled")


class ProgressPanel(ctk.CTkFrame):
    """Visualization status dashboard tracks displaying task completion fractions indicators bars and timers metrics."""

    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self._progress_bar = ctk.CTkProgressBar(self, height=20)
        self._progress_bar.pack(fill="x", pady=(0, 6))
        self._progress_bar.set(0)

        self._info_label = ctk.CTkLabel(
            self, text="—", anchor="w", height=20
        )
        self._info_label.pack(fill="x")

        self._start_time: Optional[float] = None

    def update_progress(
        self, current: int, total: int, filename: str = ""
    ) -> None:
        """Advances active bar positions parameters scales recalculating estimated operational termination times.

        Args:
            current: Aggregated values quantity scale files mapped successfully.
            total: Quantitative total scale parameters context target boundaries limitations benchmarks.
            filename: Active ongoing filename targets labels traces items strings.
        """
        import time

        if self._start_time is None:
            self._start_time = time.time()

        if total > 0:
            fraction = current / total
            self._progress_bar.set(fraction)

            # Compute ongoing temporal velocity estimations properties metrics safely
            elapsed = time.time() - self._start_time
            if current > 0:
                avg_per_file = elapsed / current
                remaining = avg_per_file * (total - current)
                time_str = self._format_time(remaining)
            else:
                time_str = "—"

            info = _i18n.t(
                "files_processed", current=current, total=total
            )
            if filename:
                info += f"  │  {_i18n.t('processing', name=filename)}"
            info += f"  │  {_i18n.t('time_remaining', time=time_str)}"

            self._info_label.configure(text=info)

    def reset(self) -> None:
        """Resets visual properties scales indexes to standard starting parameters baseline settings values."""
        self._progress_bar.set(0)
        self._info_label.configure(text="—")
        self._start_time = None

    @staticmethod
    def _format_time(seconds: float) -> str:
        """Converts raw timestamps double metrics values fields entries inside easy-to-read format text blocks strings."""
        if seconds < 60:
            return f"{seconds:.0f}s"
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        if minutes < 60:
            return f"{minutes}m {secs}s"
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"