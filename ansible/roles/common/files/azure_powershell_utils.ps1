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

# Resolve the current principal's AAD objectId for role queries
function Get-CurrentPrincipalObjectId {
    try {
        $ctx = Get-AzContext -ErrorAction Stop
        $accountType = $ctx.Account.Type
        $accountId = $ctx.Account.Id

        # Preferred: explicit username if provided by environment
        if ($env:AZURE_USERNAME) {
            $user = Get-AzADUser -UserPrincipalName $env:AZURE_USERNAME -ErrorAction SilentlyContinue
            if ($user) { return $user.Id }
        }

        if ($accountType -eq 'User') {
            $user = Get-AzADUser -UserPrincipalName $accountId -ErrorAction SilentlyContinue
            if ($user) { return $user.Id }
            $userByMail = Get-AzADUser -Mail $accountId -ErrorAction SilentlyContinue
            if ($userByMail) { return $userByMail.Id }
        } elseif ($accountType -eq 'ServicePrincipal' -or $accountType -eq 'ManagedService') {
            # For SP contexts, Account.Id is typically the application (client) ID
            $sp = Get-AzADServicePrincipal -ApplicationId $accountId -ErrorAction SilentlyContinue
            if ($sp) { return $sp.Id }
            $spByObj = Get-AzADServicePrincipal -ObjectId $accountId -ErrorAction SilentlyContinue
            if ($spByObj) { return $spByObj.Id }
        }
    } catch {
        # Fall through to null
    }
    return $null
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
        Write-Host "INFO: Successfully imported Azure PowerShell modules: $($RequiredModules -join ', ')"
    }
    catch {
        Write-Host "ERROR: Required Azure PowerShell modules not available. Please install them with:"
        Write-Host "  Install-Module -Name Az -Scope CurrentUser -Force"
        Write-Host "Or install specific modules:"
        Write-Host "  Install-Module -Name $($RequiredModules -join ', ') -Scope CurrentUser -Force"
        Write-Host "See: https://learn.microsoft.com/azure/migrate/tutorial-migrate-vmware-powershell?view=migrate-classic"
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
            Write-Host "ERROR: Required cmdlet '$Cmdlet' not found. Ensure required Azure PowerShell modules are installed/updated."
            Write-Host "See: https://learn.microsoft.com/azure/migrate/tutorial-migrate-vmware-powershell?view=migrate-classic"
            exit 1
        }
    }
    Write-Host "INFO: All required cmdlets verified: $($RequiredCmdlets -join ', ')"
}

# Verify and set Azure PowerShell context
function Set-AzureContext {
    param(
        [string]$SubscriptionId
    )

    # Verify Azure PowerShell context exists
    $ctx = Get-AzContext -ErrorAction SilentlyContinue
    if (-not $ctx) {
        Write-Host "ERROR: No Azure PowerShell context found. Please authenticate first using 'az login'"
        exit 1
    }

    # Set subscription context if specified
    if ($SubscriptionId -and $ctx.Subscription.Id -ne $SubscriptionId) {
        try {
            Set-AzContext -SubscriptionId $SubscriptionId | Out-Null
            Write-Host "INFO: Set Azure context to subscription: $SubscriptionId"
        }
        catch {
            Write-Host "ERROR: Failed to set Azure context to subscription '$SubscriptionId': $($_.Exception.Message)"
            exit 1
        }
    } elseif (-not $SubscriptionId -or [string]::IsNullOrWhiteSpace($SubscriptionId)) {
        $SubscriptionId = $ctx.Subscription.Id
        Write-Host "INFO: Using current Azure context subscription: $SubscriptionId"
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
            Write-Host "ERROR: $ResourceType '$ResourceName' not found$(if($ResourceGroupName) { " in resource group '$ResourceGroupName'" })."
            exit 1
        }

        if ($resource) {
            Write-Host "INFO: Found $ResourceType '$ResourceName'$(if($ResourceGroupName) { " in resource group '$ResourceGroupName'" })"
        }

        return $resource
    }
    catch {
        if ($Required) {
            Write-Host "ERROR: Failed to get $ResourceType '$ResourceName': $($_.Exception.Message)"
            exit 1
        }
        return $null
    }
}

# Initialize Azure Migrate replication infrastructure
function Initialize-AzureMigrateReplicationInfrastructure {
    param(
        [string]$ProjectName,
        [string]$ProjectResourceGroup,
        [string]$ScenarioChoice = "agentlessVMware",
        [string]$TargetRegion = "CentralUS"
    )

    try {
        Write-Host "INFO: Attempting to initialize Azure Migrate replication infrastructure...`n"
        Write-Host "INFO: Project Name: $ProjectName`n"

        # Check if Initialize-AzMigrateReplicationInfrastructure cmdlet exists
        if (Get-Command -Name Initialize-AzMigrateReplicationInfrastructure -ErrorAction SilentlyContinue) {
            Write-Host "INFO: Initialize-AzMigrateReplicationInfrastructure cmdlet found, attempting initialization...`n"

            Write-Host "INFO: Initializing replication infrastructure...`n"
            $initResult = Initialize-AzMigrateReplicationInfrastructure `
                -ResourceGroupName $ProjectResourceGroup `
                -ProjectName $ProjectName `
                -Scenario $ScenarioChoice `
                -TargetRegion $TargetRegion

            Write-Host "SUCCESS: Replication infrastructure initialized successfully`n"
            Write-Host "INFO: Initialization result: $initResult`n"
        } else {
            Write-Host "WARNING: Initialize-AzMigrateReplicationInfrastructure cmdlet not available`n"
        }
    }
    catch {
        Write-Host "ERROR: Failed to initialize replication infrastructure: $($_.Exception.Message)`n"
        Write-Host "INFO: Exception details: $($_.Exception)`n"
        Write-Host "INFO: Please initialize replication infrastructure manually in Azure Portal`n"
    }
}
