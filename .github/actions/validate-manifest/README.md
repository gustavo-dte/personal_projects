# Validate Manifest Action

Validates Ansible manifest directory and file exist with security protections against path traversal attacks.

## Usage

```yaml
- name: Validate manifest
  uses: ./.github/actions/validate-manifest
  with:
    manifest: phase_1
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `manifest` | Manifest name (alphanumeric, hyphens, underscores only) | Yes | - |
| `vars_path` | Path to vars directory | No | `ansible/vars` |

## Outputs

| Output | Description |
|--------|-------------|
| `manifest_path` | Full path to validated manifest file |
| `manifest_dir` | Full path to validated manifest directory |

## Security

- **Input Validation**: Only allows safe characters (`a-zA-Z0-9_-`)
- **Path Traversal Protection**: Prevents `../` attacks
- **Length Limits**: Maximum 50 characters
- **Boundary Checking**: Ensures paths stay within vars directory

## Error Examples

**Invalid characters:**
```
❌ ERROR: Invalid manifest name. Use only alphanumeric characters, hyphens, and underscores (max 50 chars).
   Provided: 'phase;rm -rf /'
```

**Directory not found:**
```
❌ ERROR: Manifest directory 'ansible/vars/invalid_name' does not exist
📋 Available manifests:
  - phase_1
  - phase_2
```
