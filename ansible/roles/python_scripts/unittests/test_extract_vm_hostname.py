#!/usr/bin/env python3
"""
test_extract_vm_hostname.py
============================
Unit tests for extract_vm_hostname.py.

Coverage:
  - load_manifest      : success, blank file, OSError, yaml.YAMLError,
                         file path in error message
  - extract_hostname   : winrm hostname preferred, name fallback, no VMs,
                         no hostname, whitespace stripped, multiple VMs,
                         empty/None hostname fields
  - _write_github_env  : None path warning, file write, OSError propagation,
                         no write when github_env is None, appends to file
  - run                : success with github_env, success without github_env,
                         domain suffix appended, ManifestError propagated,
                         OSError propagated
  - main               : missing MANIFEST_FILE, empty MANIFEST_FILE, file not found,
                         ManifestError, OSError, success exit
"""

import os
import sys
import unittest
from typing import Any, Dict, List
from unittest.mock import mock_open, patch

import yaml

# ---------------------------------------------------------------------------
# Path setup — allow importing the module from the parent directory
# ---------------------------------------------------------------------------

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import extract_vm_hostname as module
from extract_vm_hostname import (
    ManifestError,
    _write_github_env,
    extract_hostname,
    load_manifest,
    run,
)


# ---------------------------------------------------------------------------
# Module-level helpers
# ---------------------------------------------------------------------------


def _manifest_with_hostname(hostname: str) -> Dict[str, List[Dict[str, str]]]:
    """Return a minimal manifest dict containing a single VM with the given name."""
    return {"vms": [{"name": hostname}]}


# ---------------------------------------------------------------------------
# load_manifest
# ---------------------------------------------------------------------------


class TestLoadManifest(unittest.TestCase):
    """Tests for the load_manifest() YAML loading helper."""

    def test_returns_parsed_dict_on_success(self) -> None:
        yaml_content = "vms:\n  - name: server01\n"
        with patch("builtins.open", mock_open(read_data=yaml_content)):
            result = load_manifest("/fake/manifest.yml")
        self.assertEqual(result, {"vms": [{"name": "server01"}]})

    def test_returns_empty_dict_when_file_is_blank(self) -> None:
        with patch("builtins.open", mock_open(read_data="")):
            result = load_manifest("/fake/manifest.yml")
        self.assertEqual(result, {})

    def test_raises_manifest_error_on_os_error(self) -> None:
        with patch("builtins.open", side_effect=OSError("no such file")):
            with self.assertRaises(ManifestError) as ctx:
                load_manifest("/fake/manifest.yml")
        self.assertIn("/fake/manifest.yml", str(ctx.exception))

    def test_raises_manifest_error_on_yaml_parse_failure(self) -> None:
        invalid_yaml = "vms: [\nunclosed bracket"
        with patch("builtins.open", mock_open(read_data=invalid_yaml)), \
             patch("yaml.safe_load", side_effect=yaml.YAMLError("bad syntax")):
            with self.assertRaises(ManifestError) as ctx:
                load_manifest("/fake/manifest.yml")
        self.assertIn("/fake/manifest.yml", str(ctx.exception))

    def test_manifest_file_path_is_included_in_os_error_message(self) -> None:
        with patch("builtins.open", side_effect=OSError("permission denied")):
            with self.assertRaises(ManifestError) as ctx:
                load_manifest("/restricted/path/manifest.yml")
        self.assertIn("/restricted/path/manifest.yml", str(ctx.exception))


# ---------------------------------------------------------------------------
# extract_hostname
# ---------------------------------------------------------------------------


class TestExtractHostname(unittest.TestCase):
    """Tests for the extract_hostname() manifest parsing helper."""

    def test_returns_winrm_hostname_when_present(self) -> None:
        manifest = {"vms": [{"vm_winrm_connect_hostname": "winrm-host", "name": "vm-name"}]}
        self.assertEqual(extract_hostname(manifest), "winrm-host")

    def test_falls_back_to_name_when_winrm_hostname_absent(self) -> None:
        manifest = {"vms": [{"name": "server01"}]}
        self.assertEqual(extract_hostname(manifest), "server01")

    def test_strips_surrounding_whitespace_from_hostname(self) -> None:
        manifest = {"vms": [{"name": "  server01  "}]}
        self.assertEqual(extract_hostname(manifest), "server01")

    def test_uses_first_vm_when_multiple_vms_present(self) -> None:
        manifest = {"vms": [{"name": "first"}, {"name": "second"}]}
        self.assertEqual(extract_hostname(manifest), "first")

    def test_raises_manifest_error_when_no_vms_key(self) -> None:
        with self.assertRaises(ManifestError) as ctx:
            extract_hostname({})
        self.assertIn("No VMs", str(ctx.exception))

    def test_raises_manifest_error_when_vms_list_is_empty(self) -> None:
        with self.assertRaises(ManifestError) as ctx:
            extract_hostname({"vms": []})
        self.assertIn("No VMs", str(ctx.exception))

    def test_raises_manifest_error_when_first_vm_has_no_hostname_fields(self) -> None:
        manifest = {"vms": [{"other_field": "value"}]}
        with self.assertRaises(ManifestError) as ctx:
            extract_hostname(manifest)
        self.assertIn("No hostname", str(ctx.exception))

    def test_raises_manifest_error_when_both_hostname_fields_are_empty(self) -> None:
        manifest = {"vms": [{"vm_winrm_connect_hostname": "", "name": ""}]}
        with self.assertRaises(ManifestError) as ctx:
            extract_hostname(manifest)
        self.assertIn("No hostname", str(ctx.exception))

    def test_raises_manifest_error_when_both_hostname_fields_are_none(self) -> None:
        manifest = {"vms": [{"vm_winrm_connect_hostname": None, "name": None}]}
        with self.assertRaises(ManifestError) as ctx:
            extract_hostname(manifest)
        self.assertIn("No hostname", str(ctx.exception))


