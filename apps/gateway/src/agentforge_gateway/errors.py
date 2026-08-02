from __future__ import annotations


def error_response(message: str, error_type: str) -> dict[str, object]:
    return {
        "error": {
            "message": message,
            "type": error_type,
        }
    }


def not_found_response() -> dict[str, object]:
    return error_response("not found", "not_found")


def invalid_json_response() -> dict[str, object]:
    return error_response("invalid JSON body", "bad_request")


def internal_error_response() -> dict[str, object]:
    return error_response("internal server error", "internal_error")


def unauthorized_response() -> dict[str, object]:
    return error_response("unauthorized: valid API key required", "unauthorized")


def rate_limited_response() -> dict[str, object]:
    return error_response("rate limit exceeded", "rate_limited")


class GatewayError(Exception):
    status_code = 500
    error_type = "internal_error"

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_response(self) -> dict[str, object]:
        return error_response(self.message, self.error_type)

    def to_anthropic_response(self) -> dict[str, object]:
        # Anthropic error envelope (ADR-0019, R5): same status mapping,
        # different shape — {"type": "error", "error": {...}}
        return {
            "type": "error",
            "error": {
                "type": self.error_type,
                "message": self.message,
            },
        }


class BadRequestError(GatewayError):
    status_code = 400
    error_type = "bad_request"


class ModelNotFoundError(GatewayError):
    status_code = 404
    error_type = "model_not_found"


class ProviderConfigurationError(GatewayError):
    status_code = 500
    error_type = "provider_configuration_error"


class UpstreamProviderError(GatewayError):
    status_code = 502
    error_type = "upstream_provider_error"
