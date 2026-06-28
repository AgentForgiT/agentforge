from __future__ import annotations


class GatewayError(Exception):
    status_code = 500
    error_type = "internal_error"

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_response(self) -> dict[str, object]:
        return {
            "error": {
                "message": self.message,
                "type": self.error_type,
            }
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
