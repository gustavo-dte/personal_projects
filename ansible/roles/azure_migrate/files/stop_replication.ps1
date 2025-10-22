#! /usr/bin/env pwsh
# PowerShell script to stop migration replication using Azure Migrate

Param(
  # Required parameters
  [Parameter(Mandatory=$true)][string]$ProjectName,
  [Parameter(Mandatory=$true)][string]$ProjectResourceGroup,
  [Parameter(Mandatory=$true)][string]$ProjectSubscriptionId,
  [Parameter(Mandatory=$true)][string]$MachineName
)

# Import common utilities
$UtilsPath = Join-Path $PSScriptRoot "..\..\common\files\azure_powershell_utils.ps1"
if (Test-Path $UtilsPath) {
  . $UtilsPath
} else {
  Write-Output "ERROR: Common utilities script not found at: $UtilsPath"
  exit 1
}

# Initialize environment and import required modules
Initialize-PowerShellEnvironment
Import-AzureModules -RequiredModules @('Az.Accounts', 'Az.Migrate', 'Az.Resources')
Test-RequiredCmdlets -RequiredCmdlets @('Remove-AzMigrateServerReplication', 'Get-AzMigrateServerReplication')

# Set Azure context
Write-Output "INFO: Setting Azure context to subscription: $ProjectSubscriptionId"
$ProjectSubscriptionId = Set-AzureContext -SubscriptionId $ProjectSubscriptionId

# Log configuration
Write-Output "INFO: Project Name: $ProjectName"
Write-Output "INFO: Project Resource Group: $ProjectResourceGroup"
Write-Output "INFO: Machine Name: $MachineName"

# Results tracking
$Results = @{
  VMName = $MachineName
  Success = $false
  Error = $null
  ReplicationId = $null
  StopTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

try {
  Write-Output "INFO: Resolving replication object for VM '$MachineName'..."

  # Fetch replication object directly by MachineName (pre-check already done in Ansible)
  $TargetReplication = Get-AzMigrateServerReplication -ProjectName $ProjectName -ResourceGroupName $ProjectResourceGroup -MachineName $MachineName -ErrorAction Stop

  if (-not $TargetReplication) {
    Write-Output "INFO: No replication object found for VM '$MachineName' (it may already be stopped)"
    $Results.Success = $true
    $Results.Error = "No active replication found"
    return
  }

  Write-Output "INFO: Stopping replication for VM '$MachineName' (ID: $($TargetReplication.Id))..."

  # Stop the replication
  $stopResult = Remove-AzMigrateServerReplication -InputObject $TargetReplication -Force

  $Results.Success = $true
  $Results.ReplicationId = $TargetReplication.Id

  Write-Output "SUCCESS: Replication stop requested for VM '$MachineName'"
  Write-Output "INFO: Replication ID: $($TargetReplication.Id)"

  if ($stopResult) {
    Write-Output "INFO: Stop replication result:"
    $stopResult | ConvertTo-Json -Depth 6
  }

} catch {
  $errorMessage = $_.Exception.Message
  Write-Output "ERROR: Failed to stop replication for VM '$MachineName': $errorMessage"

  if ($errorMessage -match "not found|does not exist|resource not found|solution not found") {
    # Treat as already stopped
    $Results.Success = $true
    $Results.Error = "Replication not found (may already be stopped)"
  } else {
    $Results.Success = $false
    $Results.Error = $errorMessage
    exit 1
  }
} finally {
  # Output results as JSON for Ansible processing
  $JsonOutput = $Results | ConvertTo-Json -Depth 3

  # Write JSON to a file for Ansible to read
  $OutputFile = "stop_replication_result.json"
  $JsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8

  # Also output to console for debugging
  Write-Output "JSON output written to: $OutputFile"
  Write-Output $JsonOutput
}
