#!/usr/bin/env python3
"""
test_resolve_delinea_secret_id.py
==================================
Unit tests for resolve_delinea_secret_id.py.

Coverage:
  - _env                     : env var reading and stripping
  - _sanitize_secret_id      : valid/invalid ID formats
  - _write_github_env        : None path warning, file write, OSError propagation
  - _item_val                : slug matching, multi-slug, missing slug
  - _matches_by_name         : fqdn\\account format, non-matching, missing backslash
  - _matches_by_items        : slug-based machine+account matching
  - _resolve_by_exact_name   : hit, miss, empty records
  - _resolve_by_machine      : fast path, slow path, no match, ambiguous match,
                               missing filter guard, skipped on fetch error
  - Config.from_env          : valid config, missing credentials, missing search criteria
  - _acquire_token           : success, HTTP error, network error, missing token
  - _search_secrets          : success, HTTP error, network error
  - _fetch_detail            : success, HTTP error, network error
  - resolve                  : exact name strategy, machine strategy, no match fallback
  - main                     : configuration error, delinea error, write error
"""

import sys
import os
import unittest
from io import StringIO
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch, mock_open

# ---------------------------------------------------------------------------
# Path setup — allow importing the module from the parent directory
# ---------------------------------------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import resolve_delinea_secret_id as module
from resolve_delinea_secret_id import (
    Config,
    ConfigurationError,
    DelineaError,
    _acquire_token,
    _env,
    _fetch_detail,
    _item_val,
    _matches_by_items,
    _matches_by_name,
    _resolve_by_exact_name,
    _resolve_by_machine,
    _sanitize_secret_id,
    _search_secrets,
    _write_github_env,
    resolve,
)
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_http_error(status_code: int) -> HTTPError:
    """Build a minimal HTTPError with the given status code."""
    response = MagicMock()
    response.status_code = status_code
    return HTTPError(response=response)


def _make_config(**overrides: Any) -> Config:
    """Return a minimal valid Config, with optional field overrides."""
    defaults: Dict[str, Any] = {
        "base_url": "https://delinea.example.com",
        "username": "svc-account",
        "password": "s3cr3t",
        "search_text": "my-secret",
        "machine_filter": "",
        "secret_name_filter": "",
        "account_filter": "",
        "github_env": None,
    }
    defaults.update(overrides)
    return Config(**defaults)


# ---------------------------------------------------------------------------
# _env
# ---------------------------------------------------------------------------

class TestEnv(unittest.TestCase):
    """Tests for the _env() environment variable helper."""

    def test_returns_stripped_value(self) -> None:
        with patch.dict(os.environ, {"MY_VAR": "  hello  "}):
            self.assertEqual(_env("MY_VAR"), "hello")

    def test_returns_empty_string_when_unset(self) -> None:
        env = {k: v for k, v in os.environ.items() if k != "MY_VAR"}
        with patch.dict(os.environ, env, clear=True):
            self.assertEqual(_env("MY_VAR"), "")

    def test_returns_empty_string_when_set_to_empty(self) -> None:
        with patch.dict(os.environ, {"MY_VAR": ""}):
            self.assertEqual(_env("MY_VAR"), "")


# ---------------------------------------------------------------------------
# _sanitize_secret_id
# ---------------------------------------------------------------------------

class TestSanitizeSecretId(unittest.TestCase):
    """Tests for the _sanitize_secret_id() validation helper."""

    def test_valid_numeric_id_returned_unchanged(self) -> None:
        self.assertEqual(_sanitize_secret_id("12345"), "12345")

    def test_strips_surrounding_whitespace(self) -> None:
        self.assertEqual(_sanitize_secret_id("  99  "), "99")

    def test_raises_on_non_numeric_characters(self) -> None:
        with self.assertRaises(ValueError):
            _sanitize_secret_id("123abc")

    def test_raises_on_empty_string(self) -> None:
        with self.assertRaises(ValueError):
            _sanitize_secret_id("")

    def test_raises_on_whitespace_only(self) -> None:
        with self.assertRaises(ValueError):
            _sanitize_secret_id("   ")

    def test_raises_on_float_format(self) -> None:
        with self.assertRaises(ValueError):
            _sanitize_secret_id("123.45")

    def test_raises_on_negative_number(self) -> None:
        with self.assertRaises(ValueError):
            _sanitize_secret_id("-1")


# ---------------------------------------------------------------------------
# _write_github_env
# ---------------------------------------------------------------------------

