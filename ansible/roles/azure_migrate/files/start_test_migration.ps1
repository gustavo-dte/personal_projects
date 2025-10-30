#! /usr/bin/env pwsh
# PowerShell script to start test migration using Azure Migrate

Param(
  # Required parameters
  [Parameter(Mandatory=$true)][string]$ProjectName,
  [Parameter(Mandatory=$true)][string]$ProjectResourceGroup,
  [Parameter(Mandatory=$true)][string]$ProjectSubscriptionId,
  [Parameter(Mandatory=$true)][string]$MachineName,
  [Parameter(Mandatory=$true)][string]$TargetObjectId,
  [Parameter(Mandatory=$true)][string]$TestNetworkId
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
Test-RequiredCmdlets -RequiredCmdlets @('Start-AzMigrateTestMigration')

# Set Azure context
Write-Output "INFO: Setting Azure context to subscription: $ProjectSubscriptionId"
$ProjectSubscriptionId = Set-AzureContext -SubscriptionId $ProjectSubscriptionId

Write-Output "INFO: Starting test migration for VM '$MachineName'..."

# Results tracking
$Results = @{
  VMName = $MachineName
  Success = $false
  Error = $null
  JobId = $null
  TestMigrationId = $null
  StartTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

try {
  # Start test migration using the TargetObjectID method
  Write-Output "INFO: Starting test migration with parameters:"
  Write-Output "  - TargetObjectId: $TargetObjectId"
  Write-Output "  - TestNetworkId: $TestNetworkId"

  $TestMigrationJob = Start-AzMigrateTestMigration `
    -TargetObjectID $TargetObjectId `
    -TestNetworkID $TestNetworkId `
    -ErrorAction Stop

  # Extract job ID from result
  if ($TestMigrationJob.Id) {
    $Results.JobId = $TestMigrationJob.Id
  }
  if ($TestMigrationJob.Name) {
    $Results.TestMigrationId = $TestMigrationJob.Name
  }

  $Results.Success = $true
  Write-Output "SUCCESS: Test migration started successfully for VM '$MachineName'"
  Write-Output "INFO: Test migration job ID: $Results.JobId"

} catch {
  $errorMessage = $_.Exception.Message
  $Results.Success = $false
  $Results.Error = $errorMessage

  Write-Output "ERROR: Failed to start test migration for VM '$MachineName': $errorMessage"
  exit 1
} finally {
  # Output results as JSON for Ansible processing
  $JsonOutput = $Results | ConvertTo-Json -Depth 3

  # Write JSON to a file for Ansible to read
  $OutputFile = "start_test_migration_result.json"
  $JsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8

  # Also output to console for debugging
  Write-Output "JSON output written to: $OutputFile"
  Write-Output $JsonOutput
}
