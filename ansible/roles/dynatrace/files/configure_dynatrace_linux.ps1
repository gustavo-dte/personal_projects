#! /usr/bin/env pwsh
# PowerShell script to configure Dynatrace extension on Linux VMs

Param(
  [Parameter(Mandatory=$true)][string]$VMName,
  [Parameter(Mandatory=$true)][string]$ResourceGroup,
  [Parameter(Mandatory=$true)][string]$SubscriptionId,
  [Parameter(Mandatory=$false)][string]$DynatraceEnvironmentUrl,
  [Parameter(Mandatory=$false)][string]$DynatraceApiToken,
  [Parameter(Mandatory=$false)][string]$ExtensionVersion = "latest",
  [Parameter(Mandatory=$false)][switch]$DryRun
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
Import-AzureModules -RequiredModules @('Az.Accounts', 'Az.Compute')
Test-RequiredCmdlets -RequiredCmdlets @('Get-AzVM', 'Set-AzVMExtension')

# Set Azure context
Write-Output "INFO: Setting Azure context to subscription: $SubscriptionId"
$SubscriptionId = Set-AzureContext -SubscriptionId $SubscriptionId

# Initialize result object
$Result = @{
  VMName = $VMName
  ResourceGroup = $ResourceGroup
  Success = $false
  ExtensionStatus = "Unknown"
  Message = ""
  ExtensionName = "DynatraceOneAgent"
  ExtensionVersion = ""
  StartTime = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
  Error = $null
}

try {
  Write-Output "INFO: Configuring Dynatrace extension for Linux VM '$VMName'..."
  
  # Get VM information
  Write-Output "INFO: Retrieving VM information..."
  $VM = Get-AzVM -ResourceGroupName $ResourceGroup -Name $VMName -ErrorAction Stop
  
  if (-not $VM) {
    throw "VM '$VMName' not found in resource group '$ResourceGroup'"
  }
  
  Write-Output "INFO: VM Location: $($VM.Location)"
  Write-Output "INFO: VM OS Type: $($VM.StorageProfile.OsDisk.OsType)"
  
  # Check if VM is running
  $VMStatus = Get-AzVM -ResourceGroupName $ResourceGroup -Name $VMName -Status -ErrorAction Stop
  $PowerState = ($VMStatus.Statuses | Where-Object { $_.Code -like "PowerState/*" }).Code -replace "PowerState/", ""
  
  if ($PowerState -ne "running") {
    $Result.ExtensionStatus = "Skipped"
    $Result.Message = "VM is not running (current state: $PowerState). Extension can only be installed on running VMs."
    $Result.Success = $false
    Write-Output "WARNING: $($Result.Message)"
  } else {
    # Check if Dynatrace extension already exists
    Write-Output "INFO: Checking for existing Dynatrace extension..."
    $ExistingExtension = $VM.Extensions | Where-Object { $_.Publisher -eq "dynatrace.ruxit" -or $_.Name -like "*Dynatrace*" }
    
    if ($ExistingExtension) {
      Write-Output "INFO: Dynatrace extension already installed:"
      Write-Output "  Name: $($ExistingExtension.Name)"
      Write-Output "  Type: $($ExistingExtension.Type)"
      Write-Output "  Publisher: $($ExistingExtension.Publisher)"
      Write-Output "  Version: $($ExistingExtension.TypeHandlerVersion)"
      
      $Result.ExtensionStatus = "AlreadyInstalled"
      $Result.ExtensionVersion = $ExistingExtension.TypeHandlerVersion
      $Result.Message = "Dynatrace extension is already installed (version: $($ExistingExtension.TypeHandlerVersion))"
      $Result.Success = $true
    } else {
      if ($DryRun) {
        Write-Output "INFO: [DRY RUN] Would install Dynatrace extension with the following settings:"
        Write-Output "  VM Name: $VMName"
        Write-Output "  Resource Group: $ResourceGroup"
        Write-Output "  Location: $($VM.Location)"
        Write-Output "  Extension Version: $ExtensionVersion"
        if ($DynatraceEnvironmentUrl) {
          Write-Output "  Dynatrace Environment URL: $DynatraceEnvironmentUrl"
        }
        
        $Result.ExtensionStatus = "DryRun"
        $Result.Message = "Dry run completed - no actual changes made"
        $Result.Success = $true
      } else {
        # Prepare extension settings
        $ExtensionSettings = @{}
        $ProtectedSettings = @{}
        
        if ($DynatraceEnvironmentUrl) {
          $ExtensionSettings.Add("tenantId", $DynatraceEnvironmentUrl)
        }
        
        if ($DynatraceApiToken) {
          $ProtectedSettings.Add("token", $DynatraceApiToken)
        }
        
        # Install Dynatrace extension
        Write-Output "INFO: Installing Dynatrace extension..."
        $ExtensionParams = @{
          ResourceGroupName = $ResourceGroup
          VMName = $VMName
          Name = "DynatraceOneAgent"
          Publisher = "dynatrace.ruxit"
          ExtensionType = "oneAgentLinux"
          TypeHandlerVersion = if ($ExtensionVersion -eq "latest") { "2.0" } else { $ExtensionVersion }
          Location = $VM.Location
          ErrorAction = "Stop"
        }
        
        if ($ExtensionSettings.Count -gt 0) {
          $ExtensionParams.Add("Settings", $ExtensionSettings)
        }
        
        if ($ProtectedSettings.Count -gt 0) {
          $ExtensionParams.Add("ProtectedSettings", $ProtectedSettings)
        }
        
        $Extension = Set-AzVMExtension @ExtensionParams
        
        if ($Extension.IsSuccessStatusCode -or $Extension.StatusCode -eq "OK") {
          Write-Output "INFO: Dynatrace extension installed successfully"
          $Result.ExtensionStatus = "Installed"
          $Result.ExtensionVersion = $ExtensionParams.TypeHandlerVersion
          $Result.Message = "Dynatrace extension installed successfully"
          $Result.Success = $true
        } else {
          throw "Extension installation returned unexpected status: $($Extension.StatusCode)"
        }
      }
    }
  }
  
} catch {
  $ErrorMessage = $_.Exception.Message
  Write-Output "ERROR: Failed to configure Dynatrace extension for VM '$VMName': $ErrorMessage"
  
  $Result.ExtensionStatus = "Failed"
  $Result.Success = $false
  $Result.Error = $ErrorMessage
  $Result.Message = "Failed to configure Dynatrace extension: $ErrorMessage"
}

# Add completion time
$Result.Add("EndTime", (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))

# Output result as JSON
$JsonOutput = $Result | ConvertTo-Json -Depth 3

# Write JSON to file for Ansible
$OutputFile = "configure_dynatrace_result.json"
$JsonOutput | Out-File -FilePath $OutputFile -Encoding UTF8

# Output to console
Write-Output ""
Write-Output "=== DYNATRACE CONFIGURATION RESULT ==="
Write-Output $JsonOutput
Write-Output ""
Write-Output "Result written to: $OutputFile"

# Exit with appropriate code
if ($Result.Success) {
  exit 0
} else {
  exit 1
}
