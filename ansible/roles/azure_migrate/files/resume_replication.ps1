#! /usr/bin/env pwsh
# PowerShell script to resume migration replication using Azure Migrate

Param(
  # Required parameters
  [Parameter(Mandatory=$true)][string]$ProjectName,
  [Parameter(Mandatory=$true)][string]$ProjectResourceGroup,
  [Parameter(Mandatory=$true)][string]$ProjectSubscriptionId,
  [Parameter(Mandatory=$true)][string]$MachineName,
  [Parameter(Mandatory=$true)][string]$ReplicationId
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
Import-AzureModules -RequiredModules @('Az.Accounts', 'Az.Migrate')
Test-RequiredCmdlets -RequiredCmdlets @('Resume-AzMigrateServerReplication', 'Get-AzMigrateServerReplication')

# Set Azure context
Write-Output "INFO: Setting Azure context to subscription: $ProjectSubscriptionId"
Set-AzureContext -SubscriptionId $ProjectSubscriptionId

# Get the replication item using the replication ID
Write-Output "INFO: Retrieving replication item for VM '$MachineName' with ID: $ReplicationId"
try {
  $ReplicationItem = Get-AzMigrateServerReplication -ProjectName $ProjectName -ResourceGroupName $ProjectResourceGroup -MachineName $MachineName -ErrorAction Stop

  if (-not $ReplicationItem) {
    Write-Output "ERROR: Replication item not found for VM '$MachineName'"
    exit 1
  }

  Write-Output "INFO: Found replication item for VM '$MachineName'"
  Write-Output "INFO: Current Replication Status: $($ReplicationItem.ReplicationStatus)"
  Write-Output "INFO: Allowed Operations: $($ReplicationItem.AllowedOperation -join ', ')"

  # Verify ResumeReplication is in allowed operations
  $AllowedOps = @($ReplicationItem.AllowedOperation | ForEach-Object { [string]$_ })
  if (-not ($AllowedOps -contains "ResumeReplication")) {
    Write-Output "ERROR: ResumeReplication is not an allowed operation for VM '$MachineName'"
    Write-Output "INFO: Current allowed operations: $($AllowedOps -join ', ')"
    exit 1
  }

} catch {
  Write-Output "ERROR: Failed to retrieve replication item for VM '$MachineName': $($_.Exception.Message)"
  exit 1
}

# Results tracking
$Results = @{
  VMName = $MachineName
  Success = $false
  Error = $null
  ReplicationId = $ReplicationId
  ResumeTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

try {
  Write-Output "INFO: Resuming replication for VM '$MachineName'..."

  $result = Resume-AzMigrateServerReplication -InputObject $ReplicationItem -Force

  $Results.Success = $true

  Write-Output "SUCCESS: Replication resumed successfully for VM '$MachineName'"
  Write-Output "INFO: Replication ID: $ReplicationId"

  # Output result details
  Write-Output "INFO: Resume replication result:"
  $result | ConvertTo-Json -Depth 6

} catch {
  $errorMessage = $_.Exception.Message
  $Results.Success = $false
  $Results.Error = $errorMessage

  Write-Output "ERROR: Failed to resume replication for VM '$MachineName': $errorMessage"
  exit 1
} finally {
  # Output results as JSON for Ansible processing
  $JsonOutput = $Results | ConvertTo-Json -Depth 3

  # Write JSON to a file for Ansible to read
  $OutputFile = "resume_replication_result.json"
  $JsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8

  # Also output to console for debugging
  Write-Output "JSON output written to: $OutputFile"
  Write-Output $JsonOutput
}
