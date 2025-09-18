#! /usr/bin/env pwsh
# Common Azure PowerShell utilities for migration scripts
# This script contains shared functions and initialization code

# Initialize PowerShell environment with consistent settings
function Initialize-PowerShellEnvironment {
    Set-StrictMode -Version Latest
    $script:ErrorActionPreference = 'Stop'

    # Disable PowerShell styling for cleaner output
    if (Get-Variable -Name PSStyle -ErrorAction SilentlyContinue) {
        $PSStyle.OutputRendering = 'PlainText'
    }
}

# Import required Azure PowerShell modules with standardized error handling
function Import-AzureModules {
    param(
        [string[]]$RequiredModules = @('Az.Accounts')
    )

    try {
        foreach ($Module in $RequiredModules) {
            Import-Module $Module -Force
        }
        Write-Output "INFO: Successfully imported Azure PowerShell modules: $($RequiredModules -join ', ')"
    }
    catch {
        Write-Output "ERROR: Required Azure PowerShell modules not available. Please install them with:"
        Write-Output "  Install-Module -Name Az -Scope CurrentUser -Force"
        Write-Output "Or install specific modules:"
        Write-Output "  Install-Module -Name $($RequiredModules -join ', ') -Scope CurrentUser -Force"
        Write-Output "See: https://learn.microsoft.com/azure/migrate/tutorial-migrate-vmware-powershell?view=migrate-classic"
        exit 1
    }
}

# Verify required cmdlets exist
function Test-RequiredCmdlets {
    param(
        [string[]]$RequiredCmdlets
    )

    foreach ($Cmdlet in $RequiredCmdlets) {
        if (-not (Get-Command -Name $Cmdlet -ErrorAction SilentlyContinue)) {
            Write-Output "ERROR: Required cmdlet '$Cmdlet' not found. Ensure required Azure PowerShell modules are installed/updated."
            Write-Output "See: https://learn.microsoft.com/azure/migrate/tutorial-migrate-vmware-powershell?view=migrate-classic"
            exit 1
        }
    }
    Write-Output "INFO: All required cmdlets verified: $($RequiredCmdlets -join ', ')"
}

# Verify and set Azure PowerShell context
function Set-AzureContext {
    param(
        [string]$SubscriptionId
    )

    # Verify Azure PowerShell context exists
    $ctx = Get-AzContext -ErrorAction SilentlyContinue
    if (-not $ctx) {
        Write-Output "ERROR: No Azure PowerShell context found. Please authenticate first using 'az login'"
        exit 1
    }

    # Set subscription context if specified
    if ($SubscriptionId -and $ctx.Subscription.Id -ne $SubscriptionId) {
        try {
            Set-AzContext -SubscriptionId $SubscriptionId | Out-Null
            Write-Output "INFO: Set Azure context to subscription: $SubscriptionId"
        }
        catch {
            Write-Output "ERROR: Failed to set Azure context to subscription '$SubscriptionId': $($_.Exception.Message)"
            exit 1
        }
    } elseif (-not $SubscriptionId -or [string]::IsNullOrWhiteSpace($SubscriptionId)) {
        $SubscriptionId = $ctx.Subscription.Id
        Write-Output "INFO: Using current Azure context subscription: $SubscriptionId"
    }

    return $SubscriptionId
}

# Get Azure resource with error handling
function Get-AzureResource {
    param(
        [string]$ResourceType,
        [string]$ResourceName,
        [string]$ResourceGroupName,
        [switch]$Required
    )

    try {
        $resource = switch ($ResourceType) {
            'ResourceGroup' { Get-AzResourceGroup -Name $ResourceName -ErrorAction SilentlyContinue }
            'VirtualNetwork' { Get-AzVirtualNetwork -ResourceGroupName $ResourceGroupName -Name $ResourceName -ErrorAction SilentlyContinue }
            default { throw "Unsupported resource type: $ResourceType" }
        }

        if (-not $resource -and $Required) {
            Write-Output "ERROR: $ResourceType '$ResourceName' not found$(if($ResourceGroupName) { " in resource group '$ResourceGroupName'" })."
            exit 1
        }

        if ($resource) {
            Write-Output "INFO: Found $ResourceType '$ResourceName'$(if($ResourceGroupName) { " in resource group '$ResourceGroupName'" })"
        }

        return $resource
    }
    catch {
        if ($Required) {
            Write-Output "ERROR: Failed to get $ResourceType '$ResourceName': $($_.Exception.Message)"
            exit 1
        }
        return $null
    }
}

# Export functions for use in other scripts
Export-ModuleMember -Function Initialize-PowerShellEnvironment, Import-AzureModules, Test-RequiredCmdlets, Set-AzureContext, Get-AzureResource
