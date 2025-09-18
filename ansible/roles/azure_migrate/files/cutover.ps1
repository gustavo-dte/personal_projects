#! /usr/bin/env pwsh
# PowerShell script to perform migration cutover using Azure Migrate
# Based on existing replication patterns in this repository

Param(
  # Required parameters
  [Parameter(Mandatory=$true)][string]$ProjectName,
  [Parameter(Mandatory=$true)][string]$ProjectResourceGroup,
  [Parameter(Mandatory=$true)][string]$MachineName,

  # Optional parameters
  [Parameter(Mandatory=$false)][string]$SubscriptionId,
  [Parameter(Mandatory=$false)][switch]$ShutdownSourceVM = $false,
  [Parameter(Mandatory=$false)][string]$TargetVMName
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
Test-RequiredCmdlets -RequiredCmdlets @('Get-AzMigrateServerReplication', 'Start-AzMigrateServerMigration')

# Set Azure context
$SubscriptionId = Set-AzureContext -SubscriptionId $SubscriptionId

# Log cutover parameters
Write-Output "INFO: Starting cutover operation"
Write-Output "  - Project: $ProjectName"
Write-Output "  - Resource Group: $ProjectResourceGroup"
Write-Output "  - Machine: $MachineName"
if ($TargetVMName) {
  Write-Output "  - Target VM: $TargetVMName"
}
Write-Output "  - Shutdown Source: $ShutdownSourceVM"
Write-Output "  - Subscription: $SubscriptionId"

# Get the replicating machine to verify replication status
try {
  Write-Output "INFO: Looking for replicating machine '$MachineName'"
  $ReplicatingServers = Get-AzMigrateServerReplication -ProjectName $ProjectName -ResourceGroupName $ProjectResourceGroup
  
  if (-not $ReplicatingServers -or $ReplicatingServers.Count -eq 0) {
    Write-Output "ERROR: No replicating servers found in project '$ProjectName'"
    exit 1
  }

  # Find the replicating server by machine name
  $ReplicatingServer = $ReplicatingServers | Where-Object { 
    $_.SourceServerName -eq $MachineName -or 
    $_.MachineName -eq $MachineName -or
    $_.Name -eq $MachineName
  } | Select-Object -First 1

  if (-not $ReplicatingServer) {
    Write-Output "ERROR: Replicating server '$MachineName' not found"
    Write-Output "INFO: Available servers:"
    $ReplicatingServers | ForEach-Object {
      Write-Output "  - $($_.Name) (Source: $($_.SourceServerName))"
    }
    exit 1
  }

  Write-Output "INFO: Found server: $($ReplicatingServer.Name)"
  Write-Output "INFO: Migration state: $($ReplicatingServer.MigrationState)"
  Write-Output "INFO: Replication health: $($ReplicatingServer.ReplicationHealth)"

} catch {
  Write-Output "ERROR: Failed to get replicating servers: $($_.Exception.Message)"
  exit 1
}

# Validate replication status
if ($ReplicatingServer.MigrationState -eq "None") {
  Write-Output "ERROR: VM '$MachineName' is not ready for cutover"
  Write-Output "INFO: Current state: $($ReplicatingServer.MigrationState)"
  Write-Output "INFO: Replication must be active before cutover"
  exit 1
}

if ($ReplicatingServer.ReplicationHealth -eq "Critical") {
  Write-Output "WARNING: VM has critical replication health"
  Write-Output "INFO: Current health: $($ReplicatingServer.ReplicationHealth)"
  Write-Output "INFO: Review replication status before proceeding"
}

# Check if already migrated
if ($ReplicatingServer.MigrationState -in @("MigrationSucceeded", "MigrationFailed")) {
  Write-Output "INFO: Migration already attempted for '$MachineName'"
  Write-Output "INFO: State: $($ReplicatingServer.MigrationState)"
  
  if ($ReplicatingServer.MigrationState -eq "MigrationSucceeded") {
    Write-Output "INFO: Migration completed successfully"
    # Return success for idempotency
    $result = @{
      Status = "AlreadyCompleted"
      MigrationState = $ReplicatingServer.MigrationState
      Message = "Migration already completed"
      TargetVMName = $ReplicatingServer.TargetVMName
    }
    $result | ConvertTo-Json -Depth 3
    exit 0
  } else {
    Write-Output "WARNING: Previous migration failed, will retry"
  }
}

# Perform the cutover
try {
  Write-Output "INFO: Starting cutover for '$MachineName'"
  
  # Prepare migration parameters
  $migrationParams = @{
    InputObject = $ReplicatingServer
  }
  
  if ($ShutdownSourceVM) {
    $migrationParams['TurnOffSourceServer'] = $true
    Write-Output "INFO: Source VM will be shut down"
  } else {
    Write-Output "INFO: Source VM will remain running"
  }

  # Start the migration
  Write-Output "INFO: Initiating migration..."
  $MigrationResult = Start-AzMigrateServerMigration @migrationParams
  
  if ($MigrationResult) {
    Write-Output "INFO: Cutover initiated successfully"
    Write-Output "INFO: Job ID: $($MigrationResult.JobId)"
    
    $targetName = $MigrationResult.TargetVMName
    if (-not $targetName) {
      $targetName = $ReplicatingServer.TargetVMName
    }
    Write-Output "INFO: Target VM: $targetName"
    
    # Return result
    $result = @{
      Status = "Initiated"
      JobId = $MigrationResult.JobId
      TargetVMName = $targetName
      MigrationState = "MigrationInProgress"
      Message = "Cutover initiated successfully"
      ShutdownSourceVM = $ShutdownSourceVM
    }
    
    $result | ConvertTo-Json -Depth 3
  } else {
    Write-Output "ERROR: Cutover failed - no result returned"
    exit 1
  }

} catch {
  Write-Output "ERROR: Cutover failed for '$MachineName'"
  Write-Output "ERROR: $($_.Exception.Message)"
  
  $errorResult = @{
    Status = "Failed"
    Error = $_.Exception.Message
    MigrationState = $ReplicatingServer.MigrationState
    Message = "Cutover operation failed"
  }
  
  $errorResult | ConvertTo-Json -Depth 3
  exit 1
}