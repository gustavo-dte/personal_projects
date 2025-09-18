# Validate Manifest Action

This action validates that a specified Ansible manifest directory and file exist before running playbooks.

## Features

- ✅ Validates manifest directory exists in `ansible/vars/`
- ✅ Validates `manifest.yml` file exists within the directory
- ✅ Provides clear error messages with available options
- ✅ Returns validated paths as outputs for downstream use
- ✅ User-friendly emoji-based output formatting

## Usage

```yaml
- name: Validate manifest
  uses: ./.github/actions/validate-manifest
  with:
    manifest: phase_1
```

### With custom vars path

```yaml
- name: Validate manifest
  uses: ./.github/actions/validate-manifest
  with:
    manifest: phase_1
    vars_path: custom/vars/path
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `manifest` | Manifest name (directory in ansible/vars/) | Yes | - |
| `vars_path` | Path to vars directory | No | `ansible/vars` |

## Outputs

| Output | Description |
|--------|-------------|
| `manifest_path` | Full path to the validated manifest file |
| `manifest_dir` | Full path to the validated manifest directory |

## Example with outputs

```yaml
- name: Validate manifest
  id: validate
  uses: ./.github/actions/validate-manifest
  with:
    manifest: ${{ inputs.manifest }}

- name: Use validated paths
  run: |
    echo "Manifest file: ${{ steps.validate.outputs.manifest_path }}"
    echo "Manifest directory: ${{ steps.validate.outputs.manifest_dir }}"
```

## Error Handling

The action will fail with a clear error message if:

- The manifest directory doesn't exist (shows available manifests)
- The `manifest.yml` file doesn't exist (shows directory contents)
- The manifest file is not readable

## Example Output

### Success
```
🔍 Validating manifest: phase_1
📁 Looking in directory: ansible/vars/phase_1
✅ Manifest validation successful!
📄 Using manifest file: ansible/vars/phase_1/manifest.yml
```

### Error (directory not found)
```
🔍 Validating manifest: invalid_name
📁 Looking in directory: ansible/vars/invalid_name
❌ ERROR: Manifest directory 'ansible/vars/invalid_name' does not exist

📋 Available manifests:
  - phase_1
  - phase_2
```

### Error (file not found)
```
🔍 Validating manifest: phase_1
📁 Looking in directory: ansible/vars/phase_1
❌ ERROR: Manifest file 'ansible/vars/phase_1/manifest.yml' does not exist

📁 Contents of ansible/vars/phase_1:
  total 8
  -rw-r--r--  1 user  staff  123 Jan 1 12:00 other_file.yml
```
