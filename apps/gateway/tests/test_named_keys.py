from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
CLI_SRC = ROOT.parent / "cli" / "src"
sys.path.insert(0, str(CLI_SRC))

from agentforge_gateway.keystore import (
    NamedKey,
    decrypt_store,
    encrypt_store,
    generate_key,
    load_key_store,
    write_encrypted_key_store,
    write_key_store,
)


def store_with(alice_rpm: int | None = 60, bob_rpm: int | None = 300) -> dict[str, str]:
    return {
        "alice": generate_key(),
        "bob": generate_key(),
    }


class KeyStoreTests(unittest.TestCase):
    def test_generate_key_format(self) -> None:
        key = generate_key()
        self.assertTrue(key.startswith("af-k-"))
        self.assertGreater(len(key), 8)

    def test_write_and_load_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            write_key_store(path, [NamedKey(name="alice", key="af-k-a", rate_limit_rpm=60)])
            keys = load_key_store(path)
            self.assertEqual(len(keys), 1)
            self.assertEqual(keys[0].name, "alice")
            self.assertEqual(keys[0].rate_limit_rpm, 60)

    def test_load_rejects_missing_file(self) -> None:
        with self.assertRaises(ValueError):
            load_key_store(Path("no-such-keys.json"))

    def test_load_rejects_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            path.write_text("{not json", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_key_store(path)

    def test_load_rejects_duplicate_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            path.write_text(
                json.dumps({"keys": [{"name": "a", "key": "k1"}, {"name": "a", "key": "k2"}]}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_key_store(path)

    def test_load_rejects_bad_rpm(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            path.write_text(
                json.dumps({"keys": [{"name": "a", "key": "k1", "rate_limit_rpm": -1}]}),
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                load_key_store(path)

    def test_load_rejects_empty_store(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            path.write_text(json.dumps({"keys": []}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_key_store(path)


class NamedKeyAuthTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.store_path = Path(self.tmp.name) / "keys.json"
        self.keys = store_with()
        write_key_store(
            self.store_path,
            [
                NamedKey(name="alice", key=self.keys["alice"], rate_limit_rpm=2),
                NamedKey(name="bob", key=self.keys["bob"], rate_limit_rpm=300),
            ],
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _config(self, **overrides: object):
        from agentforge_gateway.config import DEFAULT_CONFIG, GatewayConfig

        params: dict[str, object] = {
            "host": "127.0.0.1",
            "port": 8080,
            "models": DEFAULT_CONFIG.models,
            "providers": DEFAULT_CONFIG.providers,
        }
        params.update(overrides)
        if "auth_keys_file" not in params:
            params["auth_keys_file"] = str(self.store_path)
        return GatewayConfig(**params)

    def _app(self, **overrides: object):
        from agentforge_gateway.app import GatewayApp

        return GatewayApp(self._config(**overrides))

    def test_named_key_authenticates(self) -> None:
        from agentforge_gateway.app import create_handler
        from http.server import ThreadingHTTPServer
        from urllib.request import Request, urlopen
        import threading

        app = self._app()
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            request = Request(
                f"{base}/v1/chat/completions",
                data=json.dumps({"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]}).encode(),
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {self.keys['alice']}"},
                method="POST",
            )
            with urlopen(request) as response:
                self.assertEqual(response.status, 200)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_unknown_key_returns_401(self) -> None:
        from agentforge_gateway.app import create_handler
        from http.server import ThreadingHTTPServer
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen
        import threading

        app = self._app()
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            request = Request(
                f"{base}/v1/chat/completions",
                data=json.dumps({"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]}).encode(),
                headers={"Content-Type": "application/json", "Authorization": "Bearer af-k-wrong"},
                method="POST",
            )
            with self.assertRaises(HTTPError) as ctx:
                urlopen(request)
            self.assertEqual(ctx.exception.code, 401)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_per_key_rate_limit(self) -> None:
        # alice limited at 2 rpm: third request → 429
        from agentforge_gateway.app import create_handler
        from http.server import ThreadingHTTPServer
        from urllib.error import HTTPError
        from urllib.request import Request, urlopen
        import threading

        app = self._app()
        server = ThreadingHTTPServer(("127.0.0.1", 0), create_handler(app))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address
        base = f"http://{host}:{port}"
        try:
            def post(key: str):
                request = Request(
                    f"{base}/v1/chat/completions",
                    data=json.dumps({"model": "mock-coder", "messages": [{"role": "user", "content": "Hi"}]}).encode(),
                    headers={"Content-Type": "application/json", "x-api-key": key},
                    method="POST",
                )
                try:
                    with urlopen(request) as response:
                        return response.status
                except HTTPError as exc:
                    return exc.code

            # alice: 2 allowed, 3rd blocked
            self.assertEqual(post(self.keys["alice"]), 200)
            self.assertEqual(post(self.keys["alice"]), 200)
            self.assertEqual(post(self.keys["alice"]), 429)
            # bob unaffected (different bucket)
            self.assertEqual(post(self.keys["bob"]), 200)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_shared_key_still_works_alongside(self) -> None:
        os.environ["AGENTFORGE_API_KEY"] = "shared-sekrit"
        try:
            app = self._app(api_key_env="AGENTFORGE_API_KEY")
            self.assertIsNotNone(app.api_key)
            self.assertIsNotNone(app.named_keys)
        finally:
            del os.environ["AGENTFORGE_API_KEY"]

    def test_live_reload_picks_up_new_key_without_restart(self) -> None:
        # add a new key to the store after the app is constructed;
        # the app must authenticate it without a restart (ADR-0031)
        new_key = generate_key()
        from agentforge_gateway.keystore import load_key_store, write_key_store

        current = load_key_store(self.store_path)
        current.append(NamedKey(name="carol", key=new_key, rate_limit_rpm=100))
        write_key_store(self.store_path, current)

        app = self._app()
        live = app._named_keys_live()
        self.assertIn("carol", live)
        self.assertEqual(live["carol"]["key"], new_key)

    def test_per_key_limiter_persists_across_reloads(self) -> None:
        # the same limiter object must be returned across live reloads so
        # rate limits accumulate (ADR-0031)
        app = self._app()
        first = app._named_keys_live()
        second = app._named_keys_live()
        self.assertIs(first["alice"]["limiter"], second["alice"]["limiter"])
        # consuming the shared limiter reflects across reloads
        limiter = first["alice"]["limiter"]
        limiter.allow("alice")  # consume one token
        still_same = app._named_keys_live()["alice"]["limiter"]
        self.assertIs(limiter, still_same)

    def test_malformed_store_fails_startup(self) -> None:
        bad = Path(self.tmp.name) / "bad.json"
        bad.write_text("{oops", encoding="utf-8")
        from agentforge_gateway.app import GatewayApp

        with self.assertRaises(ValueError):
            GatewayApp(
                self._config(auth_keys_file=str(bad))
            )


class AuthKeyCliTests(unittest.TestCase):
    def run_cli(self, args: list[str]) -> tuple[int, str]:
        import io
        from contextlib import redirect_stdout
        from agentforge_cli.cli import main

        sys.path.insert(0, str(ROOT.parent / "cli" / "src"))
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = main(args)
        return code, buffer.getvalue()

    def test_add_list_revoke_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "keys.json"
            code, out = self.run_cli(["auth-key", "add", "--name", "ci", "--rate-limit", "120", "--file", str(store)])
            self.assertEqual(code, 0, out)
            self.assertIn("added key 'ci'", out)
            key_line = [line for line in out.splitlines() if line.startswith("af-k-")]
            self.assertEqual(len(key_line), 1)
            key = key_line[0]
            # key appears exactly once (one-time print)
            self.assertEqual(out.count(key), 1)

            # add a second key so revocation of 'ci' is allowed
            code, out = self.run_cli(["auth-key", "add", "--name", "keep", "--file", str(store)])
            self.assertEqual(code, 0, out)

            code, out = self.run_cli(["auth-key", "list", "--file", str(store)])
            self.assertEqual(code, 0, out)
            self.assertIn("ci\t120", out)
            self.assertNotIn(key, out)  # list never prints keys

            code, out = self.run_cli(["auth-key", "revoke", "--name", "ci", "--file", str(store)])
            self.assertEqual(code, 0, out)
            self.assertIn("revoked key 'ci'", out)

            code, out = self.run_cli(["auth-key", "list", "--file", str(store)])
            self.assertEqual(code, 0, out)
            self.assertNotIn("ci", out)
            self.assertIn("keep", out)

    def test_duplicate_name_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "keys.json"
            self.run_cli(["auth-key", "add", "--name", "x", "--file", str(store)])
            code, out = self.run_cli(["auth-key", "add", "--name", "x", "--file", str(store)])
            self.assertEqual(code, 1)
            self.assertIn("already exists", out)

    def test_revoke_last_key_refused(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "keys.json"
            self.run_cli(["auth-key", "add", "--name", "only", "--file", str(store)])
            code, out = self.run_cli(["auth-key", "revoke", "--name", "only", "--file", str(store)])
            self.assertEqual(code, 1)
            self.assertIn("refusing", out)

    def test_add_encrypt_writes_encrypted_store(self) -> None:
        os.environ["AGENTFORGE_AUTH_KEYS_PASSPHRASE"] = "secret"
        try:
            with tempfile.TemporaryDirectory() as tmp:
                store = Path(tmp) / "keys.json"
                code, out = self.run_cli(["auth-key", "add", "--name", "enc", "--encrypt", "--file", str(store)])
                self.assertEqual(code, 0, out)
                self.assertIn('"encrypted": true', store.read_text(encoding="utf-8"))
                # list works against the encrypted store with the env passphrase
                code, out = self.run_cli(["auth-key", "list", "--file", str(store)])
                self.assertEqual(code, 0, out)
                self.assertIn("enc", out)
        finally:
            del os.environ["AGENTFORGE_AUTH_KEYS_PASSPHRASE"]

    def test_add_encrypt_requires_passphrase(self) -> None:
        os.environ.pop("AGENTFORGE_AUTH_KEYS_PASSPHRASE", None)
        with tempfile.TemporaryDirectory() as tmp:
            store = Path(tmp) / "keys.json"
            code, out = self.run_cli(["auth-key", "add", "--name", "x", "--encrypt", "--file", str(store)])
            self.assertEqual(code, 1)
            self.assertIn("passphrase", out)


class KeyStoreEncryptionTests(unittest.TestCase):
    def test_encrypt_decrypt_roundtrip(self) -> None:
        payload = {"keys": [{"name": "alice", "key": "af-k-x", "rate_limit_rpm": 60}]}
        envelope = encrypt_store(payload, "correct horse")
        self.assertTrue(envelope["encrypted"])
        self.assertEqual(envelope["kdf"], "PBKDF2-HMAC-SHA256")
        decrypted = decrypt_store(envelope, "correct horse")
        self.assertEqual(decrypted, payload)

    def test_wrong_passphrase_fails(self) -> None:
        payload = {"keys": [{"name": "a", "key": "k"}]}
        envelope = encrypt_store(payload, "right")
        with self.assertRaises(ValueError):
            decrypt_store(envelope, "wrong")

    def test_tampered_ciphertext_detected(self) -> None:
        payload = {"keys": [{"name": "a", "key": "k"}]}
        envelope = encrypt_store(payload, "pass")
        tampered = dict(envelope)
        tampered["ciphertext"] = "0" * len(envelope["ciphertext"])
        with self.assertRaises(ValueError):
            decrypt_store(tampered, "pass")

    def test_encrypted_store_roundtrips_through_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            write_encrypted_key_store(path, [NamedKey(name="alice", key="af-k-a", rate_limit_rpm=60)], "secret")
            self.assertIn('"encrypted": true', path.read_text(encoding="utf-8"))
            os.environ["AGENTFORGE_AUTH_KEYS_PASSPHRASE"] = "secret"
            try:
                keys = load_key_store(path)
                self.assertEqual(keys[0].name, "alice")
                self.assertEqual(keys[0].rate_limit_rpm, 60)
            finally:
                del os.environ["AGENTFORGE_AUTH_KEYS_PASSPHRASE"]

    def test_encrypted_store_missing_passphrase_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            write_encrypted_key_store(path, [NamedKey(name="a", key="k")], "secret")
            os.environ.pop("AGENTFORGE_AUTH_KEYS_PASSPHRASE", None)
            with self.assertRaises(ValueError):
                load_key_store(path)

    def test_plaintext_store_still_loads(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            write_key_store(path, [NamedKey(name="bob", key="af-k-b")])
            keys = load_key_store(path)
            self.assertEqual(keys[0].name, "bob")

    def test_gateway_authenticates_against_encrypted_store(self) -> None:
        from agentforge_gateway.app import GatewayApp
        from agentforge_gateway.config import DEFAULT_CONFIG, GatewayConfig

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keys.json"
            key = generate_key()
            write_encrypted_key_store(path, [NamedKey(name="carol", key=key, rate_limit_rpm=100)], "secret")
            os.environ["AGENTFORGE_AUTH_KEYS_PASSPHRASE"] = "secret"
            try:
                config = GatewayConfig(
                    host="127.0.0.1", port=8080, auth_keys_file=str(path),
                    models=DEFAULT_CONFIG.models, providers=DEFAULT_CONFIG.providers,
                )
                app = GatewayApp(config)
                live = app._named_keys_live()
                self.assertEqual(live["carol"]["key"], key)
            finally:
                del os.environ["AGENTFORGE_AUTH_KEYS_PASSPHRASE"]


if __name__ == "__main__":
    unittest.main()
