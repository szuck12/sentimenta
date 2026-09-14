# backend/tests/model/test_emotion_model.py
# Integration tests exercising real Hugging Face inference. These
# require the model to be downloaded; skip when weights are absent.

import math

import pytest

from app.core.emotions import Emotion
from app.core.config import Settings
from app.services.emotion_model_service import EmotionModelService

pytestmark = pytest.mark.model


@pytest.fixture(scope="module")
def loaded_service() -> EmotionModelService:
    """Load the model once for all tests in this file."""
    settings = Settings(model_id="SamLowe/roberta-base-go_emotions")
    svc = EmotionModelService(settings)
    svc.load()
    return svc


def _all_probabilities_in_range(
    scores: dict[Emotion, float],
) -> None:
    """Assert every probability is a finite float in [0, 1]."""
    for label, score in scores.items():
        assert 0.0 <= score <= 1.0, f"{label} score {score} out of range"
        assert not math.isinf(score) and not math.isnan(score), (
            f"{label} score is not finite"
        )


class TestModelInference:
    """Smoke tests that the model produces valid outputs."""

    def test_excitement_text(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict(["I can't wait!"])[0]
        _all_probabilities_in_range(scores)
        assert scores[Emotion.EXCITEMENT] > scores[Emotion.SADNESS]

    def test_sadness_text(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict(["I feel so alone."])[0]
        _all_probabilities_in_range(scores)
        assert scores[Emotion.SADNESS] > scores[Emotion.JOY]

    def test_neutral_text(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict(
            ["The temperature is 72 degrees today."]
        )[0]
        _all_probabilities_in_range(scores)
        assert scores[Emotion.NEUTRAL] > 0.15

    def test_multi_label_output(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict(
            ["I'm nervous but excited!"]
        )[0]
        _all_probabilities_in_range(scores)
        assert scores[Emotion.NERVOUSNESS] > 0.10
        assert scores[Emotion.EXCITEMENT] > 0.10

    def test_all_28_labels_returned(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict(["hello"])[0]
        assert set(scores.keys()) == {e for e in Emotion}

    def test_batch_inference(self, loaded_service: EmotionModelService) -> None:
        texts = ["I am angry.", "So happy!", "I am confused."]
        results = loaded_service.predict(texts)
        assert len(results) == 3
        assert results[0][Emotion.ANGER] > results[0][Emotion.JOY]
        assert results[1][Emotion.JOY] > results[1][Emotion.ANGER]

    def test_empty_batch(self, loaded_service: EmotionModelService) -> None:
        assert loaded_service.predict([]) == []

    def test_punctuation_heavy(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict(["WHAT?!?!?!?"])[0]
        _all_probabilities_in_range(scores)

    def test_emoji_input(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict(["😂😂😂"])[0]
        _all_probabilities_in_range(scores)

    def test_unicode_text(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict(["Je suis très heureux 😊"])[0]
        _all_probabilities_in_range(scores)

    def test_long_text_truncation(self, loaded_service: EmotionModelService) -> None:
        long_text = "word " * 500  # ~2500 chars, exceeds 256 tokens
        scores = loaded_service.predict([long_text])[0]
        _all_probabilities_in_range(scores)
        assert loaded_service.exceeds_token_budget(long_text) is True

    def test_short_text_no_truncation(self, loaded_service: EmotionModelService) -> None:
        assert loaded_service.exceeds_token_budget("hello") is False

    def test_empty_string(self, loaded_service: EmotionModelService) -> None:
        scores = loaded_service.predict([""])[0]
        _all_probabilities_in_range(scores)


class TestSentenceAnalysis:
    """Verify sentence-level batch predictions."""

    def test_two_sentences(self, loaded_service: EmotionModelService) -> None:
        texts = [
            "I was nervous.",
            "Then I felt relieved!",
        ]
        results = loaded_service.predict(texts)
        assert len(results) == 2
        assert results[0][Emotion.NERVOUSNESS] > results[0][Emotion.JOY]
        assert results[1][Emotion.RELIEF] > results[1][Emotion.NERVOUSNESS]


class TestOffsetPredictions:
    """predict_with_offsets retains token metadata for attribution."""

    def test_returns_scores_encoding_and_flag(
        self, loaded_service: EmotionModelService
    ) -> None:
        prediction = loaded_service.predict_with_offsets("I love this!")
        assert set(prediction.scores.keys()) == {e for e in Emotion}
        assert "input_ids" in prediction.encoding
        assert "attention_mask" in prediction.encoding
        assert "offset_mapping" in prediction.encoding
        assert prediction.truncated is False

    def test_flags_truncation_for_long_text(
        self, loaded_service: EmotionModelService
    ) -> None:
        prediction = loaded_service.predict_with_offsets("word " * 500)
        assert prediction.truncated is True

    def test_forward_locked_returns_28_probabilities(
        self, loaded_service: EmotionModelService
    ) -> None:
        prediction = loaded_service.predict_with_offsets("hello")
        device_inputs = loaded_service._model_inputs(
            prediction.encoding, loaded_service.device
        )
        probs = loaded_service.forward_locked(device_inputs)
        assert probs.shape == (1, 28)
        detached = probs.detach()
        assert float(detached.min()) >= 0.0
        assert float(detached.max()) <= 1.0


class TestModelServiceState:
    """State and taxonomy invariants of the loaded service."""

    def test_is_loaded_after_load(
        self, loaded_service: EmotionModelService
    ) -> None:
        assert loaded_service.is_loaded is True

    def test_id2label_matches_emotion_taxonomy(
        self, loaded_service: EmotionModelService
    ) -> None:
        assert loaded_service.model is not None
        labels = set(loaded_service.model.config.id2label.values())
        assert labels == {e.value for e in Emotion}

    def test_predictions_are_deterministic(
        self, loaded_service: EmotionModelService
    ) -> None:
        first = loaded_service.predict(["I am so happy!"])[0]
        second = loaded_service.predict(["I am so happy!"])[0]
        assert first == second

    def test_batch_order_is_preserved(
        self, loaded_service: EmotionModelService
    ) -> None:
        def top_label(scores: dict[Emotion, float]) -> Emotion:
            return max(scores, key=scores.get)

        batch = loaded_service.predict(["I am angry.", "So happy!"])
        angry = loaded_service.predict(["I am angry."])[0]
        happy = loaded_service.predict(["So happy!"])[0]
        assert top_label(batch[0]) == top_label(angry)
        assert top_label(batch[1]) == top_label(happy)

    def test_token_budget_matches_tokenizer(
        self, loaded_service: EmotionModelService
    ) -> None:
        assert loaded_service.tokenizer is not None
        text = "a " * 200
        ids = loaded_service.tokenizer(text, truncation=False)["input_ids"]
        expected = len(ids) > loaded_service.max_input_tokens
        assert loaded_service.exceeds_token_budget(text) == expected

    def test_multi_label_scores_need_not_sum_to_one(
        self, loaded_service: EmotionModelService
    ) -> None:
        scores = loaded_service.predict(["I'm nervous but excited!"])[0]
        assert 0.0 <= sum(scores.values()) <= len(Emotion)


class TestIntegrityVerification:
    """The pinned SHA-256 is enforced when loading weights."""

    def test_wrong_hash_raises(self) -> None:
        settings = Settings(
            model_id="SamLowe/roberta-base-go_emotions",
            model_revision="d75048347613a25d77de8cf6412eaae9fa7b26be",
            model_sha256="0" * 64,
        )
        service = EmotionModelService(settings)
        with pytest.raises(RuntimeError):
            service.load()

    def test_correct_hash_loads(self) -> None:
        settings = Settings(
            model_id="SamLowe/roberta-base-go_emotions",
            model_revision="d75048347613a25d77de8cf6412eaae9fa7b26be",
        )
        service = EmotionModelService(settings)
        service.load()
        assert service.is_loaded is True
