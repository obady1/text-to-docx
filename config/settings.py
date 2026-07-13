"""إدارة إعدادات المستخدم: الحفظ والاستعادة وإعادة التعيين."""

import json
import os
from pathlib import Path
from typing import Any

from core.model import BookSettings

# مجلد الإعدادات الافتراضي
CONFIG_DIR = Path.home() / ".txt_to_docx"
SETTINGS_FILE = CONFIG_DIR / "settings.json"


class SettingsManager:
    """مدير الإعدادات يحفظ ويستعيد إعدادات المستخدم كملف JSON."""

    def __init__(self, config_dir: Path | None = None) -> None:
        self._config_dir = config_dir or CONFIG_DIR
        self._settings_file = self._config_dir / "settings.json"
        self._ensure_dir()

    # ──────────────────────────────────────────────
    # المساعدات
    # ──────────────────────────────────────────────

    def _ensure_dir(self) -> None:
        """التأكد من وجود مجلد الإعدادات."""
        self._config_dir.mkdir(parents=True, exist_ok=True)

    def _settings_to_dict(self, settings: BookSettings) -> dict[str, Any]:
        """تحويل كائن الإعدادات إلى قاموس قابل للتسلسل."""
        from dataclasses import asdict
        return asdict(settings)

    def _dict_to_settings(self, data: dict[str, Any]) -> BookSettings:
        """تحويل قاموس إلى كائن إعدادات مع تجاهل القيم غير المعروفة."""
        valid_fields = BookSettings.__dataclass_fields__
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return BookSettings(**filtered)

    # ──────────────────────────────────────────────
    # العمليات الرئيسية
    # ──────────────────────────────────────────────

    def save(self, settings: BookSettings) -> None:
        """حفظ الإعدادات الحالية في ملف JSON.

        Args:
            settings: كائن الإعدادات المراد حفظه.
        """
        try:
            data = self._settings_to_dict(settings)
            with open(self._settings_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except (OSError, TypeError) as e:
            raise SettingsError(f"فشل في حفظ الإعدادات: {e}") from e

    def load(self) -> BookSettings:
        """استعادة الإعدادات من ملف JSON، أو إرجاع الإعدادات الافتراضية."""
        if not self._settings_file.exists():
            return BookSettings()
        try:
            with open(self._settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._dict_to_settings(data)
        except (json.JSONDecodeError, OSError, TypeError) as e:
            return BookSettings()

    def reset(self) -> BookSettings:
        """إعادة التعيين إلى القيم الافتراضية وحذف ملف الإعدادات."""
        if self._settings_file.exists():
            try:
                self._settings_file.unlink()
            except OSError:
                pass
        return BookSettings()

    @property
    def config_dir(self) -> Path:
        """مسار مجلد الإعدادات."""
        return self._config_dir


class SettingsError(Exception):
    """استثناء مخصص لأخطاء الإعدادات."""
    pass