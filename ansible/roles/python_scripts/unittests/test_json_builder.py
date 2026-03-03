#!/usr/bin/env python3
"""
test_json_builder.py
====================
Unit tests for json_builder.py.

Coverage:
  - _env              : returns stripped value, empty string when unset,
                        empty string when set to empty
  - _env_bool         : "true" → True, "false" → False, case-insensitive,
                        default="true" respected, unset uses default
  - _require_env      : returns value when set, raises ConfigurationError
                        when unset, raises when set to empty string
  - _build_join_vars  : all fields populated correctly, WORKFLOW_MANIFEST
                        missing raises ConfigurationError, missing password
                        logs warning, dry_run defaults to True,
                        rename_winrm_username defaults to Administrator,
                        rename_winrm_username overridden by WORKFLOW_RENAME_USERNAME
  - _build_disjoin_vars: all fields populated correctly, WORKFLOW_MANIFEST
                         missing raises ConfigurationError, dry_run defaults to True,
                         rename_winrm_username defaults to Administrator,
                         rename_winrm_username overridden by WORKFLOW_RENAME_USERNAME
  - build_extra_vars  : join action dispatched, disjoin action dispatched,
                        invalid action raises ConfigurationError, action is
                        case-insensitive, error message lists valid actions
  - write_extra_vars  : file written with correct JSON, indent=2 used,
                        OSError propagated on write failure
  - main              : missing argv exits with code 1, ConfigurationError
                        exits with code 1, OSError exits with code 1, success
                        logs output filename and action
"""

import json
import os
import sys
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock, call, mock_open, patch

# ---------------------------------------------------------------------------
# Path setup — allow importing the module from the parent directory
# ---------------------------------------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json_builder as module
from json_builder import (
    ConfigurationError,
    RENAME_USERNAME,
    _build_disjoin_vars,
    _build_join_vars,
    _env,
    _env_bool,
    _require_env,
    build_extra_vars,
    write_extra_vars,
)

# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _base_join_env() -> Dict[str, str]:
    """Return a minimal environment dict sufficient for the join workflow."""
    return {
        "WORKFLOW_MANIFEST": "ansible/vars/test/manifest.yml",
        "WORKFLOW_DRY_RUN": "false",
        "WORKFLOW_FORCE_REJOIN": "false",
        "WORKFLOW_SKIP_HOSTNAME_SETUP": "false",
        "SECRET_DOMAIN_ADMIN_VALUE": "s3cr3t",  # pragma: allowlist secret
        "SECRET_DOMAIN_OU_PATH": "OU=Servers,DC=corp,DC=com",
    }


def _base_join_env_with_rename() -> Dict[str, str]:
    """Return a join environment dict with an explicit WORKFLOW_RENAME_USERNAME."""
    return {**_base_join_env(), "WORKFLOW_RENAME_USERNAME": "CustomAdmin"}


def _base_disjoin_env() -> Dict[str, str]:
    """Return a minimal environment dict sufficient for the disjoin workflow."""
    return {
        "WORKFLOW_MANIFEST": "ansible/vars/test/manifest.yml",
        "WORKFLOW_DRY_RUN": "false",
    }


def _capture_written(handle: MagicMock) -> str:
    """Join all strings passed to write() across all mock_open call instances.

    json.dump() issues multiple write() calls (one per chunk), so checking
    only call_args captures only the final chunk. This helper stitches them
    all together so assertions can operate on the complete JSON output.
    """
    return "".join(c.args[0] for c in handle().write.call_args_list)


# ---------------------------------------------------------------------------
# _env
# ---------------------------------------------------------------------------


