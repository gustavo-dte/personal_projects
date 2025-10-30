#! /usr/bin/env pwsh
# PowerShell script to start migration replication using Azure Migrate

Param(
  # Required parameters
  [Parameter(Mandatory=$true)][string]$ProjectName,
  [Parameter(Mandatory=$true)][string]$ProjectResourceGroup,
  [Parameter(Mandatory=$true)][string]$ProjectSubscriptionId,
  [Parameter(Mandatory=$true)][string]$MachineName,
  [Parameter(Mandatory=$true)][string]$TargetResourceGroup,
  [Parameter(Mandatory=$true)][string]$TargetSubscriptionId,
  [Parameter(Mandatory=$true)][string]$TargetNetworkId,
  [Parameter(Mandatory=$true)][string]$TargetSubnetName,
  [Parameter(Mandatory=$true)][string]$OSDiskScsiId,

  # Optional parameters
  [Parameter(Mandatory=$false)][string]$TargetVMName,
  [Parameter(Mandatory=$false)][string]$TargetVMSize = "Standard_DS2_v2",
  [Parameter(Mandatory=$false)][string]$LicenseType = "NoLicenseType",
  [Parameter(Mandatory=$false)][string]$TargetDiskType = "Standard_LRS",
  [Parameter(Mandatory=$false)][switch]$SkipOSVersionCheck,
  [Parameter(Mandatory=$false)][int]$MinWindowsBuild = 17763,
  [Parameter(Mandatory=$false)][int]$MinRHELVersion = 8,
  [Parameter(Mandatory=$false)][string]$TargetRegion = "CentralUS",
  [Parameter(Mandatory=$false)][string]$ScenarioChoice = "agentlessVMware",
  [Parameter(Mandatory=$false)][string]$Tags
)

# Import common utilities
$UtilsPath = Join-Path $PSScriptRoot "..\..\common\files\azure_powershell_utils.ps1"
if (Test-Path $UtilsPath) {
  . $UtilsPath
} else {
  Write-Output "ERROR: Common utilities script not found at: $UtilsPath"
  exit 1
}

# Convert JSON string tag parameters to hashtables
function Convert-TagsFromJson {
  param([string]$TagJson)

  if ([string]::IsNullOrWhiteSpace($TagJson)) {
    return $null
  }

  try {
    $tags = $TagJson | ConvertFrom-Json -AsHashtable
    if ($tags -is [hashtable]) {
      return $tags
    } elseif ($tags -is [PSCustomObject]) {
      # Convert PSCustomObject to hashtable if needed
      $hashtable = @{}
      $tags.PSObject.Properties | ForEach-Object {
        $hashtable[$_.Name] = $_.Value
      }
      return $hashtable
    } else {
      Write-Output "WARNING: Tags parameter is not a valid JSON object. Ignoring tags."
      return $null
    }
  } catch {
    Write-Output "WARNING: Failed to parse tags JSON: $($_.Exception.Message). Ignoring tags."
    return $null
  }
}

# Convert tag JSON string to hashtable (applied to VM, Disk, and NIC)
$TagsHashtable = Convert-TagsFromJson -TagJson $Tags

# Initialize environment and import required modules
Initialize-PowerShellEnvironment
Import-AzureModules -RequiredModules @('Az.Accounts', 'Az.Migrate', 'Az.Resources', 'Az.Network', 'Az.Storage', 'Az.Compute')
Test-RequiredCmdlets -RequiredCmdlets @('New-AzMigrateServerReplication', 'Get-AzMigrateDiscoveredServer', 'New-AzMigrateDiskMapping')

# Set Azure context
Write-Output "INFO: Setting Azure context to subscription: $TargetSubscriptionId"
Set-AzureContext -SubscriptionId $TargetSubscriptionId

# Get target resource group and virtual network using common utilities
$targetRg = Get-AzureResource -ResourceType 'ResourceGroup' -ResourceName $TargetResourceGroup -Required
$targetRgId = $targetRg.ResourceId

# Set target VM name to source VM name if not provided
if (-not $TargetVMName) {
  $TargetVMName = $MachineName
  Write-Output "INFO: Target VM name not specified, using source VM name: $TargetVMName"
}

# Log target configuration
Write-Output "INFO: Target VM Name: $TargetVMName"
Write-Output "INFO: Target Resource Group: $TargetResourceGroup"
Write-Output "INFO: Target Network ID: $TargetNetworkId"
Write-Output "INFO: Target Subnet: $TargetSubnetName"

# Set Azure context
Write-Output "INFO: Setting Azure context to subscription: $ProjectSubscriptionId"
Set-AzureContext -SubscriptionId $ProjectSubscriptionId