# ---------------------------------------------------------------------------
# _write_github_env
# ---------------------------------------------------------------------------


class TestWriteGithubEnv(unittest.TestCase):
    """Tests for the _write_github_env() file export helper."""

    def test_logs_warning_when_github_env_is_none(self) -> None:
        with self.assertLogs(module.log, level="WARNING") as cm:
            _write_github_env(None, "KEY", "value")
        self.assertTrue(any("GITHUB_ENV not set" in line for line in cm.output))

    def test_writes_key_value_pair_to_file(self) -> None:
        handle = mock_open()
        with patch("builtins.open", handle):
            _write_github_env("/tmp/github_env", "DELINEA_SECRET_MACHINE", "host.corp.com")
        handle().write.assert_called_once_with("DELINEA_SECRET_MACHINE=host.corp.com\n")

    def test_propagates_os_error_on_write_failure(self) -> None:
        with patch("builtins.open", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                _write_github_env("/tmp/github_env", "KEY", "val")

    def test_does_not_open_file_when_github_env_is_none(self) -> None:
        with patch("builtins.open", mock_open()) as handle, \
             patch.object(module.log, "warning"):
            _write_github_env(None, "KEY", "val")
        handle.assert_not_called()

    def test_appends_to_existing_file(self) -> None:
        handle = mock_open()
        with patch("builtins.open", handle):
            _write_github_env("/tmp/github_env", "KEY", "val")
        handle.assert_called_once_with("/tmp/github_env", "a", encoding="utf-8")


# ---------------------------------------------------------------------------
# run
# ---------------------------------------------------------------------------


class TestRun(unittest.TestCase):
    """Tests for the run() orchestration function."""

    MANIFEST_FILE = "/fake/manifest.yml"
    GITHUB_ENV = "/tmp/github_env"

    def test_writes_fqdn_to_github_env_on_success(self) -> None:
        manifest = _manifest_with_hostname("server01")
        with patch("extract_vm_hostname.load_manifest", return_value=manifest), \
             patch("extract_vm_hostname._write_github_env") as mock_write:
            run(self.MANIFEST_FILE, self.GITHUB_ENV)
        mock_write.assert_called_once_with(
            self.GITHUB_ENV, "DELINEA_SECRET_MACHINE", "server01.dtenet.com"
        )

    def test_appends_domain_suffix_to_hostname(self) -> None:
        manifest = _manifest_with_hostname("myvm")
        with patch("extract_vm_hostname.load_manifest", return_value=manifest), \
             patch("extract_vm_hostname._write_github_env") as mock_write:
            run(self.MANIFEST_FILE, self.GITHUB_ENV)
        _, _, fqdn = mock_write.call_args[0]
        self.assertTrue(fqdn.endswith(".dtenet.com"))

    def test_passes_none_github_env_to_write_helper(self) -> None:
        manifest = _manifest_with_hostname("server01")
        with patch("extract_vm_hostname.load_manifest", return_value=manifest), \
             patch("extract_vm_hostname._write_github_env") as mock_write:
            run(self.MANIFEST_FILE, None)
        mock_write.assert_called_once_with(None, "DELINEA_SECRET_MACHINE", "server01.dtenet.com")

    def test_propagates_manifest_error_from_load_manifest(self) -> None:
        with patch("extract_vm_hostname.load_manifest", side_effect=ManifestError("bad yaml")):
            with self.assertRaises(ManifestError):
                run(self.MANIFEST_FILE, self.GITHUB_ENV)

    def test_propagates_manifest_error_from_extract_hostname(self) -> None:
        with patch("extract_vm_hostname.load_manifest", return_value={"vms": []}):
            with self.assertRaises(ManifestError):
                run(self.MANIFEST_FILE, self.GITHUB_ENV)

    def test_propagates_os_error_from_write_github_env(self) -> None:
        manifest = _manifest_with_hostname("server01")
        with patch("extract_vm_hostname.load_manifest", return_value=manifest), \
             patch("extract_vm_hostname._write_github_env", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                run(self.MANIFEST_FILE, self.GITHUB_ENV)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


class TestMain(unittest.TestCase):
    """Tests for the main() entry point."""

    def test_exits_with_code_1_when_manifest_file_not_set(self) -> None:
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_when_manifest_file_empty_string(self) -> None:
        with patch.dict(os.environ, {"MANIFEST_FILE": "   "}, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_when_manifest_file_not_found(self) -> None:
        with patch.dict(os.environ, {"MANIFEST_FILE": "/nonexistent/manifest.yml"}, clear=True):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_on_manifest_error(self) -> None:
        with patch.dict(os.environ, {"MANIFEST_FILE": "/fake/manifest.yml"}, clear=True), \
             patch("os.path.isfile", return_value=True), \
             patch("extract_vm_hostname.run", side_effect=ManifestError("no vms")):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_exits_with_code_1_on_os_error(self) -> None:
        with patch.dict(os.environ, {"MANIFEST_FILE": "/fake/manifest.yml"}, clear=True), \
             patch("os.path.isfile", return_value=True), \
             patch("extract_vm_hostname.run", side_effect=OSError("disk full")):
            with self.assertRaises(SystemExit) as ctx:
                module.main()
        self.assertEqual(ctx.exception.code, 1)

    def test_completes_without_error_on_success(self) -> None:
        with patch.dict(os.environ, {"MANIFEST_FILE": "/fake/manifest.yml"}, clear=True), \
             patch("os.path.isfile", return_value=True), \
             patch("extract_vm_hostname.run"):
            module.main()  # Should not raise


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main()
