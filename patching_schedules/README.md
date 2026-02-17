# Patching Schedules

This folder contains VM patching schedule configurations in JSON format. Each file defines maintenance windows for Azure Update Manager to automatically patch VMs after migration.

## Files

### `testing_vm_patching_schedules.json`
Test configuration for the Testing manifest VMs:
- `vmcuwinwebd02` - Web server, Sunday 2 AM, reboot if required
- `dca-dev7048` - SQL server, Saturday midnight, no reboot

## JSON Format

Each VM requires an entry with the following structure:

```json
{
  "vm-name-lowercase": {
    "maintenance_configuration": "unique-config-name",
    "frequency": "Weekly",
    "day_of_week": "Sunday",
    "time_of_day": "HH:MM",
    "duration": "HH:MM",
    "reboot_setting": "IfRequired|Never|Always",
    "description": "Human-readable description"
  }
}
```

### Field Descriptions

| Field | Type | Values | Example | Description |
|-------|------|--------|---------|-------------|
| `maintenance_configuration` | String | Any unique name | `"weekly-sunday-2am"` | Unique identifier for this maintenance config |
| `frequency` | String | `"Weekly"` | `"Weekly"` | Patching frequency (only Weekly supported) |
| `day_of_week` | String | Monday-Sunday | `"Sunday"` | Day of week to perform patching |
| `time_of_day` | String | HH:MM (24h) | `"02:00"` | Start time in UTC (24-hour format) |
| `duration` | String | HH:MM | `"03:00"` | Maintenance window duration |
| `reboot_setting` | String | IfRequired, Never, Always | `"IfRequired"` | VM reboot behavior after patching |
| `description` | String | Any text | `"Web server..."` | Description for documentation |

## Usage

### In GitHub Actions Workflow

```yaml
inputs:
  manifest: "Testing"
  patching_schedules_file: "patching_schedules/testing_vm_patching_schedules.json"
```

### In Ansible Playbook

```bash
ansible-playbook ansible/playbooks/migration-cutover.yml \
  -e "manifest=Testing" \
  -e "patching_schedules_file=$PWD/patching_schedules/testing_vm_patching_schedules.json"
```

## Creating New Schedules

1. Copy `testing_vm_patching_schedules.json` as a template
2. Update VM names to match your manifest VMs (use lowercase)
3. Configure maintenance windows based on your requirements
4. Ensure schedules don't conflict with business hours or SLAs
5. Test with dry-run mode first

## Best Practices

### Timing Considerations
- **Production VMs**: Weekend or off-hours (e.g., Saturday/Sunday 2-4 AM)
- **Development VMs**: Any time (e.g., Wednesday 10 AM)
- **Database Servers**: Low-traffic windows with longer duration
- **Web Servers**: Load-balanced, rotate patching windows

### Reboot Settings
- **IfRequired** (Recommended): Reboots only if patches require it
- **Never**: For VMs that can't afford downtime (use with caution)
- **Always**: For VMs where you want guaranteed clean state

### Duration Guidelines
- **Standard VMs**: 2-3 hours
- **Large/Complex VMs**: 4+ hours
- **No-reboot VMs**: 1-2 hours

## Example Schedules

### Production Web Farm (Staggered)
```json
{
  "webvm01": {
    "maintenance_configuration": "prod-web-sun-2am",
    "frequency": "Weekly",
    "day_of_week": "Sunday",
    "time_of_day": "02:00",
    "duration": "03:00",
    "reboot_setting": "IfRequired",
    "description": "Production web server - Sunday early morning"
  },
  "webvm02": {
    "maintenance_configuration": "prod-web-sun-6am",
    "frequency": "Weekly",
    "day_of_week": "Sunday",
    "time_of_day": "06:00",
    "duration": "03:00",
    "reboot_setting": "IfRequired",
    "description": "Production web server - Sunday morning (staggered 4h from webvm01)"
  }
}
```

### Database Cluster (Coordinated)
```json
{
  "sqlvm01": {
    "maintenance_configuration": "db-sat-midnight",
    "frequency": "Weekly",
    "day_of_week": "Saturday",
    "time_of_day": "00:00",
    "duration": "04:00",
    "reboot_setting": "Never",
    "description": "SQL primary - Saturday midnight, no reboot to avoid failover"
  },
  "sqlvm02": {
    "maintenance_configuration": "db-fri-midnight",
    "frequency": "Weekly",
    "day_of_week": "Friday",
    "time_of_day": "00:00",
    "duration": "04:00",
    "reboot_setting": "IfRequired",
    "description": "SQL secondary - Friday midnight, can reboot (24h before primary)"
  }
}
```

### Development/Test Environment
```json
{
  "devvm01": {
    "maintenance_configuration": "dev-wed-morning",
    "frequency": "Weekly",
    "day_of_week": "Wednesday",
    "time_of_day": "10:00",
    "duration": "02:00",
    "reboot_setting": "Always",
    "description": "Dev VM - Wednesday morning, always reboot for clean state"
  }
}
```

## Validation

Before using in production:

1. **VM Name Match**: Ensure all manifest VMs have entries (case-sensitive, use lowercase)
2. **No Time Conflicts**: Stagger windows for high-availability setups
3. **Business Hours**: Avoid patching during business hours for production
4. **Test First**: Use dry-run mode to validate configuration
5. **Azure Portal**: Verify configurations appear correctly after deployment

## Troubleshooting

### VM Not Getting Patched
- Check VM name matches exactly (lowercase in JSON)
- Verify maintenance configuration exists in Azure
- Check VM assignment to configuration
- Ensure patch mode is `AutomaticByPlatform`

### Schedule Not Applied
- Validate JSON syntax (use JSON linter)
- Check file path in workflow/playbook is correct
- Review workflow logs for errors

### Wrong Time Zone
- All times are in **UTC**
- Convert local times to UTC before setting `time_of_day`
- Example: EST (UTC-5) → 2 AM EST = 07:00 UTC

## Reference

For more information on Azure Update Manager and maintenance configurations:
- [Azure Update Manager Documentation](https://learn.microsoft.com/en-us/azure/update-manager/)
- [Maintenance Configurations](https://learn.microsoft.com/en-us/azure/virtual-machines/maintenance-configurations)
- [Patch Orchestration Modes](https://learn.microsoft.com/en-us/azure/update-manager/overview#patch-orchestration)
