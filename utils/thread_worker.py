"""خيط العمل المنفصل لعملية التحويل لمنع تجميد الواجهة."""

import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional

from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class WorkerResult:
    """نتيجة عملية التحويل."""
    success: bool = False
    output_path: str = ""
    error_message: str = ""
    stats: Optional[dict] = None


class ConversionWorker:
    """خيط عمل يقوم بعملية التحويل في الخلفية.

    يتواصل مع الواجهة عبر دوال الاستدعاء (callbacks).
    """

    def __init__(
        self,
        target: Callable,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        on_complete: Optional[Callable[[WorkerResult], None]] = None,
        on_log: Optional[Callable[[str], None]] = None,
    ) -> None:
        """تهيئة خيط العمل.

        Args:
            target: الدالة الرئيسية للتنفيذ.
            on_progress: دالة تُستدعى عند تحديث التقدم (حالي, إجمالي, اسم).
            on_complete: دالة تُستدعى عند انتهاء العمل مع النتيجة.
            on_log: دالة تُستدعى لإضافة رسالة للسجل.
        """
        self._target = target
        self._on_progress = on_progress
        self._on_complete = on_complete
        self._on_log = on_log

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._running = False

    @property
    def is_running(self) -> bool:
        """هل الخيط يعمل حاليًا؟"""
        return self._running

    @property
    def stop_check(self) -> Callable[[], bool]:
        """دالة يمكن تمريرها للباني للتحقق من طلب الإيقاف."""
        return self._stop_event.is_set

    def start(self, *args, **kwargs) -> None:
        """بدء خيط العمل.

        Args:
            *args: معاملات موضعية للدالة المستهدفة.
            **kwargs: معاملات مسماة للدالة المستهدفة.
        """
        if self._running:
            logger.warning("خيط العمل يعمل بالفعل")
            return

        self._stop_event.clear()
        self._running = True

        def _run():
            start_time = datetime.now()
            result = WorkerResult()
            try:
                output = self._target(*args, **kwargs)
                # إذا أرجعت الدالة مسار الملف
                if isinstance(output, str):
                    result.output_path = output
                    result.success = True
                elif isinstance(output, dict):
                    result.stats = output
                    result.success = output.get("success", True)
                    result.output_path = output.get("output_path", "")
                    if not result.success:
                        result.error_message = output.get("error", "")
                else:
                    result.success = True

                elapsed = (datetime.now() - start_time).total_seconds()
                self._safe_log(f"⏱ انتهت العملية في {elapsed:.1f} ثانية")

            except Exception as e:
                result.success = False
                result.error_message = str(e)
                logger.error("خطأ في خيط العمل: %s", e, exc_info=True)
                self._safe_log(f"❌ خطأ: {e}")

            finally:
                self._running = False
                if self._on_complete:
                    self._on_complete(result)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        logger.info("تم بدء خيط العمل")

    def stop(self) -> None:
        """طلب إيقاف العملية."""
        if self._running:
            self._stop_event.set()
            self._safe_log("⏳ جارٍ إيقاف العملية...")
            logger.info("تم طلب إيقاف خيط العمل")

    def _safe_log(self, message: str) -> None:
        """إرسال رسالة للسجل بأمان."""
        if self._on_log:
            try:
                self._on_log(message)
            except Exception:
                pass

    def _safe_progress(self, current: int, total: int, name: str) -> None:
        """تحديث التقدم بأمان."""
        if self._on_progress:
            try:
                self._on_progress(current, total, name)
            except Exception:
                pass