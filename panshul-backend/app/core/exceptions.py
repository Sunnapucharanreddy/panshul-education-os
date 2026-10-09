"""Domain exceptions. API layer maps these to HTTP responses in one place."""


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str = "Internal error"):
        self.message = message
        super().__init__(message)


class AuthError(AppError):
    status_code = 401
    code = "auth_error"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class ValidationFailed(AppError):
    status_code = 422
    code = "validation_failed"


class RateLimited(AppError):
    status_code = 429
    code = "rate_limited"


class ProviderError(AppError):
    """An upstream AI provider (LLM/STT/TTS) failed."""
    status_code = 502
    code = "provider_error"
