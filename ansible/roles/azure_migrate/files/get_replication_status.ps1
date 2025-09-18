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
$SubscriptionId = Set-AzureContext -SubscriptionId $SubscriptionId

# Parse VM names from JSON
try {
  $VMNames = $VMNamesJson | ConvertFrom-Json
  if (-not $VMNames -or $VMNames.Count -eq 0) {
    Write-Output "ERROR: No VM names provided in manifest."
    exit 1
  }
} catch {
  Write-Output "ERROR: Failed to parse VM names JSON: $VMNamesJson"
  exit 1
}

Write-Output "INFO: Checking Azure Migrate replication status for $($VMNames.Count) VMs..."

# Results tracking
$Results = @()
$VmsAboveThreshold = 0
$VmsBelowThreshold = 0
$VmsWithErrors = 0

# Check replication status for each VM
foreach ($VMName in $VMNames) {
  Write-Output "INFO: Checking replication status for VM '$VMName'..."

  try {
    # Get replication status for the VM
    $ReplicationStatus = Get-AzMigrateServerReplication -ProjectName $ProjectName -ResourceGroupName $ProjectResourceGroup -MachineName $VMName -ErrorAction SilentlyContinue

    if (-not $ReplicationStatus) {
      Write-Output "WARNING: No replication status found for VM '$VMName' in project '$ProjectName'"
      $Results += @{
        VMName = $VMName
        ReplicationStatus = "Not Found"
        ReplicationPercentage = 0
        MeetsThreshold = $false
        Error = "No replication status found"
      }
      $VmsWithErrors++
      continue
    }

    # Extract replication percentage - try different property names based on Az.Migrate version
    $ReplicationPercentage = 0
    $ReplicationState = "Unknown"

    if ($ReplicationStatus.MigrationState) {
      $ReplicationState = $ReplicationStatus.MigrationState.MigrationState
      if ($ReplicationStatus.MigrationState.PercentComplete) {
        $ReplicationPercentage = $ReplicationStatus.MigrationState.PercentComplete
      }
    } elseif ($ReplicationStatus.PercentComplete) {
      $ReplicationPercentage = $ReplicationStatus.PercentComplete
      $ReplicationState = $ReplicationStatus.MigrationState
    } elseif ($ReplicationStatus.ReplicationPercentage) {
      $ReplicationPercentage = $ReplicationStatus.ReplicationPercentage
      $ReplicationState = $ReplicationStatus.ReplicationState
    } else {
      # Try to extract from properties if available
      if ($ReplicationStatus.Properties -and $ReplicationStatus.Properties.MigrationState) {
        $ReplicationState = $ReplicationStatus.Properties.MigrationState.MigrationState
        $ReplicationPercentage = $ReplicationStatus.Properties.MigrationState.PercentComplete
      }
    }

    # Ensure percentage is a number
    if ($ReplicationPercentage -is [string]) {
      $ReplicationPercentage = [int]($ReplicationPercentage -replace '%', '')
    }

    $MeetsThreshold = $ReplicationPercentage -ge $ReplicationThreshold

    if ($MeetsThreshold) {
      Write-Output "SUCCESS: VM '$VMName' meets threshold with $ReplicationPercentage% replication (>= $ReplicationThreshold%)"
      $VmsAboveThreshold++
    } else {
      Write-Output "INFO: VM '$VMName' below threshold with $ReplicationPercentage% replication (< $ReplicationThreshold%)"
      $VmsBelowThreshold++
    }

    $Results += @{
      VMName = $VMName
      ReplicationStatus = $ReplicationState
      ReplicationPercentage = $ReplicationPercentage
      MeetsThreshold = $MeetsThreshold
      Error = $null
    }

  } catch {
    Write-Output "ERROR: Failed to get replication status for VM '$VMName': $($_.Exception.Message)"
    $Results += @{
      VMName = $VMName
      ReplicationStatus = "Error"
      ReplicationPercentage = 0
      MeetsThreshold = $false
      Error = $_.Exception.Message
    }
    $VmsWithErrors++
  }
}

# Output summary
Write-Output ""
Write-Output "=== AZURE MIGRATE REPLICATION STATUS SUMMARY ==="
Write-Output "Total VMs checked: $($VMNames.Count)"
Write-Output "VMs above threshold ($ReplicationThreshold%): $VmsAboveThreshold"
Write-Output "VMs below threshold ($ReplicationThreshold%): $VmsBelowThreshold"
Write-Output "VMs with errors: $VmsWithErrors"
Write-Output ""

# Output detailed results as JSON for Ansible processing
$Results | ConvertTo-Json -Depth 3
