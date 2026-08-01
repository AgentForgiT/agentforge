from __future__ import annotations

from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentforge_gateway.config import DEFAULT_CONFIG, load_config, parse_config


def minimal_config() -> dict[str, object]:
    return {
        "models": {
            "mock-coder": {
                "provider": "mock",
                "provider_model": "mock-coder-v1",
            }
        }
    }


class GatewayConfigValidationTests(unittest.TestCase):
    def test_parse_minimal_config_uses_default_server_and_mock_provider(self) -> None:
        config = parse_config(minimal_config())

        self.assertEqual(config.host, "127.0.0.1")
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.providers["mock"].type, "mock")

    def test_load_config_without_path_returns_default_config(self) -> None:
        self.assertIs(load_config(), DEFAULT_CONFIG)

    def test_parse_openrouter_provider_config(self) -> None:
        config = parse_config(
            {
                "models": {
                    "openrouter-coder": {
                        "provider": "openrouter",
                        "provider_model": "qwen/qwen3-coder:free",
                    }
                },
                "providers": {
                    "openrouter": {
                        "type": "openrouter",
                        "base_url": "https://openrouter.ai/api/v1",
                        "api_key_env": "OPENROUTER_API_KEY",
                        "timeout_seconds": 10,
                        "headers": {"HTTP-Referer": "https://github.com/AgentForgiT/agentforge"},
                    }
                },
            }
        )

        self.assertEqual(config.models["openrouter-coder"].provider, "openrouter")
        self.assertEqual(config.providers["openrouter"].type, "openrouter")
        self.assertEqual(config.providers["openrouter"].timeout_seconds, 10)
        self.assertEqual(config.providers["openrouter"].headers["HTTP-Referer"], "https://github.com/AgentForgiT/agentforge")

    def test_example_configs_parse(self) -> None:
        load_config(REPO_ROOT / "apps/gateway/config.example.json")
        load_config(REPO_ROOT / "apps/gateway/config.openrouter.example.json")
        load_config(REPO_ROOT / "apps/gateway/config.ollama.example.json")

    def test_ollama_example_config_uses_ollama_provider(self) -> None:
        config = load_config(REPO_ROOT / "apps/gateway/config.ollama.example.json")

        self.assertEqual(config.models["local-llama3"].provider, "ollama")
        self.assertEqual(config.models["local-llama3"].provider_model, "llama3.2")
        self.assertEqual(config.providers["ollama"].type, "ollama")
        self.assertEqual(config.providers["ollama"].base_url, "http://127.0.0.1:11434/v1")
        self.assertEqual(config.providers["ollama"].timeout_seconds, 120)

    def test_parse_config_rejects_non_object_root(self) -> None:
        with self.assert_config_error("JSON object"):
            parse_config([])

    def test_parse_config_rejects_non_object_server(self) -> None:
        raw = minimal_config()
        raw["server"] = []

        with self.assert_config_error("server"):
            parse_config(raw)

    def test_parse_config_rejects_empty_host(self) -> None:
        raw = minimal_config()
        raw["server"] = {"host": ""}

        with self.assert_config_error("server.host"):
            parse_config(raw)

    def test_parse_config_rejects_non_string_host(self) -> None:
        raw = minimal_config()
        raw["server"] = {"host": 127}

        with self.assert_config_error("server.host"):
            parse_config(raw)

    def test_parse_config_rejects_null_host(self) -> None:
        raw = minimal_config()
        raw["server"] = {"host": None}

        with self.assert_config_error("server.host"):
            parse_config(raw)

    def test_parse_config_rejects_invalid_port(self) -> None:
        for port in (0, 65536, "8080", True):
            raw = minimal_config()
            raw["server"] = {"port": port}

            with self.subTest(port=port):
                with self.assert_config_error("server.port"):
                    parse_config(raw)

    def test_parse_config_rejects_missing_models(self) -> None:
        with self.assert_config_error("model"):
            parse_config({})

    def test_parse_config_rejects_non_object_model(self) -> None:
        with self.assert_config_error("model 'mock-coder'"):
            parse_config({"models": {"mock-coder": []}})

    def test_parse_config_rejects_missing_model_provider(self) -> None:
        with self.assert_config_error("model 'mock-coder'.provider"):
            parse_config({"models": {"mock-coder": {"provider_model": "mock-coder-v1"}}})

    def test_parse_config_rejects_empty_model_provider_model(self) -> None:
        with self.assert_config_error("model 'mock-coder'.provider_model"):
            parse_config({"models": {"mock-coder": {"provider": "mock", "provider_model": ""}}})

    def test_parse_config_rejects_unknown_provider_reference(self) -> None:
        with self.assert_config_error("unknown provider"):
            parse_config(
                {
                    "models": {
                        "openrouter-coder": {
                            "provider": "openrouter",
                            "provider_model": "qwen/qwen3-coder:free",
                        }
                    }
                }
            )

    def test_parse_config_rejects_non_object_providers(self) -> None:
        raw = minimal_config()
        raw["providers"] = []

        with self.assert_config_error("providers"):
            parse_config(raw)

    def test_parse_config_rejects_non_object_provider(self) -> None:
        raw = minimal_config()
        raw["providers"] = {"mock": []}

        with self.assert_config_error("provider 'mock'"):
            parse_config(raw)

    def test_parse_config_rejects_empty_provider_type(self) -> None:
        raw = minimal_config()
        raw["providers"] = {"mock": {"type": ""}}

        with self.assert_config_error("provider 'mock'.type"):
            parse_config(raw)

    def test_parse_config_rejects_invalid_timeout(self) -> None:
        for timeout in (0, -1, "30", True):
            raw = minimal_config()
            raw["providers"] = {"mock": {"type": "mock", "timeout_seconds": timeout}}

            with self.subTest(timeout=timeout):
                with self.assert_config_error("timeout_seconds"):
                    parse_config(raw)

    def test_parse_config_rejects_non_object_headers(self) -> None:
        raw = minimal_config()
        raw["providers"] = {"mock": {"type": "mock", "headers": []}}

        with self.assert_config_error("headers"):
            parse_config(raw)

    def test_parse_config_rejects_null_headers(self) -> None:
        raw = minimal_config()
        raw["providers"] = {"mock": {"type": "mock", "headers": None}}

        with self.assert_config_error("headers"):
            parse_config(raw)

    def test_parse_config_rejects_non_string_header_value(self) -> None:
        raw = minimal_config()
        raw["providers"] = {"mock": {"type": "mock", "headers": {"X-Test": 1}}}

        with self.assert_config_error("headers"):
            parse_config(raw)

    def test_parse_config_rejects_non_string_optional_provider_field(self) -> None:
        raw = minimal_config()
        raw["providers"] = {"mock": {"type": "mock", "base_url": 42}}

        with self.assert_config_error("base_url"):
            parse_config(raw)

    def test_parse_config_default_log_level_is_info(self) -> None:
        config = parse_config(minimal_config())

        self.assertEqual(config.log_level, "INFO")

    def test_parse_config_normalizes_lowercase_log_level(self) -> None:
        raw = minimal_config()
        raw["server"] = {"log_level": "debug"}

        config = parse_config(raw)

        self.assertEqual(config.log_level, "DEBUG")

    def test_parse_config_rejects_invalid_log_level(self) -> None:
        for level in ("TRACE", "verbose", "", 42, True, None):
            raw = minimal_config()
            raw["server"] = {"log_level": level}

            with self.subTest(level=level):
                with self.assert_config_error("server.log_level"):
                    parse_config(raw)

    def assert_config_error(self, expected: str) -> object:
        return self.assertRaisesRegex(ValueError, expected)


if __name__ == "__main__":
    unittest.main()
