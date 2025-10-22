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


def compute_target_vm_name(
    source_vm_name: str,
    vm_spec: Optional[Dict[str, Any]] = None,
    override_target_vm_name: Optional[str] = None,
) -> str:
    """
    Compute 'vm-{os}-{env}-{app}' from inputs; override takes precedence.
    """
    if override_target_vm_name and str(override_target_vm_name).strip():
        return str(override_target_vm_name).strip()

    name = str(source_vm_name or "").strip()

    os_prefix_match = re.match(r"^(dca|lnx)", name, flags=re.IGNORECASE)
    os_prefix = os_prefix_match.group(1).lower() if os_prefix_match else "vm"

    env = "prod"
    if isinstance(vm_spec, dict):
        env = str(vm_spec.get("env", env) or env)

    if isinstance(vm_spec, dict) and vm_spec.get("app_name"):
        app_name_raw = str(vm_spec.get("app_name"))
    else:
        app_name_raw = re.sub(r"^(dca|lnx)-?", "", name, flags=re.IGNORECASE)

    app_name_camel = to_camel_case(app_name_raw)

    digit_suffix_match = re.search(r"(\d+)$", name)
    if digit_suffix_match:
        numeric_suffix = digit_suffix_match.group(1)
        if not re.search(r"\d+$", app_name_camel):
            app_name_camel = f"{app_name_camel}-{numeric_suffix}"

    return f"vm-{os_prefix}-{env}-{app_name_camel}"


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
            "compute_target_vm_name": compute_target_vm_name,
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