# Retrieve discovered server in the Migrate project (DisplayName is the VM name shown by Azure Migrate)
$DiscoveredServer = Get-AzMigrateDiscoveredServer -ProjectName $ProjectName -ResourceGroupName $ProjectResourceGroup -DisplayName $MachineName | Select-Object -First 1
if (-not $DiscoveredServer) {
  Write-Output "ERROR: Discovered server '$MachineName' not found in project '$ProjectName' (RG: '$ProjectResourceGroup')."
  exit 1
}

# Validate OS version requirements using configurable minimum versions
function Test-OSVersionSupported {
  param($Server, $MinWinBuild, $MinRHEL)

  # Extract OS information from discovered server
  $osName = $Server.OperatingSystemName
  $osVersion = $Server.OperatingSystemVersion

  if (-not $osName) {
    Write-Output "WARNING: Operating system information not available for '$MachineName'. Proceeding without OS validation."
    return $true
  }

  Write-Output "INFO: Detected OS: $osName (Version: $osVersion)"

  # Check Windows Server versions
  if ($osName -match "Windows.*Server") {
    if ($osVersion -match "(\d+)\.(\d+)\.(\d+)") {
      $buildNumber = [int]$matches[3]
      if ($buildNumber -lt $MinWinBuild) {
        Write-Output "ERROR: Windows Server version not supported. Requires build $MinWinBuild or later. Found build: $buildNumber"
        return $false
      }
      Write-Output "INFO: Windows Server version is supported (build: $buildNumber >= $MinWinBuild)"
      return $true
    }
    else {
      Write-Output "WARNING: Could not parse Windows Server version '$osVersion'. Proceeding without validation."
      return $true
    }
  }

  # Check RHEL versions
  elseif ($osName -match "Red Hat.*Enterprise.*Linux|RHEL") {
    if ($osVersion -match "(\d+)\.(\d+)" -or $osVersion -match "(\d+)") {
      $majorVersion = [int]$matches[1]
      if ($majorVersion -lt $MinRHEL) {
        Write-Output "ERROR: RHEL version not supported. Requires RHEL $MinRHEL or later. Found version: $majorVersion"
        return $false
      }
      Write-Output "INFO: RHEL version is supported (version: $majorVersion >= $MinRHEL)"
      return $true
    }
    else {
      Write-Output "WARNING: Could not parse RHEL version '$osVersion'. Proceeding without validation."
      return $true
    }
  }

  # For other OS types, log info but allow to proceed
  else {
    Write-Output "INFO: OS type '$osName' - skipping version validation (only Windows Server and RHEL are validated)"
    return $true
  }
}

# Perform OS version validation (unless skipped)
if ($SkipOSVersionCheck) {
  Write-Output "INFO: OS version validation skipped for '$MachineName' due to -SkipOSVersionCheck parameter."
} elseif (-not (Test-OSVersionSupported -Server $DiscoveredServer -MinWinBuild $MinWindowsBuild -MinRHEL $MinRHELVersion)) {
  Write-Output "ERROR: OS version validation failed for '$MachineName'. Replication cannot proceed."
  Write-Output "INFO: Use -SkipOSVersionCheck parameter to bypass this validation if needed."
  Write-Output "INFO: Current requirements: Windows Server build >= $MinWindowsBuild, RHEL >= $MinRHELVersion"
  exit 1
}

# Create disk mappings dynamically from discovered server disks
$DisksToInclude = @()

if (-not $DiscoveredServer.Disk -or $DiscoveredServer.Disk.Count -eq 0) {
  Write-Output "ERROR: No disks found for discovered server '$MachineName'."
  exit 1
}

Write-Output "INFO: Found $($DiscoveredServer.Disk.Count) disk(s) for '$MachineName'"

# Find OS disk using SCSI ID
$OSDiskFound = $false
foreach ($disk in $DiscoveredServer.Disk) {
  $isOSDisk = $false

  # Check if this is the OS disk by SCSI ID
  if ($disk.Name -eq $OSDiskScsiId) {
    $isOSDisk = $true
    $OSDiskFound = $true
    Write-Output "INFO: OS disk identified by SCSI ID '$OSDiskScsiId': $($disk.Uuid)"
  }

  # Create disk mapping for this disk
  $diskMapping = New-AzMigrateDiskMapping -DiskID $disk.Uuid -DiskType $TargetDiskType -IsOSDisk $isOSDisk
  $DisksToInclude += $diskMapping

  $diskType = if ($isOSDisk) { "OS" } else { "Data" }
  Write-Output "INFO: Added $diskType disk: $($disk.Name) (UUID: $($disk.Uuid), Type: $TargetDiskType)"
}

