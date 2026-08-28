# backend/tests/unit/test_preprocessing.py
# Tests for text normalization, word counting, and sentence splitting.

from app.services.preprocessing import (
    count_words,
    normalize_text,
    split_sentences,
)


def test_normalize_collapses_whitespace() -> None:
    assert normalize_text("  a\nb\tc  ") == "a b c"


def test_normalize_preserves_emojis() -> None:
    assert "😂😂😂" in normalize_text("😂😂😂")


def test_normalize_empty_string() -> None:
    assert normalize_text("") == ""


def test_count_words() -> None:
    assert count_words("hello world foo") == 3


def test_count_single_word() -> None:
    assert count_words("wow") == 1


def test_split_sentences_simple() -> None:
    text = "I was nervous. I felt relieved!"
    parts = split_sentences(text)
    assert len(parts) == 2
    assert parts[0] == "I was nervous."
    assert parts[1] == "I felt relieved!"


def test_split_sentences_newline_separation() -> None:
    text = "line one\nline two"
    parts = split_sentences(text)
    assert len(parts) == 2


def test_split_sentences_single_sentence() -> None:
    parts = split_sentences("no breaks here")
    assert parts == ["no breaks here"]


def test_split_sentences_blank_paragraphs_ignored() -> None:
    text = "hello\n\n\nworld"
    parts = split_sentences(text)
    assert parts == ["hello", "world"]


def test_split_sentences_long_text() -> None:
    sentences = [f"Word number {i}." for i in range(10)]
    text = "\n".join(sentences)
    parts = split_sentences(text)
    assert len(parts) == 10


def test_split_sentences_unicode_punctuation() -> None:
    parts = split_sentences("Wait\u2026 really?")
    assert len(parts) >= 1


def test_split_sentences_empty() -> None:
    assert split_sentences("") == []
    assert split_sentences("   ") == []
