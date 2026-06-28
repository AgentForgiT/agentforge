from __future__ import annotations

import time

from .config import GatewayConfig, ModelConfig
from .errors import ModelNotFoundError


class ModelRegistry:
    def __init__(self, config: GatewayConfig) -> None:
        self._models = config.models

    def get(self, name: str) -> ModelConfig:
        try:
            return self._models[name]
        except KeyError as exc:
            raise ModelNotFoundError(f"unknown model: {name}") from exc

    def list_models(self) -> dict[str, object]:
        now = int(time.time())
        return {
            "object": "list",
            "data": [
                {
                    "id": name,
                    "object": "model",
                    "created": now,
                    "owned_by": "agentforge",
                }
                for name in sorted(self._models)
            ],
        }
