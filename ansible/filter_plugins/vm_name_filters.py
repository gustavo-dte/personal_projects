import re
from typing import Any, Dict, Iterable, List, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalize_vm_name(candidate: Any) -> str:
    """Return a trimmed string from any value; None or non-string values yield an empty string."""
    if candidate is None:
        return ""
    return str(candidate).strip()


def _parse_names_input(vm_names_input: Any) -> List[str]:
    """
    Parse a names input into a list of strings.

    Accepts a list/tuple or a comma-delimited string. Returns:
      - ["STOP_ALL"] when the input equals the STOP_ALL keyword (case-insensitive)
      - []           when input is None or empty (no VMs selected)
      - [name, ...]  list of non-empty name strings otherwise
    """
    _STOP_ALL = "STOP_ALL"

    if vm_names_input is None:
        return []

    if isinstance(vm_names_input, (list, tuple)):
        return [n for n in (_normalize_vm_name(item) for item in vm_names_input) if n]

    raw = str(vm_names_input).strip()
    if not raw:
        return []

    if raw.upper() == _STOP_ALL:
        return [_STOP_ALL]

    return [name for name in (part.strip() for part in raw.split(",")) if name]


# ---------------------------------------------------------------------------
# Public filter functions
# ---------------------------------------------------------------------------


def validate_target_vm_name(target_vm_name: str) -> bool:
    """
    Validate that a target VM name follows the naming convention:
      vm{region}{os}{appname}{env}{instance}

    Segments:
      vm        — literal prefix (2 chars)
      region    — cu | e2 (2 chars)
      os        — win | lnx (3 chars)
      appname   — abbreviated app name, lowercase letters (3+ chars)
      env       — p | d | t (1 char)
      instance  — zero-padded number (2 digits)

    Minimum length: 13 characters (2+2+3+3+1+2)

    Examples:
      vmcuwinwebp01   Central US, Windows, web server, production, instance 01
      vme2lnxsqlp02   East US 2, Linux, SQL server, production, instance 02
      vmcuwinmond03   Central US, Windows, monitoring, development, instance 03
    """
    pattern = r"^vm(cu|e2)(win|lnx)[a-z]{3,}[pdt]\d{2}$"
    return bool(re.match(pattern, target_vm_name, re.IGNORECASE))


def compute_vmss_short_hostname(target_vm_name: str, os_disk_os_type: Optional[str] = None) -> str:
    """
    Build a VMSS-compatible short hostname from a target VM name and OS type.

    Rules:
      - Prepend "vm" to the name
      - Strip all non-alphanumeric characters
      - Lowercase the result
      - Truncate to 63 chars for Linux, 9 chars for Windows (provider constraints)
    """
    raw = f"vm{_normalize_vm_name(target_vm_name)}"
    normalized = re.sub(r"[^A-Za-z0-9]", "", raw).lower()
    os_type = _normalize_vm_name(os_disk_os_type).lower() or "windows"
    max_len = 63 if os_type == "linux" else 9
    return normalized[:max_len]


def filter_vm_specs_by_names(
    vm_specs: Optional[Iterable[Dict[str, Any]]],
    vm_names_input: Any,
) -> List[Dict[str, Any]]:
    """
    Filter a list of VM spec dicts by a names input (comma-delimited string, list, or 'STOP_ALL').

    Behaviour:
      - STOP_ALL / stop_all  → return all vm_specs unfiltered
      - empty / None         → return empty list (no VMs selected)
      - named list           → return only specs whose 'name' exactly matches one of the given names
    """
    specs_list: List[Dict[str, Any]] = list(vm_specs or [])
    requested = _parse_names_input(vm_names_input)

    if not requested:
        return []

    if requested == ["STOP_ALL"]:
        return specs_list

    requested_set = set(requested)
    return [
        spec
        for spec in specs_list
        if isinstance(spec, dict) and _normalize_vm_name(spec.get("name")) in requested_set
    ]


# ---------------------------------------------------------------------------
# Ansible FilterModule
# ---------------------------------------------------------------------------


class FilterModule:
    def filters(self) -> Dict[str, Any]:
        return {
            "validate_target_vm_name":     validate_target_vm_name,
            "compute_vmss_short_hostname": compute_vmss_short_hostname,
            "filter_vm_specs_by_names":    filter_vm_specs_by_names,
        }
