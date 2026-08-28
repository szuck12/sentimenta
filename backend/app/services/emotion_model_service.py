# backend/app/services/emotion_model_service.py
# Singleton wrapper around the Hugging Face GoEmotions model. Loads
# the tokenizer and model exactly once and exposes batch inference.

import logging
import threading
from dataclasses import dataclass

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from transformers.tokenization_utils_base import BatchEncoding

from ..core.config import Settings
from ..core.emotions import Emotion

logger = logging.getLogger(__name__)


@dataclass
class OffsetPrediction:
    """Inference result that retains token-level bookkeeping.

    Attributes:
        scores: All 28 sigmoid probabilities for the text.
        encoding: Tokenizer output (input_ids, attention_mask,
            offset_mapping) kept on CPU for attribution reuse.
        truncated: Whether the input exceeded the token budget.
    """

    scores: dict[Emotion, float]
    encoding: BatchEncoding
    truncated: bool

# Inference token budget. The upstream model was trained on short
# Reddit comments; longer inputs are truncated (and flagged in the
# response metadata) rather than rejected.
MAX_INPUT_TOKENS = 256


class EmotionModelService:
    """Loads and serves the multi-label GoEmotions classifier.

    The service owns all PyTorch/Hugging Face state so the rest of
    the application never touches the model directly. One instance is
    created at startup and reused for every request; a lock serialises
    forward passes when requests arrive concurrently.

    Attributes:
        settings: Application settings (model id, device, etc.).
        tokenizer: Loaded HF tokenizer (None until :meth:`load`).
        model: Loaded HF sequence-classification model in eval mode.
        device: Torch device the model resides on.
        max_input_tokens: Token budget applied before inference.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.tokenizer = None
        self.model = None
        self.max_input_tokens = MAX_INPUT_TOKENS
        self.device = torch.device(
            settings.device
            if settings.device
            else ("mps" if torch.backends.mps.is_available() else "cpu")
        )
        self._lock = threading.Lock()

    @property
    def is_loaded(self) -> bool:
        """Whether the model weights are loaded and ready."""
        return self.model is not None and self.tokenizer is not None

    def load(self) -> None:
        """Download (once, then cache) and prepare the model.

        Sets evaluation mode, moves tensors to the selected device,
        and validates that the label order matches Sentimenta's
        taxonomy.

        Raises:
            RuntimeError: If loading fails; the original exception is
                chained so operators see the root cause.
        """
        try:
            logger.info("Loading model %s ...", self.settings.model_id)
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.settings.model_id
            )
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.settings.model_id
            )
            assert self.model is not None
            self.model.to(self.device)
            self.model.eval()
            expected = {e.value for e in Emotion}
            assert self.model.config is not None
            actual = set(self.model.config.id2label.values())
            if actual != expected:
                raise RuntimeError(
                    f"Model labels {sorted(actual)} do not match the "
                    f"GoEmotions taxonomy {sorted(expected)}"
                )
            logger.info("Model ready on %s", self.device)
        except Exception as exc:
            self.model = None
            self.tokenizer = None
            raise RuntimeError(
                f"Failed to load emotion model "
                f"'{self.settings.model_id}': {exc}"
            ) from exc

    def _require_loaded(self) -> None:
        """Raise if :meth:`load` has not completed successfully."""
        if not self.is_loaded:
            raise RuntimeError(
                "Emotion model is not loaded; call load() first."
            )

    def _encode(
        self, texts: list[str], with_offsets: bool
    ) -> BatchEncoding:
        """Tokenise inputs on CPU, optionally keeping offsets."""
        assert self.tokenizer is not None
        return self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=self.max_input_tokens,
            return_tensors="pt",
            return_offsets_mapping=with_offsets,
        )

    _MODEL_INPUT_KEYS = ("input_ids", "attention_mask")

    @staticmethod
    def _model_inputs(
        encoded: BatchEncoding, device: torch.device | None = None
    ) -> dict[str, torch.Tensor]:
        """Keep only the tensors the model accepts, optionally moved.

        Args:
            encoded: Tokenizer output that may include extra entries
                such as ``offset_mapping``.
            device: When provided, tensors are moved to this device.

        Returns:
            A dict containing ``input_ids`` and ``attention_mask``.
        """
        selected: dict[str, torch.Tensor] = {}
        for key in EmotionModelService._MODEL_INPUT_KEYS:
            if key in encoded:
                tensor = encoded[key]
                if device is not None:
                    tensor = tensor.to(device)
                selected[key] = tensor
        return selected

    def _forward(
        self,
        encoded: dict[str, torch.Tensor],
        needs_grad: bool = False,
    ) -> torch.Tensor:
        """Run one batched forward pass and return sigmoid outputs.

        Args:
            encoded: Tokenizer output already moved to the device.
            needs_grad: When True gradients stay enabled so
                gradient-based attribution methods can differentiate
                through the pass.

        Returns:
            A (batch, 28) tensor of sigmoid probabilities.

        Raises:
            RuntimeError: If the forward pass fails.
        """
        try:
            ctx = (
                torch.no_grad() if not needs_grad else torch.enable_grad()
            )
            with ctx:
                assert self.model is not None
                logits = self.model(**encoded).logits
            return torch.sigmoid(logits)
        except Exception as exc:
            raise RuntimeError(
                f"Emotion inference failed: {exc}"
            ) from exc

    def _to_scores(self, probs_row: torch.Tensor) -> dict[Emotion, float]:
        """Convert one probability row into the label mapping."""
        assert self.model is not None
        id2label: dict[int, str] = self.model.config.id2label
        return {
            Emotion(id2label[i]): float(p)
            for i, p in enumerate(probs_row.tolist())
        }

    def predict(self, texts: list[str]) -> list[dict[Emotion, float]]:
        """Run multi-label inference and return per-text probabilities.

        Args:
            texts: Non-empty input strings.

        Returns:
            One ``{emotion: probability}`` mapping (all 28 labels,
            sigmoid-activated) per input text, in input order.

        Raises:
            RuntimeError: If the model is not loaded or inference
                fails.
        """
        self._require_loaded()
        if not texts:
            return []
        with self._lock:
            encoded = self._encode(texts, with_offsets=False)
            device_inputs = self._model_inputs(encoded, self.device)
            probs = self._forward(device_inputs).cpu()
        return [self._to_scores(row) for row in probs]

    def predict_with_offsets(self, text: str) -> OffsetPrediction:
        """Infer scores for one text while retaining token metadata.

        Used by the explanation service, which needs subtoken offset
        mappings to map attribution values back to words.

        Args:
            text: Non-empty input string.

        Returns:
            An OffsetPrediction with scores, the CPU-side encoding
            (including ``offset_mapping``), and a truncation flag.
        """
        self._require_loaded()
        with self._lock:
            encoded = self._encode([text], with_offsets=True)
            num_tokens = int(encoded["input_ids"].shape[1])
            truncated = num_tokens >= self.max_input_tokens
            device_inputs = self._model_inputs(encoded, self.device)
            probs = self._forward(device_inputs).cpu()
        return OffsetPrediction(
            scores=self._to_scores(probs[0]),
            encoding=encoded,
            truncated=truncated,
        )

    def exceeds_token_budget(self, text: str) -> bool:
        """Check tokenisation length without running the model.

        Args:
            text: Input text.

        Returns:
            True when ``text`` would be truncated at
            ``max_input_tokens`` during inference.
        """
        self._require_loaded()
        assert self.tokenizer is not None
        ids = self.tokenizer(text, truncation=False)["input_ids"]
        return len(ids) > self.max_input_tokens

    def forward_locked(
        self, device_inputs: dict[str, torch.Tensor]
    ) -> torch.Tensor:
        """Run a gradient-enabled forward pass under the model lock.

        Exposed for the explanation service's attribution methods,
        which must serialise their many small forward passes with
        ordinary inference.

        Args:
            device_inputs: Tokenizer tensors already on the device.

        Returns:
            A (batch, 28) tensor of sigmoid probabilities.
        """
        self._require_loaded()
        with self._lock:
            return self._forward(device_inputs, needs_grad=True)
