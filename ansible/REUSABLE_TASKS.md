## Reusable Tasks
This document explains approache for structuring reusable tasks for this project.

**Structure:**
```
ansible/
├── roles/
│   ├── common/                    # Shared role for common tasks
│   │   ├── tasks/
│   │   │   ├── main.yml          # Entry point for the role
│   │   │   └── azure_verify_prerequisites.yml
│   │   ├── defaults/main.yml      # Default variables
│   │   ├── meta/main.yml         # Role metadata
│   │   └── README.md             # Documentation
│   └── azure_migrate/            # Your specific role
│       └── tasks/
│           ├── main.yml
│           ├── list_projects.yml  # Uses common role
│           └── start_replication.yml  # Uses common role
```

**Usage in tasks:**
```yaml
- name: Verify Azure prerequisites
  ansible.builtin.include_role:
    name: common
    tasks_from: azure_verify_prerequisites
  vars:
    target_subscription_id: "{{ my_subscription_id }}"
    target_resource_group: "{{ my_resource_group }}"
```

## Available Common Tasks

### azure_verify_prerequisites.yml
Verifies Azure subscription and resource group prerequisites. **Automatically detects what to validate** based on provided parameters:
- **Resource Group Only**: If only `target_resource_group` is provided
- **Full Validation**: If both `target_resource_group` and `target_subscription_id` are provided
- **Format Validation**: Subscription ID is validated against Azure GUID format for fast failure

## Usage Examples

### Resource Group Only Verification
```yaml
- name: Verify resource group exists
  ansible.builtin.include_role:
    name: common
    tasks_from: azure_verify_prerequisites
  vars:
    target_resource_group: "my-resource-group"
```

### Full Subscription + Resource Group Verification
```yaml
- name: Verify Azure prerequisites
  ansible.builtin.include_role:
    name: common
    tasks_from: azure_verify_prerequisites
  vars:
    target_subscription_id: "12345678-1234-1234-1234-123456789012"
    target_resource_group: "my-resource-group"
```

## Adding More Common Tasks

To add new reusable tasks to the common role:

1. Create the task file in `roles/common/tasks/`
2. Add any required defaults to `roles/common/defaults/main.yml`
3. Document the task in `roles/common/README.md`
4. Optionally add to `roles/common/tasks/main.yml` if it should run by default
