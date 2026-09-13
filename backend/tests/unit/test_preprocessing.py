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


def test_normalize_strips_surrounding_whitespace() -> None:
    assert normalize_text("\n  hello  \t") == "hello"


def test_normalize_collapses_multiple_spaces() -> None:
    assert normalize_text("a    b") == "a b"


def test_normalize_preserves_punctuation() -> None:
    assert normalize_text("Wait... what?!") == "Wait... what?!"


def test_count_words_empty_and_whitespace() -> None:
    assert count_words("") == 0
    assert count_words("   \n\t ") == 0


def test_count_words_with_punctuation() -> None:
    assert count_words("hello, world!") == 2


def test_split_sentences_question_and_exclamation() -> None:
    parts = split_sentences("Are you sure? Yes I am!")
    assert parts == ["Are you sure?", "Yes I am!"]


def test_split_sentences_strips_each_part() -> None:
    parts = split_sentences("  First.   Second.  ")
    assert parts == ["First.", "Second."]


def test_split_sentences_lowercase_after_period_not_split() -> None:
    # A period followed by a lowercase word is treated as one sentence.
    parts = split_sentences("see e.g. this")
    assert parts == ["see e.g. this"]


def test_split_sentences_quote_after_period_splits() -> None:
    parts = split_sentences('He left. "Goodbye" was all he said.')
    assert len(parts) == 2


def test_split_sentences_multiple_punctuation() -> None:
    parts = split_sentences("What?! Really?!")
    assert len(parts) >= 1
    assert all(part.strip() for part in parts)

