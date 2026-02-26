# Common Role

This role provides shared tasks and utilities for Azure migration operations.

## Available Tasks

### load_manifest.yml

Loads the migration manifest from the vars directory based on name. This provides a centralized way for all roles to load the same manifest configuration.

#### Parameters

- `manifest` (string, **required**) - Manifest name to load. This should be passed as a variable from the command line or playbook execution, not hardcoded.

#### Sets Variables

- `manifest` (dictionary) - Contains all manifest configuration including VM definitions, target settings, and Azure resource information

#### Usage Examples

**In role/playbook (DO NOT hardcode the manifest value):**
```yaml
- name: Load migration manifest
  ansible.builtin.include_role:
    name: common
    tasks_from: load_manifest
  vars:
    manifest: "{{ manifest }}"  # Pass through the variable - never hardcode
```

**Command line execution (how users should provide the manifest):**
```bash
# User specifies which manifest to load
ansible-playbook my-playbook.yml -e "manifest=phase_1"
ansible-playbook my-playbook.yml -e "manifest=phase_2"
```

**Note:**
- The `manifest` parameter must be passed as a variable at runtime
- Never hardcode manifest values in Ansible code - always use `"{{ manifest }}"` to pass through the variable
- The task will fail immediately if `manifest` is not provided, ensuring early detection of configuration issues

### azure_verify_prerequisites.yml

Verifies Azure subscription and resource group prerequisites before performing migration operations. Automatically detects which validations to perform based on provided parameters.

#### Parameters

- `target_resource_group` (string, required) - Azure resource group name to verify
- `target_subscription_id` (string, optional) - Azure subscription ID to verify (automatically validated if provided)

#### Behavior

- **Resource Group Only**: If only `target_resource_group` is provided, validates resource group exists
- **Full Validation**: If both `target_resource_group` and `target_subscription_id` are provided, validates both subscription and resource group
- **Format Validation**: Subscription ID is validated against Azure GUID format (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx) for fast failure

#### Usage Examples

**Method 1: Resource group only validation**
```yaml
- name: Verify Azure resource group
  ansible.builtin.include_role:
    name: common
    tasks_from: azure_verify_prerequisites
  vars:
    target_resource_group: "{{ my_resource_group }}"
```

**Method 2: Full subscription + resource group validation**
```yaml
- name: Verify Azure prerequisites
  ansible.builtin.include_role:
    name: common
    tasks_from: azure_verify_prerequisites
  vars:
    target_subscription_id: "{{ my_subscription_id }}"
    target_resource_group: "{{ my_resource_group }}"
```

**Method 3: Add as role dependency (for roles that always need verification)**
```yaml
# In your role's meta/main.yml
dependencies:
  - role: common
    vars:
      target_subscription_id: "{{ target_subscription_id }}"
      target_resource_group: "{{ target_resource_group }}"
```

**Method 4: Direct task include (alternative pattern)**
```yaml
- name: Verify prerequisites
  ansible.builtin.include_tasks: "{{ playbook_dir }}/roles/common/tasks/azure_verify_prerequisites.yml"
  vars:
    target_resource_group: "{{ my_resource_group }}"
    # Add target_subscription_id if subscription validation is also needed
```

## Adding More Common Tasks

To add new common tasks:

1. Create the task file in `tasks/`
2. Add appropriate defaults in `defaults/main.yml`
3. Update `tasks/main.yml` if the task should be included by default
4. Document usage in this README