class TestWriteGithubEnv(unittest.TestCase):
    """Tests for the _write_github_env() file export helper."""

    def test_logs_warning_when_github_env_is_none(self) -> None:
        with self.assertLogs(module.log, level="WARNING") as cm:
            _write_github_env(None, "KEY", "value")
        self.assertTrue(any("GITHUB_ENV not set" in line for line in cm.output))

    def test_writes_key_value_to_file(self) -> None:
        handle = mock_open()
        with patch("builtins.open", handle):
            _write_github_env("/tmp/github_env", "DELINEA_SECRET_ID", "42")
        handle().write.assert_called_once_with("DELINEA_SECRET_ID=42\n")

    def test_propagates_os_error_on_write_failure(self) -> None:
        with patch("builtins.open", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                _write_github_env("/tmp/github_env", "KEY", "val")

    def test_does_not_write_when_github_env_is_none(self) -> None:
        with patch("builtins.open", mock_open()) as handle:
            with patch.object(module.log, "warning"):
                _write_github_env(None, "KEY", "val")
        handle.assert_not_called()


# ---------------------------------------------------------------------------
# _item_val
# ---------------------------------------------------------------------------

class TestItemVal(unittest.TestCase):
    """Tests for the _item_val() slug-matching helper."""

    def _make_item(self, slug: str, value: str) -> Dict[str, str]:
        return {"slug": slug, "itemValue": value}

    def test_returns_value_for_matching_slug(self) -> None:
        items = [self._make_item("machine", "server01.example.com")]
        self.assertEqual(_item_val(items, "machine"), "server01.example.com")

    def test_matching_is_case_insensitive(self) -> None:
        items = [self._make_item("MACHINE", "SERVER01")]
        self.assertEqual(_item_val(items, "machine"), "server01")

    def test_returns_first_matching_slug(self) -> None:
        items = [
            self._make_item("host", "first"),
            self._make_item("machine", "second"),
        ]
        self.assertEqual(_item_val(items, "machine", "host"), "first")

    def test_returns_empty_string_when_no_slug_matches(self) -> None:
        items = [self._make_item("unrelated", "value")]
        self.assertEqual(_item_val(items, "machine", "host"), "")

    def test_returns_empty_string_for_empty_items_list(self) -> None:
        self.assertEqual(_item_val([], "machine"), "")

    def test_value_is_lowercased(self) -> None:
        items = [self._make_item("username", "DomainAdmin")]
        self.assertEqual(_item_val(items, "username"), "domainadmin")


# ---------------------------------------------------------------------------
# _matches_by_name
# ---------------------------------------------------------------------------

class TestMatchesByName(unittest.TestCase):
    """Tests for the _matches_by_name() fast-path predicate."""

    def test_returns_true_for_matching_fqdn_and_account(self) -> None:
        self.assertTrue(
            _matches_by_name("server01.corp.com\\se-admin", "server01.corp.com", "se-admin")
        )

    def test_matching_is_case_insensitive(self) -> None:
        self.assertTrue(
            _matches_by_name("SERVER01.CORP.COM\\SE-Admin", "server01.corp.com", "se-admin")
        )

    def test_returns_false_when_fqdn_does_not_match(self) -> None:
        self.assertFalse(
            _matches_by_name("other.corp.com\\se-admin", "server01.corp.com", "se-admin")
        )

    def test_returns_false_when_account_does_not_match(self) -> None:
        self.assertFalse(
            _matches_by_name("server01.corp.com\\other-user", "server01.corp.com", "se-admin")
        )

    def test_returns_false_when_no_backslash_in_name(self) -> None:
        self.assertFalse(
            _matches_by_name("server01.corp.com", "server01.corp.com", "se-admin")
        )

    def test_returns_false_for_empty_name(self) -> None:
        self.assertFalse(_matches_by_name("", "server01.corp.com", "se-admin"))


# ---------------------------------------------------------------------------
# _matches_by_items
# ---------------------------------------------------------------------------

class TestMatchesByItems(unittest.TestCase):
    """Tests for the _matches_by_items() slow-path predicate."""

    def _make_items(self, machine: str, account: str) -> List[Dict[str, str]]:
        return [
            {"slug": "machine", "itemValue": machine},
            {"slug": "username", "itemValue": account},
        ]

    def test_returns_true_when_both_slugs_match(self) -> None:
        items = self._make_items("server01.corp.com", "se-admin")
        self.assertTrue(_matches_by_items(items, "server01.corp.com", "se-admin"))

    def test_returns_false_when_machine_does_not_match(self) -> None:
        items = self._make_items("other.corp.com", "se-admin")
        self.assertFalse(_matches_by_items(items, "server01.corp.com", "se-admin"))

    def test_returns_false_when_account_does_not_match(self) -> None:
        items = self._make_items("server01.corp.com", "wrong-user")
        self.assertFalse(_matches_by_items(items, "server01.corp.com", "se-admin"))

    def test_returns_false_for_empty_items(self) -> None:
        self.assertFalse(_matches_by_items([], "server01.corp.com", "se-admin"))

    def test_matching_is_case_insensitive(self) -> None:
        items = self._make_items("SERVER01.CORP.COM", "SE-Admin")
        self.assertTrue(_matches_by_items(items, "server01.corp.com", "se-admin"))


# ---------------------------------------------------------------------------
# _resolve_by_exact_name
# ---------------------------------------------------------------------------

class TestResolveByExactName(unittest.TestCase):
    """Tests for the _resolve_by_exact_name() fast-path strategy."""

    def test_returns_sanitized_id_on_exact_match(self) -> None:
        records = [{"id": 42, "name": "my-secret"}]
        self.assertEqual(_resolve_by_exact_name(records, "my-secret"), "42")

    def test_matching_is_case_insensitive(self) -> None:
        records = [{"id": 7, "name": "My-Secret"}]
        self.assertEqual(_resolve_by_exact_name(records, "my-secret"), "7")

    def test_returns_none_when_no_match(self) -> None:
        records = [{"id": 1, "name": "other-secret"}]
        self.assertIsNone(_resolve_by_exact_name(records, "my-secret"))

    def test_returns_none_for_empty_records(self) -> None:
        self.assertIsNone(_resolve_by_exact_name([], "my-secret"))

    def test_returns_none_when_matched_record_has_no_id(self) -> None:
        records = [{"name": "my-secret"}]
        self.assertIsNone(_resolve_by_exact_name(records, "my-secret"))

    def test_ignores_partial_name_matches(self) -> None:
        records = [{"id": 1, "name": "my-secret-extended"}]
        self.assertIsNone(_resolve_by_exact_name(records, "my-secret"))


# ---------------------------------------------------------------------------
# _resolve_by_machine
# ---------------------------------------------------------------------------

class TestResolveByMachine(unittest.TestCase):
    """Tests for the _resolve_by_machine() slow-path strategy."""

    BASE_URL = "https://delinea.example.com"
    AUTH = {"Authorization": "Bearer token"}

    def test_fast_path_matches_fqdn_backslash_account_format(self) -> None:
        records = [{"id": 10, "name": "server01.corp.com\\se-admin"}]
        result = _resolve_by_machine(
            self.BASE_URL, self.AUTH, records, "server01.corp.com", "se-admin", ""
        )
        self.assertEqual(result, "10")

    def test_slow_path_matches_via_item_slugs(self) -> None:
        records = [{"id": 20, "name": "Generic Secret"}]
        detail = {
            "items": [
                {"slug": "machine", "itemValue": "server01.corp.com"},
                {"slug": "username", "itemValue": "se-admin"},
            ]
        }
        with patch("resolve_delinea_secret_id._fetch_detail", return_value=detail):
            result = _resolve_by_machine(
                self.BASE_URL, self.AUTH, records, "server01.corp.com", "", "se-admin"
            )
        self.assertEqual(result, "20")

    def test_raises_configuration_error_when_no_filter_set(self) -> None:
        with self.assertRaises(ConfigurationError):
            _resolve_by_machine(
                self.BASE_URL, self.AUTH, [{"id": 1, "name": "x"}], "machine", "", ""
            )

    def test_raises_delinea_error_when_no_match_found(self) -> None:
        records = [{"id": 1, "name": "unrelated\\other-user"}]
        with self.assertRaises(DelineaError):
            _resolve_by_machine(
                self.BASE_URL, self.AUTH, records, "server01.corp.com", "se-admin", ""
            )

    def test_raises_delinea_error_on_ambiguous_match(self) -> None:
        records = [
            {"id": 1, "name": "server01.corp.com\\se-admin"},
            {"id": 2, "name": "server01.corp.com\\se-admin"},
        ]
        with self.assertRaises(DelineaError) as ctx:
            _resolve_by_machine(
                self.BASE_URL, self.AUTH, records, "server01.corp.com", "se-admin", ""
            )
        self.assertIn("Ambiguous", str(ctx.exception))

    def test_skips_record_with_no_id_in_slow_path(self) -> None:
        records = [{"name": "Generic Secret"}]
        with self.assertRaises(DelineaError):
            _resolve_by_machine(
                self.BASE_URL, self.AUTH, records, "server01.corp.com", "", "se-admin"
            )

    def test_skips_record_when_fetch_detail_raises(self) -> None:
        records = [{"id": 5, "name": "Generic Secret"}]
        with patch(
            "resolve_delinea_secret_id._fetch_detail",
            side_effect=DelineaError("timeout"),
        ):
            with self.assertRaises(DelineaError) as ctx:
                _resolve_by_machine(
                    self.BASE_URL, self.AUTH, records, "server01.corp.com", "", "se-admin"
                )
        self.assertIn("No matching", str(ctx.exception))

    def test_secret_name_filter_takes_priority_over_account_filter(self) -> None:
        records = [{"id": 30, "name": "server01.corp.com\\named-filter"}]
        result = _resolve_by_machine(
            self.BASE_URL,
            self.AUTH,
            records,
            "server01.corp.com",
            "named-filter",
            "account-filter",
        )
        self.assertEqual(result, "30")


# ---------------------------------------------------------------------------
# Config.from_env
# ---------------------------------------------------------------------------

class TestConfigFromEnv(unittest.TestCase):
    """Tests for Config.from_env() environment validation."""

    BASE_ENV = {
        "DELINEA_BASE_URL": "https://delinea.example.com",
        "DELINEA_USERNAME": "svc-account",
        "DELINEA_PASSWORD": "s3cr3t",
        "DELINEA_SECRET_PATH": "my-secret",
    }

    def test_builds_valid_config_from_env(self) -> None:
        with patch.dict(os.environ, self.BASE_ENV, clear=True):
            cfg = Config.from_env()
        self.assertEqual(cfg.base_url, "https://delinea.example.com")
        self.assertEqual(cfg.username, "svc-account")
        self.assertEqual(cfg.search_text, "my-secret")

    def test_strips_trailing_slash_from_base_url(self) -> None:
        env = {**self.BASE_ENV, "DELINEA_BASE_URL": "https://delinea.example.com/"}
        with patch.dict(os.environ, env, clear=True):
            cfg = Config.from_env()
        self.assertEqual(cfg.base_url, "https://delinea.example.com")

    def test_raises_when_base_url_missing(self) -> None:
        env = {k: v for k, v in self.BASE_ENV.items() if k != "DELINEA_BASE_URL"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                Config.from_env()
        self.assertIn("credentials", str(ctx.exception))

    def test_raises_when_username_missing(self) -> None:
        env = {k: v for k, v in self.BASE_ENV.items() if k != "DELINEA_USERNAME"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError):
                Config.from_env()

    def test_raises_when_password_missing(self) -> None:
        env = {k: v for k, v in self.BASE_ENV.items() if k != "DELINEA_PASSWORD"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError):
                Config.from_env()

    def test_raises_when_no_search_criteria(self) -> None:
        env = {k: v for k, v in self.BASE_ENV.items() if k != "DELINEA_SECRET_PATH"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                Config.from_env()
        self.assertIn("search criteria", str(ctx.exception))

    def test_machine_filter_is_lowercased(self) -> None:
        env = {**self.BASE_ENV, "DELINEA_SECRET_MACHINE": "SERVER01.CORP.COM"}
        with patch.dict(os.environ, env, clear=True):
            cfg = Config.from_env()
        self.assertEqual(cfg.machine_filter, "server01.corp.com")

    def test_github_env_is_none_when_unset(self) -> None:
        env = {k: v for k, v in self.BASE_ENV.items()}
        env.pop("GITHUB_ENV", None)
        with patch.dict(os.environ, env, clear=True):
            cfg = Config.from_env()
        self.assertIsNone(cfg.github_env)

    def test_github_env_is_set_when_present(self) -> None:
        env = {**self.BASE_ENV, "GITHUB_ENV": "/tmp/github_env"}
        with patch.dict(os.environ, env, clear=True):
            cfg = Config.from_env()
        self.assertEqual(cfg.github_env, "/tmp/github_env")


# ---------------------------------------------------------------------------
# _acquire_token
# ---------------------------------------------------------------------------

class TestAcquireToken(unittest.TestCase):
    """Tests for the _acquire_token() API client function."""

    def test_returns_token_on_success(self) -> None:
        resp = MagicMock()
        resp.json.return_value = {"access_token": "tok123"}
        with patch("requests.post", return_value=resp):
            token = _acquire_token("https://delinea.example.com", "user", "pass")
        self.assertEqual(token, "tok123")

    def test_raises_delinea_error_on_http_error(self) -> None:
        resp = MagicMock()
        resp.raise_for_status.side_effect = _make_http_error(401)
        with patch("requests.post", return_value=resp):
            with self.assertRaises(DelineaError) as ctx:
                _acquire_token("https://delinea.example.com", "user", "pass")
        self.assertIn("401", str(ctx.exception))

    def test_raises_delinea_error_on_network_failure(self) -> None:
        with patch("requests.post", side_effect=RequestsConnectionError("timeout")):
            with self.assertRaises(DelineaError) as ctx:
                _acquire_token("https://delinea.example.com", "user", "pass")
        self.assertIn("request failed", str(ctx.exception))

    def test_raises_delinea_error_when_token_absent_in_response(self) -> None:
        resp = MagicMock()
        resp.json.return_value = {}
        with patch("requests.post", return_value=resp):
            with self.assertRaises(DelineaError) as ctx:
                _acquire_token("https://delinea.example.com", "user", "pass")
        self.assertIn("access_token", str(ctx.exception))


# ---------------------------------------------------------------------------
# _search_secrets
# ---------------------------------------------------------------------------

class TestSearchSecrets(unittest.TestCase):
    """Tests for the _search_secrets() API client function."""

    AUTH = {"Authorization": "Bearer token"}

    def test_returns_records_on_success(self) -> None:
        resp = MagicMock()
        resp.json.return_value = {"records": [{"id": 1, "name": "secret"}]}
        with patch("requests.get", return_value=resp):
            records = _search_secrets("https://delinea.example.com", self.AUTH, "seed")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["id"], 1)

    def test_returns_empty_list_when_records_key_absent(self) -> None:
        resp = MagicMock()
        resp.json.return_value = {}
        with patch("requests.get", return_value=resp):
            records = _search_secrets("https://delinea.example.com", self.AUTH, "seed")
        self.assertEqual(records, [])

    def test_raises_delinea_error_on_http_error(self) -> None:
        resp = MagicMock()
        resp.raise_for_status.side_effect = _make_http_error(403)
        with patch("requests.get", return_value=resp):
            with self.assertRaises(DelineaError) as ctx:
                _search_secrets("https://delinea.example.com", self.AUTH, "seed")
        self.assertIn("403", str(ctx.exception))

    def test_raises_delinea_error_on_network_failure(self) -> None:
        with patch("requests.get", side_effect=RequestsConnectionError("refused")):
            with self.assertRaises(DelineaError):
                _search_secrets("https://delinea.example.com", self.AUTH, "seed")


# ---------------------------------------------------------------------------
# _fetch_detail
# ---------------------------------------------------------------------------

class TestFetchDetail(unittest.TestCase):
    """Tests for the _fetch_detail() API client function."""

    AUTH = {"Authorization": "Bearer token"}

    def test_returns_detail_dict_on_success(self) -> None:
        resp = MagicMock()
        resp.json.return_value = {"id": 5, "items": []}
        with patch("requests.get", return_value=resp):
            detail = _fetch_detail("https://delinea.example.com", self.AUTH, 5)
        self.assertEqual(detail["id"], 5)

    def test_raises_delinea_error_on_http_error(self) -> None:
        resp = MagicMock()
        resp.raise_for_status.side_effect = _make_http_error(404)
        with patch("requests.get", return_value=resp):
            with self.assertRaises(DelineaError) as ctx:
                _fetch_detail("https://delinea.example.com", self.AUTH, 5)
        self.assertIn("404", str(ctx.exception))

    def test_raises_delinea_error_on_network_failure(self) -> None:
        with patch("requests.get", side_effect=RequestsConnectionError("timeout")):
            with self.assertRaises(DelineaError):
                _fetch_detail("https://delinea.example.com", self.AUTH, 5)

    def test_secret_id_is_included_in_error_message(self) -> None:
        resp = MagicMock()
        resp.raise_for_status.side_effect = _make_http_error(500)
        with patch("requests.get", return_value=resp):
            with self.assertRaises(DelineaError) as ctx:
                _fetch_detail("https://delinea.example.com", self.AUTH, 99)
        self.assertIn("99", str(ctx.exception))


# ---------------------------------------------------------------------------
# resolve
# ---------------------------------------------------------------------------

class TestResolve(unittest.TestCase):
    """Tests for the resolve() orchestration function."""

    def _make_token_resp(self) -> MagicMock:
        resp = MagicMock()
        resp.json.return_value = {"access_token": "tok"}
        return resp

    def test_resolves_via_exact_name_strategy(self) -> None:
        cfg = _make_config(search_text="my-secret")
        search_resp = MagicMock()
        search_resp.json.return_value = {"records": [{"id": 42, "name": "my-secret"}]}

        with patch("requests.post", return_value=self._make_token_resp()), \
             patch("requests.get", return_value=search_resp):
            result = resolve(cfg)

        self.assertEqual(result, "42")

    def test_resolves_via_machine_filter_strategy(self) -> None:
        cfg = _make_config(
            search_text="",
            machine_filter="server01.corp.com",
            account_filter="se-admin",
        )
        search_resp = MagicMock()
        search_resp.json.return_value = {
            "records": [{"id": 7, "name": "server01.corp.com\\se-admin"}]
        }

        with patch("requests.post", return_value=self._make_token_resp()), \
             patch("requests.get", return_value=search_resp):
            result = resolve(cfg)

        self.assertEqual(result, "7")

    def test_raises_delinea_error_when_no_records_returned(self) -> None:
        cfg = _make_config(search_text="my-secret")
        search_resp = MagicMock()
        search_resp.json.return_value = {"records": []}

        with patch("requests.post", return_value=self._make_token_resp()), \
             patch("requests.get", return_value=search_resp):
            with self.assertRaises(DelineaError) as ctx:
                resolve(cfg)

        self.assertIn("No records", str(ctx.exception))

    def test_raises_delinea_error_when_no_strategy_matches(self) -> None:
        cfg = _make_config(search_text="nonexistent", machine_filter="")
        search_resp = MagicMock()
        search_resp.json.return_value = {"records": [{"id": 1, "name": "other"}]}

        with patch("requests.post", return_value=self._make_token_resp()), \
             patch("requests.get", return_value=search_resp):
            with self.assertRaises(DelineaError) as ctx:
                resolve(cfg)

        self.assertIn("No exact name match", str(ctx.exception))

    def test_exact_name_takes_priority_over_machine_filter(self) -> None:
        cfg = _make_config(
            search_text="my-secret",
            machine_filter="server01.corp.com",
            account_filter="se-admin",
        )
        search_resp = MagicMock()
        search_resp.json.return_value = {
            "records": [
                {"id": 100, "name": "my-secret"},
                {"id": 200, "name": "server01.corp.com\\se-admin"},
            ]
        }

        with patch("requests.post", return_value=self._make_token_resp()), \
             patch("requests.get", return_value=search_resp):
            result = resolve(cfg)

        self.assertEqual(result, "100")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

class TestMain(unittest.TestCase):
    """Tests for the main() entry point."""

    def test_exits_with_code_1_on_configuration_error(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_on_delinea_error(self) -> None:
        with patch(
            "resolve_delinea_secret_id.Config.from_env",
            return_value=_make_config(search_text="x"),
        ), patch(
            "resolve_delinea_secret_id.resolve",
            side_effect=DelineaError("api failure"),
        ):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_on_os_error(self) -> None:
        with patch(
            "resolve_delinea_secret_id.Config.from_env",
            return_value=_make_config(search_text="x", github_env="/tmp/ghe"),
        ), patch(
            "resolve_delinea_secret_id.resolve", return_value="42"
        ), patch(
            "builtins.open", side_effect=OSError("disk full")
        ):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_on_value_error_from_sanitization(self) -> None:
        with patch(
            "resolve_delinea_secret_id.Config.from_env",
            return_value=_make_config(search_text="x"),
        ), patch(
            "resolve_delinea_secret_id.resolve",
            side_effect=ValueError("bad id"),
        ):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_writes_secret_id_to_github_env_on_success(self) -> None:
        with patch(
            "resolve_delinea_secret_id.Config.from_env",
            return_value=_make_config(search_text="x", github_env="/tmp/ghe"),
        ), patch(
            "resolve_delinea_secret_id.resolve", return_value="42"
        ), patch("builtins.open", mock_open()) as handle:
            module.main()
        handle().write.assert_called_once_with("DELINEA_SECRET_ID=42\n")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
