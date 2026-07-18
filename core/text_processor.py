"""Text sanitization, normalization, and semantic paragraph chunking utilities."""

import re
from typing import Optional

from core.model import Lesson
from utils.logger import get_logger

logger = get_logger(__name__)


class TextProcessor:
    """Sanitizes text components and segments character blocks into separate paragraphs."""

    # Matching criteria targeting redundant blank lines (compress 3+ line breaks down to 2)
    MULTIPLE_BLANK_LINES = re.compile(r"\n{3,}")

    def __init__(self, first_line_indent_cm: float = 0.0) -> None:
        self._first_line_indent_cm = first_line_indent_cm

    # ──────────────────────────────────────────────
    # Core Text Sanitization
    # ──────────────────────────────────────────────

    def clean_text(self, text: str) -> str:
        """Sanitizes raw character sequences to remove systemic whitespace problems.

        - Compresses redundant consecutive line gaps
        - Normalizes trailing empty character bounds on a per-line basis
        - Standardizes platform-specific line break sequences

        Args:
            text: Raw input character text string.

        Returns:
            The normalized text string.
        """
        if not text:
            return ""

        # Remove byte order marks (BOM) if discovered
        if text.startswith("\ufeff"):
            text = text[1:]

        # Split text into lines and trim padding elements from individual strings
        lines = text.split("\n")
        cleaned_lines = [line.strip() for line in lines]

        # Re-assemble text content
        text = "\n".join(cleaned_lines)

        # Enforce maximum single empty line spacing breaks between distinct blocks
        text = self.MULTIPLE_BLANK_LINES.sub("\n\n", text)

        # Strip bounding edge properties from entire block segment values
        text = text.strip()

        return text

    # ──────────────────────────────────────────────
    # Semantic Paragraph Chunking
    # ──────────────────────────────────────────────

    def split_into_paragraphs(self, text: str) -> list[str]:
        """Segments text bodies into separate logical paragraph elements.

        A paragraph is defined as consecutive lines of text bound together, isolated
        from surrounding text segments by at least one explicit empty line.

        Args:
            text: Trimmed, sanitized text content.

        Returns:
            A list where individual entries represent standalone paragraph strings.
        """
        if not text:
            return []

        # Partition data segments across structural blank line delimiters
        raw_paragraphs = re.split(r"\n\s*\n", text)

        # Uniformly bind internal multi-line fragments into single continuous strings
        paragraphs = []
        for para in raw_paragraphs:
            unified = " ".join(para.split())
            if unified.strip():
                paragraphs.append(unified.strip())

        return paragraphs

    # ──────────────────────────────────────────────
    # Lesson Transformation Workflows
    # ──────────────────────────────────────────────

    def process_lesson(self, lesson: Lesson) -> Lesson:
        """Applies sanitization and structural parsing rules directly to an individual Lesson target.

        Args:
            lesson: Unprocessed raw Lesson structure.

        Returns:
            The same Lesson object updated with parsed content.
        """
        try:
            with open(lesson.file_path, "r", encoding="utf-8", errors="replace") as f:
                raw_text = f.read()
        except OSError:
            raw_text = ""

        cleaned = self.clean_text(raw_text)
        lesson.paragraphs = self.split_into_paragraphs(cleaned)

        logger.debug(
            "Processed lesson block '%s': Identified %d distinct paragraphs.",
            lesson.title,
            len(lesson.paragraphs),
        )
        return lesson

    def process_lessons(self, lessons: list[Lesson]) -> list[Lesson]:
        """Processes a sequence of input text data blocks in batch mode.

        Args:
            lessons: Collection array of unrefined Lesson entities.

        Returns:
            Updated sequence collection populated with normalized text segments.
        """
        processed = []
        for lesson in lessons:
            processed.append(self.process_lesson(lesson))
        return processed