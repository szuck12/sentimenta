# backend/app/services/preprocessing.py
# Text normalisation, counting, and sentence segmentation used before
# (and after) model inference.

import re

# A pragmatic sentence splitter: sentence-ending punctuation followed
# by whitespace and a capital/quote/digit starts a new sentence.
# Newlines always separate sentences. Deliberately simple — this is a
# presentation aid, not a linguistic parser.
_SENTENCE_BOUNDARY = re.compile(
    r"(?<=[.!?…])\s+(?=[\"'(\[A-Z0-9])"
)
_WHITESPACE_RUN = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Collapse whitespace runs while preserving content.

    Args:
        text: Raw user input.

    Returns:
        Text with newlines/tabs collapsed to single spaces and outer
        whitespace stripped. Emojis and Unicode are preserved.
    """
    return _WHITESPACE_RUN.sub(" ", text).strip()


def count_words(text: str) -> int:
    """Count whitespace-separated words in ``text``."""
    return len(text.split())


def split_sentences(text: str) -> list[str]:
    """Split input into non-empty sentences for per-sentence analysis.

    Splits on sentence-ending punctuation followed by a new sentence
    start, as well as on any newline. Whitespace runs inside each
    sentence are collapsed.

    Args:
        text: Raw user input.

    Returns:
        Sentences in original order; empty list when nothing usable
        remains after splitting.
    """
    candidates: list[str] = []
    for paragraph in text.splitlines():
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        parts = _SENTENCE_BOUNDARY.split(paragraph)
        candidates.extend(part.strip() for part in parts)
    return [c for c in candidates if c]
