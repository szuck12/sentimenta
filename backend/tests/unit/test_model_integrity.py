# backend/tests/unit/test_model_integrity.py
# Unit test for the model-file hashing helper (no PyTorch import).

import hashlib

from app.services.emotion_model_service import _sha256_file


def test_sha256_file(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "weights.bin"
    path.write_bytes(b"hello world")
    expected = hashlib.sha256(b"hello world").hexdigest()
    assert _sha256_file(str(path)) == expected


def test_sha256_file_empty(tmp_path) -> None:  # type: ignore[no-untyped-def]
    path = tmp_path / "empty.bin"
    path.write_bytes(b"")
    assert _sha256_file(str(path)) == hashlib.sha256(b"").hexdigest()
