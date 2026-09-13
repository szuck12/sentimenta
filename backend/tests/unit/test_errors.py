# backend/tests/unit/test_errors.py
# The standardized error envelope produced by each exception handler.

import json

from fastapi.exceptions import RequestValidationError

from app.core.errors import (
    AppError,
    EmptyTextError,
    ModelUnavailableError,
    TextTooLongError,
    app_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)


async def _body(response) -> dict:  # type: ignore[no-untyped-def]
    return json.loads(response.body)


async def test_app_error_renders_envelope() -> None:
    response = await app_error_handler(None, EmptyTextError())  # type: ignore[arg-type]
    assert response.status_code == 422
    body = await _body(response)
    assert body["error"]["code"] == "empty_text"
    assert body["error"]["message"]


async def test_text_too_long_reports_counts() -> None:
    response = await app_error_handler(  # type: ignore[arg-type]
        None, TextTooLongError(max_chars=2000, actual=2500)
    )
    assert response.status_code == 422
    body = await _body(response)
    assert body["error"]["code"] == "text_too_long"
    assert "2500" in body["error"]["message"]
    assert "2000" in body["error"]["message"]


async def test_model_unavailable_is_503() -> None:
    response = await app_error_handler(None, ModelUnavailableError())  # type: ignore[arg-type]
    assert response.status_code == 503
    body = await _body(response)
    assert body["error"]["code"] == "model_unavailable"


async def test_validation_error_summarized() -> None:
    exc = RequestValidationError(
        [
            {
                "loc": ("body", "text"),
                "msg": "Field required",
                "type": "missing",
            }
        ]
    )
    response = await validation_error_handler(None, exc)  # type: ignore[arg-type]
    assert response.status_code == 422
    body = await _body(response)
    assert body["error"]["code"] == "invalid_request"
    assert "text" in body["error"]["message"]


async def test_unhandled_error_is_sanitized() -> None:
    secret = "internal-detail-should-not-leak"
    response = await unhandled_error_handler(  # type: ignore[arg-type]
        None, RuntimeError(secret)
    )
    assert response.status_code == 500
    body = await _body(response)
    assert body["error"]["code"] == "internal_error"
    assert secret not in response.body.decode()


def test_app_error_stores_attributes() -> None:
    err = AppError(status_code=418, code="teapot", message="short and stout")
    assert err.status_code == 418
    assert err.code == "teapot"
    assert str(err) == "short and stout"
