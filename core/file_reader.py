"""Text file scanner, encoding recognizer, and natural sequence engine."""

import os
import re
from pathlib import Path
from typing import Optional

import chardet

from core.model import Lesson
from utils.logger import get_logger

logger = get_logger(__name__)


class FileReader:
    """Discovers, evaluates, and parses local source text assets in correct logical order."""

    # Sequential backup character sets to verify if standard automation mechanisms fail
    FALLBACK_ENCODINGS = ["utf-8-sig", "utf-8", "windows-1256", "windows-1252", "iso-8859-6"]

    def __init__(self) -> None:
        self._detected_encodings: dict[str, str] = {}

    # ──────────────────────────────────────────────
    # Encoding Determination
    # ──────────────────────────────────────────────

    def detect_encoding(self, file_path: str | Path) -> str:
        """Evaluates character set configurations automatically using chardet framework profiles.

        Args:
            file_path: System target asset destination reference.

        Returns:
            String description matching standard encoding labels (e.g., 'utf-8').
        """
        file_path = Path(file_path)
        if file_path.name in self._detected_encodings:
            return self._detected_encodings[file_path.name]

        try:
            raw = file_path.read_bytes()
            # Sample initial 64 KB block segments to optimize execution tracking performance
            sample = raw[:65536]
            if not sample.strip():
                self._detected_encodings[file_path.name] = "utf-8"
                return "utf-8"

            result = chardet.detect(sample)
            encoding = result.get("encoding", "utf-8") or "utf-8"
            confidence = result.get("confidence", 0.0)

            # Revert to backup strategies if clarity parameters drop below safe thresholds
            if confidence < 0.6:
                encoding = self._try_fallback_encodings(raw) or encoding

            # Standardize string formatting descriptors
            encoding = encoding.lower().replace("-", "")
            if encoding == "utf8sig":
                encoding = "utf-8-sig"
            elif encoding == "utf8":
                encoding = "utf-8"
            elif encoding == "ascii":
                encoding = "utf-8"

            self._detected_encodings[file_path.name] = encoding
            logger.debug("Detected encoding for %s: %s (confidence: %.1f%%)", file_path.name, encoding, confidence * 100)
            return encoding

        except OSError as e:
            logger.warning("Failed to access properties of %s for analysis: %s", file_path.name, e)
            return "utf-8"

    def _try_fallback_encodings(self, raw: bytes) -> Optional[str]:
        """Iterates through alternative fallbacks against text buffers to resolve mapping errors.

        Args:
            raw: Underlying text byte sequence.

        Returns:
            The label descriptive identity string of a viable configuration, otherwise None.
        """
        for enc in self.FALLBACK_ENCODINGS:
            try:
                raw.decode(enc)
                return enc
            except (UnicodeDecodeError, LookupError):
                continue
        return None

    # ──────────────────────────────────────────────
    # Content Reading
    # ──────────────────────────────────────────────

    def read_file(self, file_path: str | Path) -> str:
        """Retrieves raw asset content elements safely using appropriate encoding schemas.

        Args:
            file_path: Target workspace path.

        Returns:
            Decoded text contents from the source file.

        Raises:
            FileNotFoundError: If the target file does not exist.
            OSError: If reading fails across all attempted encoding options.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Target location missing: {file_path}")

        encoding = self.detect_encoding(file_path)

        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            pass

        # Engage historical fallback strategies if exceptions arise during rendering
        raw = file_path.read_bytes()
        for enc in self.FALLBACK_ENCODINGS:
            try:
                return raw.decode(enc)
            except (UnicodeDecodeError, LookupError):
                continue

        # Terminal safe fallback recovery strategy: Drop/substitute problematic characters
        logger.warning("Unable to accurately decode %s. Substituting invalid tokens.", file_path.name)
        return raw.decode("utf-8", errors="replace")

    # ──────────────────────────────────────────────
    # Natural Sequencing Mechanics
    # ──────────────────────────────────────────────

    def get_txt_files(self, folder_path: str | Path) -> list[Path]:
        """Indexes matching folder target files arranged using standard human natural numeric sequencing order.

        Natural string processing guarantees indices flow sequentially (e.g., 001, 002, 010) rather
        than alphabetical parsing groupings where 010 precedes 002.

        Args:
            folder_path: Target directory path to query.

        Returns:
            A list containing organized sorted path entities.
        """
        folder_path = Path(folder_path)
        if not folder_path.is_dir():
            raise NotADirectoryError(f"Provided path parameter is not a valid folder entity: {folder_path}")

        txt_files = sorted(
            [f for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() == ".txt"],
            key=self._natural_sort_key,
        )
        logger.info("Indexed %d text documents within: %s", len(txt_files), folder_path.name)
        return txt_files

    @staticmethod
    def _natural_sort_key(path: Path) -> list:
        """Extracts text components and numeric sequences cleanly to generate keys for natural sorting.

        Example matching workflow: 'lesson_002.txt' < 'lesson_010.txt' < 'lesson_100.txt'

        Args:
            path: Target file path entity.

        Returns:
            Deconstructed list mapping elements into text components and integers.
        """
        name = path.stem
        return [int(part) if part.isdigit() else part.lower()
                for part in re.split(r"(\d+)", name)]

    # ──────────────────────────────────────────────
    # Batch Processing Entry Points
    # ──────────────────────────────────────────────

    def read_lessons(self, folder_path: str | Path) -> list[Lesson]:
        """Converts directory file references into fully instantiated Lesson model structures.

        Args:
            folder_path: Source workspace path.

        Returns:
            An organized array containing populated Lesson data instances.
        """
        files = self.get_txt_files(folder_path)
        lessons: list[Lesson] = []

        for index, file_path in enumerate(files):
            try:
                content = self.read_file(file_path)
                title = file_path.stem
                lessons.append(Lesson(
                    title=title,
                    paragraphs=[],  # Populated downstream inside TextProcessor
                    file_path=str(file_path),
                    file_index=index,
                ))
            except Exception as e:
                logger.error("Failed to parse and read matching text properties for %s: %s", file_path.name, e)

        return lessons