# backend/tests/unit/test_emotions.py
# Taxonomy integrity: label count, metadata completeness, and the
# group mapping used by the emotional-profile visualization.

from app.core.emotions import (
    ALL_EMOTIONS,
    DESCRIPTIONS,
    EMOJIS,
    GROUP_LABELS,
    GROUP_MEMBERS,
    Emotion,
    EmotionGroup,
    group_of,
)


def test_exactly_28_unique_emotions() -> None:
    assert len(Emotion) == 28
    assert len({e.value for e in Emotion}) == 28


def test_every_emotion_has_emoji_and_description() -> None:
    for emotion in Emotion:
        assert EMOJIS[emotion].strip()
        assert DESCRIPTIONS[emotion].strip()


def test_groups_cover_every_emotion_exactly_once() -> None:
    members = [e for group in GROUP_MEMBERS.values() for e in group]
    assert len(members) == 28
    assert sorted(members, key=lambda e: e.value) == sorted(
        Emotion, key=lambda e: e.value
    )


def test_group_of_matches_membership() -> None:
    for emotion in Emotion:
        assert emotion in GROUP_MEMBERS[group_of(emotion)]


def test_every_group_has_a_display_label() -> None:
    for group in EmotionGroup:
        assert GROUP_LABELS[group].strip()


def test_neutral_is_its_own_group() -> None:
    assert GROUP_MEMBERS[EmotionGroup.NEUTRAL] == (Emotion.NEUTRAL,)


def test_all_emotions_matches_enum_order() -> None:
    assert ALL_EMOTIONS == list(Emotion)
    assert ALL_EMOTIONS[0] is Emotion.ADMIRATION
