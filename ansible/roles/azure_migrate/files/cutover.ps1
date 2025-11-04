#! /usr/bin/env pwsh
#Requires -Version 7.0
#Requires -Modules Az.Accounts, Az.Migrate, Az.Resources

# PowerShell script to perform migration cutover using Azure Migrate
# Based on existing replication patterns in this repository

[CmdletBinding(SupportsShouldProcess=$true)]
Param(
    # Required parameters
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$ProjectName,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$ProjectResourceGroup,

    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$MachineName,

    # Optional parameters
    [Parameter()]
    [ValidatePattern('^[0-9a-fA-F-]{36}$', ErrorMessage = 'SubscriptionId must be a valid GUID (00000000-0000-0000-0000-000000000000 format)')]
    [string]$SubscriptionId,

    [Parameter()]
    [switch]$ShutdownSourceVM,
  [Parameter(Mandatory=$false)][string]$TargetVMName
)

# Set strict mode and error handling preferences
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$InformationPreference = 'Continue'

# Import common utilities
$UtilsPath = Join-Path $PSScriptRoot "..\..\common\files\azure_powershell_utils.ps1"
if (Test-Path $UtilsPath) {
    . $UtilsPath
} else {
    Write-Error "Common utilities script not found at: $UtilsPath" -ErrorAction Stop
  exit 1
}

# Initialize environment and import required modules
Initialize-PowerShellEnvironment
Import-AzureModules -RequiredModules @('Az.Accounts', 'Az.Migrate', 'Az.Resources')
Test-RequiredCmdlets -RequiredCmdlets @('Get-AzMigrateServerReplication', 'Start-AzMigrateServerMigration')

# Set Azure context
$AzureSubscriptionId = Set-AzureContext -SubscriptionId $SubscriptionId
Set-AzureContext -SubscriptionId $AzureSubscriptionId | Out-Null
# Log cutover parameters
Write-Output "Starting cutover operation"
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

  # Convert to array to ensure consistent handling of single or multiple results
  $ReplicatingServersArray = @($ReplicatingServers)
  
  if (-not $ReplicatingServers -or $ReplicatingServersArray.Count -eq 0) {
    Write-Output "ERROR: No replicating servers found in project '$ProjectName'"
    
    # Output error result in JSON format for Ansible parsing
    $errorResult = @{
      Status = "Failed"
      Error = "No replicating servers found in project '$ProjectName'"
      MigrationState = "Unknown"
      Message = "No machines are currently replicating in this project"
    }
    
    $errorResult | ConvertTo-Json -Depth 3
    exit 1
  }

  # Debug: Show what properties are actually available
  Write-Output "INFO: Retrieved $($ReplicatingServersArray.Count) replicating server(s)"
  if ($ReplicatingServersArray.Count -gt 0) {
    $firstServer = $ReplicatingServersArray[0]
    $availableProperties = $firstServer | Get-Member -MemberType Properties | Select-Object -ExpandProperty Name
    Write-Output "INFO: Available properties on server objects: $($availableProperties -join ', ')"
  }

  # Find the replicating server by machine name using flexible property matching
  $ReplicatingServer = $ReplicatingServersArray | Where-Object {
    # Try different possible property names for source server identification
    $serverIdentifiers = @()
    
    # Collect all possible identifier properties
    if ($_.PSObject.Properties['SourceServerName']) { $serverIdentifiers += $_.SourceServerName }
    if ($_.PSObject.Properties['MachineName']) { $serverIdentifiers += $_.MachineName }
    if ($_.PSObject.Properties['Name']) { $serverIdentifiers += $_.Name }
    if ($_.PSObject.Properties['DisplayName']) { $serverIdentifiers += $_.DisplayName }
    if ($_.PSObject.Properties['FriendlyName']) { $serverIdentifiers += $_.FriendlyName }
    if ($_.PSObject.Properties['ServerName']) { $serverIdentifiers += $_.ServerName }
    
    # Check if any identifier matches our target machine name
    $serverIdentifiers -contains $MachineName
  } | Select-Object -First 1

  if (-not $ReplicatingServer) {
    Write-Output "ERROR: Replicating server '$MachineName' not found"
    Write-Output "Available servers:"
    $ReplicatingServersArray | ForEach-Object {
      # Use defensive property access for display
      $name = if ($_.PSObject.Properties['Name']) { $_.Name } else { 'N/A' }
      $sourceName = if ($_.PSObject.Properties['SourceServerName']) { $_.SourceServerName } 
                    elseif ($_.PSObject.Properties['MachineName']) { $_.MachineName }
                    elseif ($_.PSObject.Properties['DisplayName']) { $_.DisplayName }
                    else { 'N/A' }
      $state = if ($_.PSObject.Properties['MigrationState']) { $_.MigrationState } else { 'N/A' }
      $health = if ($_.PSObject.Properties['ReplicationHealth']) { $_.ReplicationHealth } else { 'N/A' }
      
      Write-Output ("  - {0} (Source: {1}, State: {2}, Health: {3})" -f $name, $sourceName, $state, $health)
    }
    
    # Output error result in JSON format for Ansible parsing
    $errorResult = @{
      Status = "Failed"
      Error = "Replicating server '$MachineName' not found in project '$ProjectName'"
      MigrationState = "Unknown"
      Message = "Machine not found in replication list"
      AvailableServers = $ReplicatingServersArray | ForEach-Object { $_.Name }
    }
    
    $errorResult | ConvertTo-Json -Depth 3
    exit 1
  }

  # Display found server info using defensive property access
  $serverName = if ($ReplicatingServer.PSObject.Properties['Name']) { $ReplicatingServer.Name } else { 'N/A' }
  $migrationState = if ($ReplicatingServer.PSObject.Properties['MigrationState']) { [string]$ReplicatingServer.MigrationState } else { 'Unknown' }
  $replicationHealth = if ($ReplicatingServer.PSObject.Properties['ReplicationHealth']) { [string]$ReplicatingServer.ReplicationHealth } else { 'Unknown' }
  
  Write-Output "INFO: Found server: $serverName"
  Write-Output "INFO: Migration state: $migrationState"
  Write-Output "INFO: Replication health: $replicationHealth"

} catch {
  Write-Output "ERROR: Failed to get replicating servers: $($_.Exception.Message)"
  
  # Output error result in JSON format for Ansible parsing
  $errorResult = @{
    Status = "Failed"
    Error = "Failed to get replicating servers: $($_.Exception.Message)"
    MigrationState = "Unknown"
    Message = "Error retrieving server replication status"
  }
  
  $errorResult | ConvertTo-Json -Depth 3
  exit 1
}

