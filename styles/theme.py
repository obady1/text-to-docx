"""إدارة سمات الواجهة (داكن / فاتح)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeColors:
    """ألوان السمة."""
    bg: str
    fg: str
    accent: str
    surface: str
    border: str
    success: str
    error: str
    warning: str


# سمة داكنة
DARK_THEME = ThemeColors(
    bg="#1a1a2e",
    fg="#e0e0e0",
    accent="#16213e",
    surface="#0f3460",
    border="#2a2a4a",
    success="#4caf50",
    error="#f44336",
    warning="#ff9800",
)

# سمة فاتحة
LIGHT_THEME = ThemeColors(
    bg="#f5f5f5",
    fg="#333333",
    accent="#e0e0e0",
    surface="#ffffff",
    border="#cccccc",
    success="#2e7d32",
    error="#c62828",
    warning="#e65100",
)


class ThemeManager:
    """مدير السمات يتحكم في المظهر الداكن والفاتح."""

    def __init__(self, initial_theme: str = "dark") -> None:
        self._current = initial_theme

    @property
    def current(self) -> str:
        """اسم السمة الحالية."""
        return self._current

    @property
    def colors(self) -> ThemeColors:
        """ألوان السمة الحالية."""
        return DARK_THEME if self._current == "dark" else LIGHT_THEME

    def toggle(self) -> str:
        """تبديل السمة وإرجاع اسم السمة الجديدة."""
        self._current = "light" if self._current == "dark" else "dark"
        return self._current

    def set_theme(self, theme: str) -> None:
        """تعيين سمة محددة.

        Args:
            theme: 'dark' أو 'light'.
        """
        if theme in ("dark", "light"):
            self._current = theme