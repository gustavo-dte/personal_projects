import re
from typing import Any, Dict, Optional, List, Iterable


def _normalize_vm_name(candidate_name: Any) -> str:
    """
    Return trimmed name; None yields empty string.
    """
    if candidate_name is None:
        return ""
    return str(candidate_name).strip()


def to_camel_case(raw_name: str) -> str:
    """
    Convert a kebab/underscore/space-delimited string to lowerCamelCase.
    """
    parts = re.split(r"[-_\s]+", raw_name.strip())
    if not parts:
        return ""
    head = parts[0].lower()
    tail = "".join(p.capitalize() for p in parts[1:])
    return f"{head}{tail}"


def validate_target_vm_name(target_vm_name: str) -> bool:
    """
    Validate that target VM name follows the pattern: vm{region}{os}{appname}{env}{instance}

    Pattern breakdown:
    - vm: always "vm" (2 chars)
    - region: cu/e2 (Azure region code, 2 chars)
    - os: win/lnx (3 chars)
    - appname: abbreviated app name (exactly 3 chars)
    - env: p/d/t (1 char)
    - instance: 00-99 (2 chars)
    - Total: exactly 13 characters (2+2+3+3+1+2)

    Examples:
    - vmcuwinwebp01: CP, Central US, Windows, Web server, Production, 01
    - vme2lnxsqlp02: CP, East US 2, Linux, SQL Server, Production, 02
    - vmcuwinmond03: CP, Central US, Windows, Monitoring, Development, 03
    - vme2lnxfilp01: CP, East US 2, Linux, File server, Production, 01
    """

    # Pattern: vm + region + os + appname + env + instance
    # vm (2) + region (2) + os (3) + appname (3) + env (1) + instance (2) = 13 chars
    pattern = r'^vm(cu|e2)(win|lnx)[a-z]{3}[pdt]\d{2}$'

    return bool(re.match(pattern, target_vm_name, re.IGNORECASE))


def _parse_names_input(vm_names_input: Any) -> List[str]:
    """
    Parse names from list/tuple or comma-delimited string; supports STOP_ALL.
    """
    if vm_names_input is None:
        # None means user did not specify; treat as no selection
        return []
    if isinstance(vm_names_input, (list, tuple)):
        return [_normalize_vm_name(n) for n in vm_names_input if _normalize_vm_name(n)]
    raw = str(vm_names_input).strip()
    if not raw:
        # Empty string means no selection
        return []
    # If user passed STOP_ALL/stop_all, return empty list to indicate no filtering
    if raw.upper() == "STOP_ALL":
        # Special token indicates all, caller will handle by passing original list
        return ["__STOP_ALL__"]
    names_list = [name_part.strip() for name_part in raw.split(",")]
    return [name for name in names_list if name]


def filter_vm_specs_by_names(vm_specs: Optional[Iterable[Dict[str, Any]]], vm_names_input: Any) -> List[Dict[str, Any]]:
    """
    Filter a list of VM spec dicts (each containing a 'name' field) by a
    comma-delimited string, list, or 'STOP_ALL'.

    - If names is STOP_ALL/stop_all -> return original vm_specs (no filtering)
    - If names is empty/omitted -> return an empty list (no VMs selected)
    - Else -> include only VM specs whose 'name' matches one of the provided names (exact match)
    """
    specs_list: List[Dict[str, Any]] = list(vm_specs or [])
    requested_names = _parse_names_input(vm_names_input)

    if not requested_names:
        # No names provided -> select none (fail fast expected by caller)
        return []

    if len(requested_names) == 1 and requested_names[0] == "__STOP_ALL__":
        # STOP_ALL -> no filtering
        return specs_list

    requested_set = set(requested_names)
    filtered: List[Dict[str, Any]] = []
    for spec in specs_list:
        vm_name = _normalize_vm_name(spec.get("name")) if isinstance(spec, dict) else ""
        if vm_name and vm_name in requested_set:
            filtered.append(spec)
    return filtered


class FilterModule(object):
    def filters(self):
        return {
            "validate_target_vm_name": validate_target_vm_name,
            "filter_vm_specs_by_names": filter_vm_specs_by_names,
            "compute_vmss_short_hostname": compute_vmss_short_hostname,
        }


def compute_vmss_short_hostname(target_vm_name: str, os_disk_os_type: Optional[str] = None) -> str:
    """
    Build a short hostname for VMSS instances based on the target VM name and OS type.

    Rules:
    - Prefix with 'vm'
    - Strip all non-alphanumeric characters
    - Lowercase the result
    - Truncate to 63 chars for Linux, 9 chars for Windows (provider constraints)
    """
    name = f"vm{str(target_vm_name or '').strip()}"
    normalized = re.sub(r"[^A-Za-z0-9]", "", name).lower()
    os_type = str(os_disk_os_type or "Windows").strip().lower()
    max_len = 63 if os_type == "linux" else 9
    return normalized[:max_len]
