"""Isolated worker thread manager to run conversions without freezing the main UI."""

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
    """Data object encapsulating the conversion final output status."""
    success: bool = False
    output_path: str = ""
    error_message: str = ""
    stats: Optional[dict] = None


class ConversionWorker:
    """Background execution engine running long tasks concurrently from the main UI thread.

    Communicates lifecycle changes back to the UI asynchronously via thread-safe callbacks.
    """

    def __init__(
        self,
        target: Callable,
        on_progress: Optional[Callable[[int, int, str], None]] = None,
        on_complete: Optional[Callable[[WorkerResult], None]] = None,
        on_log: Optional[Callable[[str], None]] = None,
    ) -> None:
        """Initializes the background worker instance.

        Args:
            target: The primary task function to be invoked inside the thread.
            on_progress: Callback triggered when progress updates (current, total, filename).
            on_complete: Callback triggered upon operational termination, receiving a WorkerResult.
            on_log: Callback triggered to pipe internal execution tracking strings to the UI log view.
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
        """Checks if the thread is currently executing."""
        return self._running

    @property
    def stop_check(self) -> Callable[[], bool]:
        """Provides a check function callable by the execution target to detect cancellation requests."""
        return self._stop_event.is_set

    def start(self, *args, **kwargs) -> None:
        """Spawns and activates the worker thread safely.

        Args:
            *args: Positional arguments passed to the target function.
            **kwargs: Keyword arguments passed to the target function.
        """
        if self._running:
            logger.warning("Worker thread is already active and running.")
            return

        self._stop_event.clear()
        self._running = True

        def _run():
            start_time = datetime.now()
            result = WorkerResult()
            try:
                output = self._target(*args, **kwargs)
                
                # Check the target function's output format
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
                self._safe_log(f"⏱ Operation finished in {elapsed:.1f} seconds.")

            except Exception as e:
                result.success = False
                result.error_message = str(e)
                logger.error("Error occurred inside worker thread: %s", e, exc_info=True)
                self._safe_log(f"❌ Error: {e}")

            finally:
                self._running = False
                if self._on_complete:
                    self._on_complete(result)

        # Configure as a daemon thread so it terminates immediately if the app closes
        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()
        logger.info("Worker thread spawned successfully.")

    def stop(self) -> None:
        """Sends a soft cancellation token signal to halt operations gracefully."""
        if self._running:
            self._stop_event.set()
            self._safe_log("⏳ Stopping process gracefully...")
            logger.info("Thread termination request received.")

    def _safe_log(self, message: str) -> None:
        """Safely dispatches text string to log tracking callback ignoring errors."""
        if self._on_log:
            try:
                self._on_log(message)
            except Exception:
                pass

    def _safe_progress(self, current: int, total: int, name: str) -> None:
        """Safely dispatches standard metric progress updates tracking step progression."""
        if self._on_progress:
            try:
                self._on_progress(current, total, name)
            except Exception:
                pass