class TestEnv(unittest.TestCase):
    """Tests for the _env() environment variable helper."""

    def test_returns_stripped_value(self) -> None:
        with patch.dict(os.environ, {"MY_VAR": "  hello  "}):
            self.assertEqual(_env("MY_VAR"), "hello")

    def test_returns_empty_string_when_unset(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(_env("MY_VAR"), "")

    def test_returns_empty_string_when_set_to_empty(self) -> None:
        with patch.dict(os.environ, {"MY_VAR": ""}):
            self.assertEqual(_env("MY_VAR"), "")


# ---------------------------------------------------------------------------
# _env_bool
# ---------------------------------------------------------------------------


class TestEnvBool(unittest.TestCase):
    """Tests for the _env_bool() boolean environment variable helper."""

    def test_returns_true_for_lowercase_true(self) -> None:
        with patch.dict(os.environ, {"MY_FLAG": "true"}):
            self.assertTrue(_env_bool("MY_FLAG"))

    def test_returns_true_for_uppercase_true(self) -> None:
        with patch.dict(os.environ, {"MY_FLAG": "TRUE"}):
            self.assertTrue(_env_bool("MY_FLAG"))

    def test_returns_true_for_mixed_case_true(self) -> None:
        with patch.dict(os.environ, {"MY_FLAG": "True"}):
            self.assertTrue(_env_bool("MY_FLAG"))

    def test_returns_false_for_false_string(self) -> None:
        with patch.dict(os.environ, {"MY_FLAG": "false"}):
            self.assertFalse(_env_bool("MY_FLAG"))

    def test_returns_false_for_arbitrary_non_true_value(self) -> None:
        with patch.dict(os.environ, {"MY_FLAG": "yes"}):
            self.assertFalse(_env_bool("MY_FLAG"))

    def test_returns_false_when_unset_and_default_is_false(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_env_bool("MY_FLAG", default="false"))

    def test_returns_true_when_unset_and_default_is_true(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertTrue(_env_bool("MY_FLAG", default="true"))

    def test_default_is_false_when_not_specified(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(_env_bool("MY_FLAG"))

    def test_returns_false_for_empty_string_using_default(self) -> None:
        with patch.dict(os.environ, {"MY_FLAG": ""}):
            self.assertFalse(_env_bool("MY_FLAG", default="false"))


# ---------------------------------------------------------------------------
# _require_env
# ---------------------------------------------------------------------------


class TestRequireEnv(unittest.TestCase):
    """Tests for the _require_env() mandatory variable helper."""

    def test_returns_value_when_variable_is_set(self) -> None:
        with patch.dict(os.environ, {"MY_VAR": "  value  "}):
            self.assertEqual(_require_env("MY_VAR"), "value")

    def test_raises_configuration_error_when_variable_is_unset(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                _require_env("MY_VAR")
        self.assertIn("MY_VAR", str(ctx.exception))

    def test_raises_configuration_error_when_variable_is_empty_string(self) -> None:
        with patch.dict(os.environ, {"MY_VAR": ""}):
            with self.assertRaises(ConfigurationError) as ctx:
                _require_env("MY_VAR")
        self.assertIn("MY_VAR", str(ctx.exception))

    def test_raises_configuration_error_when_variable_is_whitespace_only(self) -> None:
        with patch.dict(os.environ, {"MY_VAR": "   "}):
            with self.assertRaises(ConfigurationError) as ctx:
                _require_env("MY_VAR")
        self.assertIn("MY_VAR", str(ctx.exception))


# ---------------------------------------------------------------------------
# _build_join_vars
# ---------------------------------------------------------------------------


class TestBuildJoinVars(unittest.TestCase):
    """Tests for the _build_join_vars() join workflow builder."""

    def test_returns_all_expected_keys(self) -> None:
        with patch.dict(os.environ, _base_join_env(), clear=True):
            result = _build_join_vars()
        expected_keys = {
            "manifest", "dry_run", "force_rejoin", "skip_hostname_setup",
            "winrm_username", "rename_winrm_username", "domain_admin_password", "domain_ou_path",
        }
        self.assertEqual(set(result.keys()), expected_keys)

    def test_manifest_value_matches_env_var(self) -> None:
        with patch.dict(os.environ, _base_join_env(), clear=True):
            result = _build_join_vars()
        self.assertEqual(result["manifest"], "ansible/vars/test/manifest.yml")

    def test_dry_run_defaults_to_true_when_not_set(self) -> None:
        env = {k: v for k, v in _base_join_env().items() if k != "WORKFLOW_DRY_RUN"}
        with patch.dict(os.environ, env, clear=True):
            result = _build_join_vars()
        self.assertTrue(result["dry_run"])

    def test_dry_run_false_when_set_to_false(self) -> None:
        with patch.dict(os.environ, {**_base_join_env(), "WORKFLOW_DRY_RUN": "false"}, clear=True):
            result = _build_join_vars()
        self.assertFalse(result["dry_run"])

    def test_force_rejoin_false_by_default(self) -> None:
        env = {k: v for k, v in _base_join_env().items() if k != "WORKFLOW_FORCE_REJOIN"}
        with patch.dict(os.environ, env, clear=True):
            result = _build_join_vars()
        self.assertFalse(result["force_rejoin"])

    def test_winrm_username_is_fixed_constant(self) -> None:
        with patch.dict(os.environ, _base_join_env(), clear=True):
            result = _build_join_vars()
        self.assertEqual(result["winrm_username"], "SE-Admin")

    def test_rename_winrm_username_defaults_to_administrator(self) -> None:
        env = {k: v for k, v in _base_join_env().items() if k != "WORKFLOW_RENAME_USERNAME"}
        with patch.dict(os.environ, env, clear=True):
            result = _build_join_vars()
        self.assertEqual(result["rename_winrm_username"], RENAME_USERNAME)

    def test_rename_winrm_username_uses_workflow_rename_username_when_set(self) -> None:
        with patch.dict(os.environ, _base_join_env_with_rename(), clear=True):
            result = _build_join_vars()
        self.assertEqual(result["rename_winrm_username"], "CustomAdmin")

    def test_raises_configuration_error_when_manifest_not_set(self) -> None:
        env = {k: v for k, v in _base_join_env().items() if k != "WORKFLOW_MANIFEST"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                _build_join_vars()
        self.assertIn("WORKFLOW_MANIFEST", str(ctx.exception))

    def test_logs_warning_when_domain_admin_value_not_set_in_dry_run(self) -> None:
        env = {k: v for k, v in _base_join_env().items() if k != "SECRET_DOMAIN_ADMIN_VALUE"}
        env["WORKFLOW_DRY_RUN"] = "true"  # Enable dry_run mode for testing
        with patch.dict(os.environ, env, clear=True):
            with self.assertLogs(module.log, level="WARNING") as cm:
                _build_join_vars()
        self.assertTrue(any("SECRET_DOMAIN_ADMIN_VALUE" in line for line in cm.output))

    def test_domain_admin_value_empty_when_not_set_in_dry_run(self) -> None:
        env = {k: v for k, v in _base_join_env().items() if k != "SECRET_DOMAIN_ADMIN_VALUE"}
        env["WORKFLOW_DRY_RUN"] = "true"  # Enable dry_run mode for testing
        with patch.dict(os.environ, env, clear=True):
            with self.assertLogs(module.log, level="WARNING"):
                result = _build_join_vars()
        self.assertEqual(result["domain_admin_value"], "")

    def test_raises_error_when_domain_admin_value_not_set_in_production(self) -> None:
        env = {k: v for k, v in _base_join_env().items() if k != "SECRET_DOMAIN_ADMIN_VALUE"}
        env["WORKFLOW_DRY_RUN"] = "false"  # Production mode
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                _build_join_vars()
        self.assertIn("SECRET_DOMAIN_ADMIN_VALUE", str(ctx.exception))


# ---------------------------------------------------------------------------
# _build_disjoin_vars
# ---------------------------------------------------------------------------


class TestBuildDisjoinVars(unittest.TestCase):
    """Tests for the _build_disjoin_vars() disjoin workflow builder."""

    def test_returns_all_expected_keys(self) -> None:
        with patch.dict(os.environ, _base_disjoin_env(), clear=True):
            result = _build_disjoin_vars()
        self.assertEqual(set(result.keys()), {"manifest", "dry_run", "rename_winrm_username"})

    def test_manifest_value_matches_env_var(self) -> None:
        with patch.dict(os.environ, _base_disjoin_env(), clear=True):
            result = _build_disjoin_vars()
        self.assertEqual(result["manifest"], "ansible/vars/test/manifest.yml")

    def test_dry_run_defaults_to_true_when_not_set(self) -> None:
        env = {k: v for k, v in _base_disjoin_env().items() if k != "WORKFLOW_DRY_RUN"}
        with patch.dict(os.environ, env, clear=True):
            result = _build_disjoin_vars()
        self.assertTrue(result["dry_run"])

    def test_dry_run_false_when_set_to_false(self) -> None:
        with patch.dict(os.environ, _base_disjoin_env(), clear=True):
            result = _build_disjoin_vars()
        self.assertFalse(result["dry_run"])

    def test_raises_configuration_error_when_manifest_not_set(self) -> None:
        env = {k: v for k, v in _base_disjoin_env().items() if k != "WORKFLOW_MANIFEST"}
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaises(ConfigurationError) as ctx:
                _build_disjoin_vars()
        self.assertIn("WORKFLOW_MANIFEST", str(ctx.exception))

    def test_does_not_include_join_only_fields(self) -> None:
        with patch.dict(os.environ, _base_disjoin_env(), clear=True):
            result = _build_disjoin_vars()
        self.assertNotIn("winrm_username", result)
        self.assertNotIn("domain_admin_password", result)
        self.assertNotIn("domain_ou_path", result)

    def test_rename_winrm_username_defaults_to_administrator(self) -> None:
        env = {k: v for k, v in _base_disjoin_env().items() if k != "WORKFLOW_RENAME_USERNAME"}
        with patch.dict(os.environ, env, clear=True):
            result = _build_disjoin_vars()
        self.assertEqual(result["rename_winrm_username"], RENAME_USERNAME)

    def test_rename_winrm_username_uses_workflow_rename_username_when_set(self) -> None:
        env = {**_base_disjoin_env(), "WORKFLOW_RENAME_USERNAME": "CustomAdmin"}
        with patch.dict(os.environ, env, clear=True):
            result = _build_disjoin_vars()
        self.assertEqual(result["rename_winrm_username"], "CustomAdmin")


# ---------------------------------------------------------------------------
# build_extra_vars
# ---------------------------------------------------------------------------


class TestBuildExtraVars(unittest.TestCase):
    """Tests for the build_extra_vars() public dispatch function."""

    def test_dispatches_join_action(self) -> None:
        with patch.dict(os.environ, _base_join_env(), clear=True):
            result = build_extra_vars("join")
        self.assertIn("winrm_username", result)

    def test_dispatches_disjoin_action(self) -> None:
        with patch.dict(os.environ, _base_disjoin_env(), clear=True):
            result = build_extra_vars("disjoin")
        self.assertNotIn("winrm_username", result)
        self.assertIn("manifest", result)

    def test_action_matching_is_case_insensitive(self) -> None:
        with patch.dict(os.environ, _base_join_env(), clear=True):
            result = build_extra_vars("JOIN")
        self.assertIn("winrm_username", result)

    def test_action_matching_strips_whitespace(self) -> None:
        with patch.dict(os.environ, _base_disjoin_env(), clear=True):
            result = build_extra_vars("  disjoin  ")
        self.assertIn("manifest", result)

    def test_raises_configuration_error_for_invalid_action(self) -> None:
        with self.assertRaises(ConfigurationError) as ctx:
            build_extra_vars("unknown")
        self.assertIn("unknown", str(ctx.exception))

    def test_error_message_lists_valid_actions(self) -> None:
        with self.assertRaises(ConfigurationError) as ctx:
            build_extra_vars("bad")
        error_msg = str(ctx.exception)
        self.assertIn("join", error_msg)
        self.assertIn("disjoin", error_msg)


# ---------------------------------------------------------------------------
# write_extra_vars
# ---------------------------------------------------------------------------


class TestWriteExtraVars(unittest.TestCase):
    """Tests for the write_extra_vars() JSON serialization helper."""

    def test_writes_valid_json_to_file(self) -> None:
        # json.dump() issues multiple write() calls; join them all to get
        # the complete JSON document before parsing.
        extra_vars = {"manifest": "test.yml", "dry_run": True}
        handle = mock_open()
        with patch("builtins.open", handle):
            write_extra_vars(extra_vars, "/tmp/ansible_extra_vars.json")
        full_output = _capture_written(handle)
        parsed = json.loads(full_output)
        self.assertEqual(parsed["manifest"], "test.yml")
        self.assertTrue(parsed["dry_run"])

    def test_opens_file_for_writing(self) -> None:
        handle = mock_open()
        with patch("builtins.open", handle):
            write_extra_vars({}, "/tmp/ansible_extra_vars.json")
        handle.assert_called_once_with("/tmp/ansible_extra_vars.json", "w", encoding="utf-8")

    def test_json_is_indented_with_two_spaces(self) -> None:
        # Join all write() chunks to check indentation in the full output.
        handle = mock_open()
        with patch("builtins.open", handle):
            write_extra_vars({"key": "value"}, "/tmp/ansible_extra_vars.json")
        full_output = _capture_written(handle)
        self.assertIn("  ", full_output)

    def test_propagates_os_error_on_write_failure(self) -> None:
        with patch("builtins.open", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                write_extra_vars({}, "/tmp/ansible_extra_vars.json")


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain(unittest.TestCase):
    """Tests for the main() entry point."""

    def test_exits_with_code_1_when_no_action_argument_given(self) -> None:
        with patch("sys.argv", ["json_builder.py"]):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_on_configuration_error(self) -> None:
        with patch("sys.argv", ["json_builder.py", "join"]), \
             patch("json_builder.build_extra_vars", side_effect=ConfigurationError("no manifest")):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_on_os_error(self) -> None:
        with patch("sys.argv", ["json_builder.py", "join"]), \
             patch("json_builder.build_extra_vars", return_value={"key": "val"}), \
             patch("json_builder.write_extra_vars", side_effect=OSError("disk full")):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_completes_without_error_on_success(self) -> None:
        with patch("sys.argv", ["json_builder.py", "join"]), \
             patch("json_builder.build_extra_vars", return_value={"key": "val"}), \
             patch("json_builder.write_extra_vars"):
            module.main()  # Should not raise

    def test_logs_output_filename_and_action_on_success(self) -> None:
        with patch("sys.argv", ["json_builder.py", "disjoin"]), \
             patch("json_builder.build_extra_vars", return_value={"key": "val"}), \
             patch("json_builder.write_extra_vars"), \
             self.assertLogs(module.log, level="INFO") as cm:
            module.main()
        log_output = " ".join(cm.output)
        self.assertIn("ansible_extra_vars.json", log_output)
        self.assertIn("disjoin", log_output)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
