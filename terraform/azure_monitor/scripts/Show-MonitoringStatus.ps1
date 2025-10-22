# Simplified PowerShell script to display monitoring status

param(
    [switch]$Detailed
)

Write-Host "=== Azure Monitor Deployment Status ===" -ForegroundColor Green
Write-Host ""

try {
    # Test if terraform is available
    $null = Get-Command terraform -ErrorAction Stop

    # Get basic outputs
    Write-Host "Getting Terraform outputs..." -ForegroundColor Cyan

    $resourceGroup = terraform output -raw resource_group_name 2>$null
    $workspaceId = terraform output -raw log_analytics_workspace_id 2>$null
    $appInsightsId = terraform output -raw application_insights_id 2>$null
    $actionGroupId = terraform output -raw action_group_id 2>$null

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Infrastructure Components:" -ForegroundColor Yellow
        Write-Host "- Resource Group: $resourceGroup"

        if ($workspaceId) {
            $workspaceName = ($workspaceId -split '/')[-1]
            Write-Host "- Log Analytics Workspace: $workspaceName"
        }

        if ($appInsightsId) {
            $appInsightsName = ($appInsightsId -split '/')[-1]
            Write-Host "- Application Insights: $appInsightsName"
        }

        if ($actionGroupId) {
            $actionGroupName = ($actionGroupId -split '/')[-1]
            Write-Host "- Action Group: $actionGroupName"
        }
        Write-Host ""
    }

    if ($Detailed) {
        # Get detailed JSON output for complex structures
        Write-Host "Getting detailed monitoring information..." -ForegroundColor Cyan

        $jsonOutput = terraform output -json 2>$null
        if ($LASTEXITCODE -eq 0 -and $jsonOutput) {
            $outputs = $jsonOutput | ConvertFrom-Json

            # Display VM monitoring status
            Write-Host "Virtual Machine Monitoring:" -ForegroundColor Yellow

            # Windows VMs
            if ($outputs.monitored_windows_vms -and $outputs.monitored_windows_vms.value) {
                $windowsVMs = $outputs.monitored_windows_vms.value
                if ($windowsVMs.PSObject.Properties) {
                    Write-Host "Windows VMs:" -ForegroundColor Cyan
                    $windowsVMs.PSObject.Properties | ForEach-Object {
                        Write-Host "  - $($_.Name): Monitoring Enabled = $($_.Value.monitoring_enabled)"
                    }
                }
            }

            # Linux VMs
            if ($outputs.monitored_linux_vms -and $outputs.monitored_linux_vms.value) {
                $linuxVMs = $outputs.monitored_linux_vms.value
                if ($linuxVMs.PSObject.Properties) {
                    Write-Host "Linux VMs:" -ForegroundColor Cyan
                    $linuxVMs.PSObject.Properties | ForEach-Object {
                        Write-Host "  - $($_.Name): Monitoring Enabled = $($_.Value.monitoring_enabled)"
                    }
                }
            }
            Write-Host ""

            # Alert summary
            if ($outputs.monitoring_summary -and $outputs.monitoring_summary.value) {
                $summary = $outputs.monitoring_summary.value
                Write-Host "Monitoring Summary:" -ForegroundColor Yellow

                if ($summary.alerting) {
                    Write-Host "- Alert Rules: $($summary.alerting.total_alert_rules)"
                    Write-Host "- Notification Email: $($summary.alerting.notification_email)"
                }

                if ($summary.features_enabled) {
                    Write-Host "- VM Insights: $($summary.features_enabled.vm_insights)"
                    Write-Host "- Dependency Agent: $($summary.features_enabled.dependency_agent)"
                    Write-Host "- Azure Monitor Agent: $($summary.features_enabled.azure_monitor_agent)"
                }
                Write-Host ""
            }
        }
    }

    Write-Host "=== Status Check Complete ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "To see detailed information, run:" -ForegroundColor Cyan
    Write-Host "  .\Show-MonitoringStatus-Simple.ps1 -Detailed"

} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting steps:" -ForegroundColor Yellow
    Write-Host "1. Ensure Terraform is installed: terraform --version"
    Write-Host "2. Ensure you're in the correct directory"
    Write-Host "3. Check if Terraform state exists: ls terraform.tfstate"
    Write-Host "4. Try running: terraform output"
    exit 1
}
