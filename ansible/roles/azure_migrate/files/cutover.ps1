#! /usr/bin/env pwsh
#Requires -Version 7.0
# Note: Azure modules will be imported dynamically to avoid hard requirement failure

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

# Results tracking - initialize early
$Results = @{
  VMName = $MachineName
  Success = $false
  Error = $null
  JobId = $null
  MigrationState = $null
  Status = $null
  TargetVMName = $null
  StartTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

try {
  # Import common utilities
  $UtilsPath = Join-Path $PSScriptRoot "..\..\common\files\azure_powershell_utils.ps1"
  if (Test-Path $UtilsPath) {
      . $UtilsPath
  } else {
      Write-Host "ERROR: Common utilities script not found at: $UtilsPath"
      $Results.Error = "Common utilities script not found"
      $Results.Status = "Failed"
      return
  }

  # Initialize environment and import required modules with custom error handling
  try {
    # Check if Azure modules are available before importing
    $MissingModules = @()
    $RequiredModules = @('Az.Accounts', 'Az.Migrate', 'Az.Resources')
    
    foreach ($Module in $RequiredModules) {
      if (-not (Get-Module -ListAvailable -Name $Module)) {
        $MissingModules += $Module
      }
    }
    
    if ($MissingModules.Count -gt 0) {
      Write-Host "ERROR: Required Azure PowerShell modules not available: $($MissingModules -join ', ')"
      Write-Host "Please install them with: Install-Module -Name Az -Scope CurrentUser -Force"
      $Results.Error = "Required Azure PowerShell modules not available: $($MissingModules -join ', ')"
      $Results.Status = "Failed"
      return
    }
    
    # If modules are available, proceed with initialization
    Initialize-PowerShellEnvironment
    Import-AzureModules -RequiredModules $RequiredModules
    Test-RequiredCmdlets -RequiredCmdlets @('Get-AzMigrateServerReplication', 'Start-AzMigrateServerMigration')
    
  } catch {
    Write-Host "ERROR: Failed to initialize PowerShell environment or import modules: $($_.Exception.Message)"
    $Results.Error = "Failed to initialize PowerShell environment: $($_.Exception.Message)"
    $Results.Status = "Failed"
    return
  }

  # Set Azure context
  try {
    Write-Host "INFO: Setting Azure context to subscription: $SubscriptionId"
    $AzureSubscriptionId = Set-AzureContext -SubscriptionId $SubscriptionId
    Set-AzureContext -SubscriptionId $AzureSubscriptionId | Out-Null
  } catch {
    Write-Host "ERROR: Failed to set Azure context: $($_.Exception.Message)"
    $Results.Error = "Failed to set Azure context: $($_.Exception.Message)"
    $Results.Status = "Failed"
    return
  }

  Write-Host "INFO: Starting cutover for VM '$MachineName'..."

  # Log cutover parameters
  Write-Host "INFO: Cutover parameters:"
  Write-Host "  - Project: $ProjectName"
  Write-Host "  - Resource Group: $ProjectResourceGroup"
  Write-Host "  - Machine: $MachineName"
  if ($TargetVMName) {
      Write-Host "  - Target VM: $TargetVMName"
  }
  Write-Host "  - Shutdown Source: $ShutdownSourceVM"
  Write-Host "  - Subscription: $SubscriptionId"

  # Get the replicating machine to verify replication status
  Write-Host "INFO: Looking for replicating machine '$MachineName'"
  $ReplicatingServers = Get-AzMigrateServerReplication -ProjectName $ProjectName -ResourceGroupName $ProjectResourceGroup

  # Convert to array to ensure consistent handling of single or multiple results
  $ReplicatingServersArray = @($ReplicatingServers)

  if (-not $ReplicatingServers -or $ReplicatingServersArray.Count -eq 0) {
    Write-Host "ERROR: No replicating servers found in project '$ProjectName'"

    $Results.Success = $false
    $Results.Error = "No replicating servers found in project '$ProjectName'"
    $Results.Status = "Failed"
    $Results.MigrationState = "Unknown"
    return
  }

  # Debug: Show what properties are actually available
  Write-Host "INFO: Retrieved $($ReplicatingServersArray.Count) replicating server(s)"
  if ($ReplicatingServersArray.Count -gt 0) {
    $firstServer = $ReplicatingServersArray[0]
    $availableProperties = $firstServer | Get-Member -MemberType Properties | Select-Object -ExpandProperty Name
    Write-Host "INFO: Available properties on server objects: $($availableProperties -join ', ')"
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
    Write-Host "ERROR: Replicating server '$MachineName' not found"
    Write-Host "Available servers:"
    $ReplicatingServersArray | ForEach-Object {
      # Use defensive property access for display
      $name = if ($_.PSObject.Properties['Name']) { $_.Name } else { 'N/A' }
      $sourceName = if ($_.PSObject.Properties['SourceServerName']) { $_.SourceServerName }
                    elseif ($_.PSObject.Properties['MachineName']) { $_.MachineName }
                    elseif ($_.PSObject.Properties['DisplayName']) { $_.DisplayName }
                    else { 'N/A' }
      $state = if ($_.PSObject.Properties['MigrationState']) { $_.MigrationState } else { 'N/A' }
      $health = if ($_.PSObject.Properties['ReplicationHealth']) { $_.ReplicationHealth } else { 'N/A' }

      Write-Host ("  - {0} (Source: {1}, State: {2}, Health: {3})" -f $name, $sourceName, $state, $health)
    }

    $Results.Success = $false
    $Results.Error = "Replicating server '$MachineName' not found in project '$ProjectName'"
    $Results.Status = "Failed"
    $Results.MigrationState = "Unknown"
    return
  }

  # Display found server info using defensive property access
  $serverName = if ($ReplicatingServer.PSObject.Properties['Name']) { $ReplicatingServer.Name } else { 'N/A' }
  $migrationState = if ($ReplicatingServer.PSObject.Properties['MigrationState']) { [string]$ReplicatingServer.MigrationState } else { 'Unknown' }
  $replicationHealth = if ($ReplicatingServer.PSObject.Properties['ReplicationHealth']) { [string]$ReplicatingServer.ReplicationHealth } else { 'Unknown' }

  Write-Host "INFO: Found server: $serverName"
  Write-Host "INFO: Migration state: $migrationState"
  Write-Host "INFO: Replication health: $replicationHealth"

  # Validate replication status
if ($migrationState -eq "None") {
  Write-Host "ERROR: VM '$MachineName' is not ready for cutover"
  Write-Host "Current state: $migrationState"
  Write-Host "Replication must be active before cutover"

  $Results.Success = $false
  $Results.Error = "VM '$MachineName' is not ready for cutover"
  $Results.Status = "Failed"
  $Results.MigrationState = $migrationState
  return
}

if ($replicationHealth -eq "Critical") {
  Write-Warning "VM has critical replication health"
  Write-Host "Current health: $replicationHealth"
  Write-Host "Review replication status before proceeding"
}

# Check if already migrated or in progress
if ($migrationState -in @("MigrationSucceeded", "MigrationFailed")) {
  Write-Host "INFO: Migration already attempted for '$MachineName'"
  Write-Host "INFO: State: $migrationState"

  if ($migrationState -eq "MigrationSucceeded") {
    Write-Host "SUCCESS: Migration completed successfully for VM '$MachineName'"
    # Return success for idempotency
    $targetVMName = if ($ReplicatingServer.PSObject.Properties['TargetVMName']) { $ReplicatingServer.TargetVMName } else { 'Unknown' }
    $Results.Success = $true
    $Results.Status = "AlreadyCompleted"
    $Results.MigrationState = "MigrationSucceeded"
    $Results.TargetVMName = $targetVMName
    
    Write-Host "SUCCESS: Cutover already completed for VM '$MachineName'"
    Write-Host "INFO: Target VM: $targetVMName"
  } else {
    Write-Host "ERROR: Previous migration failed for VM '$MachineName'"
    $Results.Success = $false
    $Results.Error = "Previous migration attempt failed"
    $Results.Status = "Failed"
    $Results.MigrationState = "MigrationFailed"
  }
  # Exit early - results will be output in finally block
  return
}

# Check if migration is already in progress
if ($migrationState -eq "MigrationInProgress") {
  Write-Host "INFO: Migration already in progress for '$MachineName'"
  Write-Host "INFO: Current migration state: $migrationState"

  # Check if there's a current job
  $currentJobId = if ($ReplicatingServer.PSObject.Properties['CurrentJobId']) { $ReplicatingServer.CurrentJobId } else { 'Unknown' }
  $currentJobName = if ($ReplicatingServer.PSObject.Properties['CurrentJobName']) { $ReplicatingServer.CurrentJobName } else { 'Unknown' }

  Write-Host "INFO: Current Job ID: $currentJobId"
  Write-Host "INFO: Current Job Name: $currentJobName"

  $Results.Success = $true
  $Results.Status = "AlreadyInProgress"
  $Results.MigrationState = $migrationState
  $Results.JobId = $currentJobId
  
  # Exit early - results will be output in finally block
  return
}

# Perform the cutover
Write-Host "INFO: Starting cutover for '$MachineName'"

# Prepare migration parameters
  $migrationParams = @{
    InputObject = $ReplicatingServer
  }

  if ($ShutdownSourceVM) {
    $migrationParams['TurnOffSourceServer'] = $true
    Write-Host "INFO: Source VM will be shut down"
  } else {
    Write-Host "INFO: Source VM will remain running"
  }

  # Start the migration
  if ($PSCmdlet.ShouldProcess(
    "VM '$MachineName' in project '$ProjectName'",
    "Perform Azure Migrate cutover migration"
  )) {
    Write-Host "Initiating migration..."
    $MigrationResult = Start-AzMigrateServerMigration @migrationParams
  }

  if ($MigrationResult) {
    Write-Host "SUCCESS: Cutover initiated successfully for VM '$MachineName'"

    # Check what properties are available on the migration result
    Write-Host "INFO: Available properties on migration result: $($MigrationResult.PSObject.Properties.Name -join ', ')"

    # Safely access JobId property
    $jobId = if ($MigrationResult.PSObject.Properties['JobId']) { $MigrationResult.JobId } elseif ($MigrationResult.PSObject.Properties['Id']) { $MigrationResult.Id } else { 'Unknown' }
    Write-Host "INFO: Migration job ID: $jobId"

    # Safely access TargetVMName property
    $targetName = if ($MigrationResult.PSObject.Properties['TargetVMName']) { $MigrationResult.TargetVMName } else { $null }
    if (-not $targetName) {
      $targetName = if ($ReplicatingServer.PSObject.Properties['TargetVMName']) { $ReplicatingServer.TargetVMName } else { 'Unknown' }
    }
    Write-Host "INFO: Target VM: $targetName"

    # Update results
    $Results.Success = $true
    $Results.JobId = $jobId
    $Results.Status = "Initiated"
    $Results.MigrationState = "MigrationInProgress"
    $Results.TargetVMName = $targetName

  } else {
    Write-Host "ERROR: Cutover failed - no result returned for VM '$MachineName'"
    $Results.Success = $false
    $Results.Error = "Cutover failed - no result returned from Start-AzMigrateServerMigration"
    $Results.Status = "Failed"
    $Results.MigrationState = $migrationState
  }

# Main catch block for all errors
} catch {
  Write-Host "ERROR: Operation failed for '$MachineName'"
  Write-Host "ERROR: $($_.Exception.Message)"

  $Results.Success = $false
  $Results.Error = $_.Exception.Message
  $Results.Status = "Failed"
  if (-not $Results.MigrationState) {
    $Results.MigrationState = "Unknown"
  }

} finally {
  # Output results as JSON for Ansible processing
  $JsonOutput = $Results | ConvertTo-Json -Depth 3

  # Write JSON to a file for Ansible to read - use current working directory
  $OutputFile = Join-Path (Get-Location) "cutover_result.json"
  Write-Host "INFO: Writing JSON output to: $OutputFile"
  $JsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8

  # Also output to console for debugging
  Write-Host "JSON output written to: $OutputFile"
  Write-Host $JsonOutput

  # Exit with appropriate code
  if ($Results.Success) {
    exit 0
  } else {
    exit 1
  }
}
