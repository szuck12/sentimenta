# backend/app/core/errors.py
# Application error types and the standardized error envelope used
# by every non-2xx API response.

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for errors that map cleanly onto an HTTP response.

    Attributes:
        status_code: HTTP status code for the response.
        code: Stable machine-readable identifier (e.g.
            "text_too_long").
        message: Human-readable explanation safe to show users.
    """

    def __init__(
        self, status_code: int, code: str, message: str
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(message)


class EmptyTextError(AppError):
    """Raised when submitted text is empty or whitespace-only."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="empty_text",
            message="Please provide some text to analyze.",
        )


class TextTooLongError(AppError):
    """Raised when submitted text exceeds the configured limit."""

    def __init__(self, max_chars: int, actual: int) -> None:
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="text_too_long",
            message=(
                f"Text is {actual} characters; the limit is "
                f"{max_chars}."
            ),
        )


class ModelUnavailableError(AppError):
    """Raised when analysis is requested before the model is ready."""

    def __init__(self) -> None:
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="model_unavailable",
            message=(
                "The emotion model is still loading. Please retry "
                "in a moment."
            ),
        )


async def app_error_handler(
    _request: Request, exc: AppError
) -> JSONResponse:
    """Render an AppError as the standard error envelope."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {"code": exc.code, "message": exc.message}
        },
    )


async def validation_error_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Render request-validation failures in the standard envelope."""
    first = exc.errors()[0] if exc.errors() else {}
    loc = ".".join(str(part) for part in first.get("loc", [])[-1:])
    message = first.get("msg", "Invalid request.")
    if loc:
        message = f"{loc}: {message}"
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "invalid_request",
                "message": message,
            }
        },
    )


async def unhandled_error_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    """Convert unexpected failures into a safe 500 envelope.

    The original exception is re-raised in server logs via uvicorn's
    error logger so developers retain full detail while clients only
    ever see the generic message.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "internal_error",
                "message": (
                    "Something went wrong while analysing your "
                    "text. Please try again."
                ),
            }
        },
    )
