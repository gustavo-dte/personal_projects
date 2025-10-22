# Enhanced PowerShell script with SQL monitoring support

param(
    [switch]$Detailed,
    [switch]$SqlOnly
)

Write-Host "=== Azure Monitor Deployment Status ===" -ForegroundColor Green
Write-Host ""

try {
    # Test if terraform is available
    $null = Get-Command terraform -ErrorAction Stop

    if (-not $SqlOnly) {
        # Get basic infrastructure outputs
        Write-Host "Getting Infrastructure Status..." -ForegroundColor Cyan

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
    }

    # Get SQL monitoring status
    Write-Host "Getting SQL Monitoring Status..." -ForegroundColor Cyan

    $sqlMonitoringOutput = terraform output -json monitored_sql_servers 2>$null
    if ($LASTEXITCODE -eq 0 -and $sqlMonitoringOutput -and $sqlMonitoringOutput -ne "null") {
        $sqlServers = $sqlMonitoringOutput | ConvertFrom-Json

        Write-Host "SQL Server Monitoring:" -ForegroundColor Yellow

        if ($sqlServers.PSObject.Properties.Count -gt 0) {
            $sqlServers.PSObject.Properties | ForEach-Object {
                $serverName = $_.Name
                $serverInfo = $_.Value

                Write-Host "- SQL Server: $serverName" -ForegroundColor Cyan
                Write-Host "  - Databases: $($serverInfo.databases.count) ($($serverInfo.databases.names -join ', '))"
                Write-Host "  - Features:"
                Write-Host "    - Diagnostic Settings: $($serverInfo.features.diagnostic_settings)"
                Write-Host "    - SQL Insights: $($serverInfo.features.sql_insights)"
                Write-Host "    - Threat Detection: $($serverInfo.features.threat_detection)"
                Write-Host "    - Vulnerability Assessment: $($serverInfo.features.vulnerability_assessment)"
                Write-Host "  - Alerts:"
                Write-Host "    - Server Alerts: $($serverInfo.alerting.server_alerts)"
                Write-Host "    - Database Alerts: $($serverInfo.alerting.database_alerts)"
                Write-Host "    - Total Alerts: $($serverInfo.alerting.total_alerts)"
                Write-Host ""
            }
        } else {
            Write-Host "- No SQL servers currently being monitored"
            Write-Host ""
        }
    } else {
        Write-Host "- SQL monitoring not enabled or no SQL servers configured"
        Write-Host ""
    }

    if ($Detailed) {
        # Get detailed SQL security information
        Write-Host "Getting SQL Security Features..." -ForegroundColor Cyan

        $sqlSecurityOutput = terraform output -json sql_security_features 2>$null
        if ($LASTEXITCODE -eq 0 -and $sqlSecurityOutput -and $sqlSecurityOutput -ne "null") {
            $sqlSecurity = $sqlSecurityOutput | ConvertFrom-Json

            Write-Host "SQL Security Features:" -ForegroundColor Yellow
            $sqlSecurity.PSObject.Properties | ForEach-Object {
                $serverName = $_.Name
                $securityInfo = $_.Value

                Write-Host "- $serverName" -ForegroundColor Cyan
                Write-Host "  - Threat Detection: $($securityInfo.threat_detection)"
                Write-Host "  - Vulnerability Assessment: $($securityInfo.vulnerability_assessment)"
            }
            Write-Host ""
        }

        # Get SQL workbook information
        $sqlWorkbooksOutput = terraform output -json sql_monitoring_workbooks 2>$null
        if ($LASTEXITCODE -eq 0 -and $sqlWorkbooksOutput -and $sqlWorkbooksOutput -ne "null") {
            $sqlWorkbooks = $sqlWorkbooksOutput | ConvertFrom-Json

            Write-Host "SQL Monitoring Workbooks:" -ForegroundColor Yellow
            $sqlWorkbooks.PSObject.Properties | ForEach-Object {
                $serverName = $_.Name
                $workbookId = $_.Value

                if ($workbookId -and $workbookId -ne "null") {
                    $workbookName = ($workbookId -split '/')[-1]
                    Write-Host "- $serverName`: $workbookName"
                }
            }
            Write-Host ""
        }
    }

    if (-not $SqlOnly) {
        # Display VM monitoring (existing functionality)
        $jsonOutput = terraform output -json 2>$null
        if ($LASTEXITCODE -eq 0 -and $jsonOutput) {
            $outputs = $jsonOutput | ConvertFrom-Json

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
        }
    }

    Write-Host "=== Status Check Complete ===" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage Examples:" -ForegroundColor Cyan
    Write-Host "  Show all monitoring:     .\Show-MonitoringStatus-Enhanced.ps1"
    Write-Host "  Show detailed info:      .\Show-MonitoringStatus-Enhanced.ps1 -Detailed"
    Write-Host "  Show SQL monitoring only: .\Show-MonitoringStatus-Enhanced.ps1 -SqlOnly"

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