# Validate replication status
if ($migrationState -eq "None") {
  Write-Output "ERROR: VM '$MachineName' is not ready for cutover"
  Write-Output "Current state: $migrationState"
  Write-Output "Replication must be active before cutover"
  
  # Output error result in JSON format for Ansible parsing
  $errorResult = @{
    Status = "Failed"
    Error = "VM '$MachineName' is not ready for cutover"
    MigrationState = $migrationState
    Message = "Replication must be active before cutover"
  }
  
  $errorResult | ConvertTo-Json -Depth 3
  exit 1
}

if ($replicationHealth -eq "Critical") {
  Write-Warning "VM has critical replication health"
  Write-Output "Current health: $replicationHealth"
  Write-Output "Review replication status before proceeding"
}

# Check if already migrated
if ($migrationState -in @("MigrationSucceeded", "MigrationFailed")) {
  Write-Output "INFO: Migration already attempted for '$MachineName'"
  Write-Output "INFO: State: $migrationState"

  if ($migrationState -eq "MigrationSucceeded") {
    Write-Output "INFO: Migration completed successfully"
    # Return success for idempotency
    $targetVMName = if ($ReplicatingServer.PSObject.Properties['TargetVMName']) { $ReplicatingServer.TargetVMName } else { 'Unknown' }
    $result = @{
      Status = "AlreadyCompleted"
      MigrationState = $migrationState
      Message = "Migration already completed"
      TargetVMName = $targetVMName
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
  if ($PSCmdlet.ShouldProcess(
    "VM '$MachineName' in project '$ProjectName'",
    "Perform Azure Migrate cutover migration"
  )) {
    Write-Output "Initiating migration..."
    $MigrationResult = Start-AzMigrateServerMigration @migrationParams
  }

  if ($MigrationResult) {
    Write-Output "INFO: Cutover initiated successfully"
    
    # Check what properties are available on the migration result
    Write-Output "INFO: Available properties on migration result: $($MigrationResult.PSObject.Properties.Name -join ', ')"
    
    # Safely access JobId property
    $jobId = if ($MigrationResult.PSObject.Properties['JobId']) { $MigrationResult.JobId } elseif ($MigrationResult.PSObject.Properties['Id']) { $MigrationResult.Id } else { 'Unknown' }
    Write-Output "INFO: Job ID: $jobId"

    # Safely access TargetVMName property
    $targetName = if ($MigrationResult.PSObject.Properties['TargetVMName']) { $MigrationResult.TargetVMName } else { $null }
    if (-not $targetName) {
      $targetName = if ($ReplicatingServer.PSObject.Properties['TargetVMName']) { $ReplicatingServer.TargetVMName } else { 'Unknown' }
    }
    Write-Output "INFO: Target VM: $targetName"

    # Return result
    $result = @{
      Status = "Initiated"
      JobId = $jobId
      TargetVMName = $targetName
      MigrationState = "MigrationInProgress"
      Message = "Cutover initiated successfully"
      ShutdownSourceVM = $ShutdownSourceVM
    }

    $result | ConvertTo-Json -Depth 3
  } else {
    Write-Output "ERROR: Cutover failed - no result returned"
    
    # Output error result in JSON format for Ansible parsing
    $errorResult = @{
      Status = "Failed"
      Error = "Cutover failed - no result returned from Start-AzMigrateServerMigration"
      MigrationState = $migrationState
      Message = "Azure Migrate API did not return a result"
    }
    
    $errorResult | ConvertTo-Json -Depth 3
    exit 1
  }

} catch {
  Write-Output "ERROR: Cutover failed for '$MachineName'"
  Write-Output "ERROR: $($_.Exception.Message)"

  $errorResult = @{
    Status = "Failed"
    Error = $_.Exception.Message
    MigrationState = $migrationState
    Message = "Cutover operation failed"
  }

  $errorResult | ConvertTo-Json -Depth 3
  exit 1
}