# Verify we found an OS disk
if (-not $OSDiskFound) {
  Write-Output "ERROR: Could not identify OS disk for '$MachineName'."
  Write-Output "INFO: Available disks:"
  foreach ($disk in $DiscoveredServer.Disk) {
    Write-Output "  - Name: $($disk.Name), UUID: $($disk.Uuid)"
  }
  Write-Output "INFO: Specify correct -OSDiskScsiId (currently: '$OSDiskScsiId') parameter."
  exit 1
}

Write-Output "INFO: Created $($DisksToInclude.Count) disk mapping(s) for replication"

# Log all replication parameters
Write-Output "INFO: Starting replication with parameters:"
Write-Output "  - Source VM: $MachineName"
Write-Output "  - Target VM Name: $TargetVMName"
Write-Output "  - Target Resource Group ID: $targetRgId"
Write-Output "  - Target Network ID: $TargetNetworkId"
Write-Output "  - Target Subnet: $TargetSubnetName"
Write-Output "  - Target VM Size: $TargetVMSize"
Write-Output "  - License Type: $LicenseType"
Write-Output "  - Target Disk Type: $TargetDiskType"

# Build parameters for New-AzMigrateServerReplication
# Using ByInputObjectPowerUser parameter set which requires DiskToInclude
$params = @{
  InputObject           = $DiscoveredServer
  DiskToInclude         = $DisksToInclude
  LicenseType           = $LicenseType
  TargetResourceGroupId = $targetRgId
  TargetNetworkId       = $TargetNetworkId
  TargetSubnetName      = $TargetSubnetName
  TargetVMName          = $TargetVMName
}

# Add optional parameters only if they have values
if ($TargetVMSize) { $params['TargetVMSize'] = $TargetVMSize }

# Add tag parameters if provided (apply same tags to VM, Disk, and NIC)
if ($TagsHashtable -and $TagsHashtable.Count -gt 0) {
  $params['VMTag'] = $TagsHashtable
  $params['DiskTag'] = $TagsHashtable
  $params['NicTag'] = $TagsHashtable
  Write-Output "INFO: Tags (applied to VM, Disk, and NIC): $($TagsHashtable | ConvertTo-Json -Compress)"
}

# Results tracking
$Results = @{
  VMName = $MachineName
  TargetVMName = $TargetVMName
  Success = $false
  Error = $null
  ReplicationId = $null
  StartTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
}

try {
  Write-Output "INFO: Starting replication for VM '$MachineName'..."
  try {
    $result = New-AzMigrateServerReplication @params
  } catch {
    if ($_.Exception.Message -match "replication infrastructure is not initialized") {
      Write-Output "ERROR: Azure Migrate replication infrastructure is not initialized in the target subscription."
      Write-Output "INFO: Attempting to initialize replication infrastructure automatically..."

      # Try to initialize replication infrastructure automatically using our custom function
      Write-Output "INFO: Calling Initialize-AzureMigrateReplicationInfrastructure function..."

      # Call the function and capture the return value properly
      $initResult = Initialize-AzureMigrateReplicationInfrastructure `
        -ProjectName $ProjectName `
        -ProjectResourceGroup $ProjectResourceGroup `
        -Scenario $ScenarioChoice `
        -TargetRegion $TargetRegion

      Write-Output $initResult

      # Catch the output has the word ERROR
      if ($initResult -contains "ERROR") {
        Write-Output "ERROR: Initialize-AzureMigrateReplicationInfrastructure failed."
        Write-Output $initResult
        throw "Replication infrastructure not initialized. Please initialize it first."
      }

      if ($initResult) {
        Write-Output "INFO: Retrying replication after infrastructure initialization..."
        $result = New-AzMigrateServerReplication @params
      } else {
        Write-Output "INFO: Automatic initialization failed. Please review the output above."
        throw "Replication infrastructure not initialized. Please initialize it first."
      }
    } else {
      throw
    }
  }

  # Extract replication ID from result
  $replicationId = $null
  if ($result -and $result.Id) {
    $replicationId = $result.Id
  }

  $Results.Success = $true
  $Results.ReplicationId = $replicationId

  Write-Output "SUCCESS: Replication started successfully for VM '$MachineName'"
  if ($replicationId) {
    Write-Output "INFO: Replication ID: $replicationId"
  }

  # Output result details
  Write-Output "INFO: Replication result:"
  $result | ConvertTo-Json -Depth 6

} catch {
  $errorMessage = $_.Exception.Message
  $Results.Success = $false
  $Results.Error = $errorMessage

  Write-Output "ERROR: Failed to start replication for VM '$MachineName': $errorMessage"
  exit 1
} finally {
  # Output results as JSON for Ansible processing
  $JsonOutput = $Results | ConvertTo-Json -Depth 3

  # Write JSON to a file for Ansible to read
  $OutputFile = "start_replication_result.json"
  $JsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8

  # Also output to console for debugging
  Write-Output "JSON output written to: $OutputFile"
  Write-Output $JsonOutput
}
