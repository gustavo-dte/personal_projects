#! /usr/bin/env pwsh
# PowerShell script to check Azure Migrate replication status for VMs

Param(
  [Parameter(Mandatory=$true)][string]$ProjectName,
  [Parameter(Mandatory=$true)][string]$ProjectResourceGroup,
  [Parameter(Mandatory=$true)][string]$VMNamesJson,  # JSON array of VM names from manifest
  [Parameter(Mandatory=$false)][int]$ReplicationThreshold = 80,
  [Parameter(Mandatory=$false)][string]$SubscriptionId
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
Test-RequiredCmdlets -RequiredCmdlets @('Get-AzMigrateServerReplication')

# Set Azure context
Write-Output "INFO: Setting Azure context to subscription: $SubscriptionId"
$SubscriptionId = Set-AzureContext -SubscriptionId $SubscriptionId

# Parse VM name from JSON (expecting a single VM per call)
try {
  $VMNames = $VMNamesJson | ConvertFrom-Json
  $VMName = $null
  if ($VMNames -is [System.Array]) {
    if ($VMNames.Count -gt 0) { $VMName = $VMNames[0] }
  } else {
    $VMName = [string]$VMNames
  }
  if (-not $VMName) {
    Write-Output "ERROR: No VM name provided."
    exit 1
  }
} catch {
  Write-Output "ERROR: Failed to parse VM names JSON: $VMNamesJson"
  exit 1
}

Write-Output "INFO: Checking Azure Migrate replication status for VM '$VMName'..."

# Result tracking (single object)
$Result = $null

try {
  # Get replication status for the VM
  $Response = Get-AzMigrateServerReplication -ProjectName $ProjectName -ResourceGroupName $ProjectResourceGroup -MachineName $VMName -ErrorAction Stop

  Write-Output "INFO: Replication status for VM '$VMName':"
  Write-Output "  - ReplicationStatus: $($Response.ReplicationStatus)"
  Write-Output "  - MigrationState: $($Response.MigrationState)"
  Write-Output "  - MigrationStateDescription: $($Response.MigrationStateDescription)"
  Write-Output "  - CurrentJobName: $($Response.CurrentJobName)"
  Write-Output "  - TargetVMName: $($Response.TargetVMName)"
  Write-Output "  - AllowedOperations: $($Response.AllowedOperation -join ', ')"

  if (-not $Response) {
    Write-Output "INFO: No replication found for VM '$VMName' in project '$ProjectName' - treating as 0% replication"
    $Result = @{
      VMName = $VMName
      ReplicationStatus = "Not Found"
      ReplicationPercentage = 0
      Error = $null
    }
  } else {
    # Extract replication percentage/state - try different property names based on Az.Migrate version
    $ReplicationPercentage = 0 # Currently not supported by the API

    if ($Response.ReplicationStatus) {
      $ReplicationStatus = $Response.ReplicationStatus
    } else {
      $ReplicationStatus = "Unknown"
    }

    # Extract replication ID (TargetObjectID)
    $ReplicationId = $null
    if ($Response.Id) {
      $ReplicationId = $Response.Id
    }

    # Extract AllowedOperation as strings for reliable JSON parsing
    $AllowedOperationStrings = @()
    if ($Response.AllowedOperation) {
      $AllowedOperationStrings = @($Response.AllowedOperation | ForEach-Object { [string]$_ })
    }

    # Extract LastTestMigrationStatus
    $LastTestMigrationStatus = $null
    if ($Response.LastTestMigrationStatus) {
      $LastTestMigrationStatus = $Response.LastTestMigrationStatus
    }

    # Extract LastTestMigrationTime
    $LastTestMigrationTime = $null
    if ($Response.LastTestMigrationTime) {
      $LastTestMigrationTime = $Response.LastTestMigrationTime
    }

    # Extract TestMigrateState and Description as strings
    $TestMigrateStateString = ""
    if ($Response.TestMigrateState) {
      $TestMigrateStateString = [string]$Response.TestMigrateState
    } else {
      $TestMigrateStateString = "None"
    }

    $TestMigrateStateDescriptionString = ""
    if ($Response.TestMigrateStateDescription) {
      $TestMigrateStateDescriptionString = [string]$Response.TestMigrateStateDescription
    } else {
      $TestMigrateStateDescriptionString = "None"
    }

    # Extract MigrationState and Description (CRITICAL for skip logic)
    $MigrationStateString = ""
    if ($Response.MigrationState) {
      $MigrationStateString = [string]$Response.MigrationState
    } else {
      $MigrationStateString = "Unknown"
    }

    $MigrationStateDescriptionString = ""
    if ($Response.MigrationStateDescription) {
      $MigrationStateDescriptionString = [string]$Response.MigrationStateDescription
    } else {
      $MigrationStateDescriptionString = "Unknown"
    }

    # Extract CurrentJobName for planned failover detection
    $CurrentJobNameString = ""
    if ($Response.CurrentJobName) {
      $CurrentJobNameString = [string]$Response.CurrentJobName
    } else {
      $CurrentJobNameString = "None"
    }

    # Extract TargetVMName for reference
    $TargetVMNameString = ""
    if ($Response.TargetVMName) {
      $TargetVMNameString = [string]$Response.TargetVMName
    } else {
      $TargetVMNameString = "Unknown"
    }

    $Result = @{
      VMName = $VMName
      ReplicationStatus = $ReplicationStatus
      ReplicationPercentage = $ReplicationPercentage
      ReplicationId = $ReplicationId
      AllowedOperationStrings = $AllowedOperationStrings
      LastTestMigrationStatus = $LastTestMigrationStatus
      LastTestMigrationTime = $LastTestMigrationTime
      TestMigrateStateString = $TestMigrateStateString
      TestMigrateStateDescriptionString = $TestMigrateStateDescriptionString
      MigrationState = $MigrationStateString
      MigrationStateDescription = $MigrationStateDescriptionString
      CurrentJobName = $CurrentJobNameString
      TargetVMName = $TargetVMNameString
      Error = $null
    }
  }

} catch {
  $ErrorMessage = $_.Exception.Message

  if ($ErrorMessage -match "not found|does not exist|not available|service not found|resource not found|solution not found" -or
      $_.Exception.GetType().Name -match "ResourceNotFound|ServiceNotFound") {
    Write-Output "INFO: No replication found for VM '$VMName' - treating as 0% replication"
    $Result = @{
      VMName = $VMName
      ReplicationStatus = "Not Found"
      ReplicationPercentage = 0
      Error = $null
    }
  } else {
    Write-Output "ERROR: Failed to get replication status for VM '$VMName': $ErrorMessage"
    $Result = @{
      VMName = $VMName
      ReplicationStatus = "Error"
      ReplicationPercentage = 0
      Error = $ErrorMessage
    }
  }
}

# Output summary (single VM)
Write-Output ""
Write-Output "=== AZURE MIGRATE REPLICATION STATUS ==="
Write-Output "VM checked: $VMName"
Write-Output ""

# Output detailed result as JSON for Ansible processing (single object)
$JsonOutput = $Result | ConvertTo-Json -Depth 3

# Write JSON to a file for Ansible to read
$OutputFile = "get_replication_status_result.json"
$JsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8

# Also output to console for debugging
Write-Output "JSON output written to: $OutputFile"
Write-Output $JsonOutput
