# Azure SQL Database Deployment Script (PowerShell)
# Usage: .\deploy.ps1 -Environment dev -Action plan
# Example: .\deploy.ps1 -Environment prod -Action apply

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory = $false)]
    [ValidateSet("init", "plan", "apply", "destroy", "validate", "fmt", "show")]
    [string]$Action = "plan"
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$TerraformDir = Split-Path -Parent $ScriptDir
$ErrorActionPreference = "Stop"

# Logging functions
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor Blue
}

function Write-Error-Log {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning-Log {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

# Check prerequisites
function Test-Prerequisites {
    Write-Log "Checking prerequisites..."
    
    # Check if terraform is installed
    if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) {
        Write-Error-Log "Terraform is not installed or not in PATH"
        exit 1
    }
    
    # Check if Azure CLI is installed
    if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
        Write-Error-Log "Azure CLI is not installed or not in PATH"
        exit 1
    }
    
    # Check if logged into Azure
    try {
        az account show | Out-Null
    }
    catch {
        Write-Error-Log "Not logged into Azure. Please run 'az login'"
        exit 1
    }
    
    Write-Success "Prerequisites check passed"
}

# Set environment variables
function Set-EnvironmentVariables {
    Write-Log "Setting environment variables for $Environment..."
    
    switch ($Environment) {
        "dev" { $env:TF_VAR_environment = "Development" }
        "staging" { $env:TF_VAR_environment = "Staging" }
        "prod" { $env:TF_VAR_environment = "Production" }
    }
    
    # Get Azure subscription info
    $subscriptionInfo = az account show | ConvertFrom-Json
    $env:TF_VAR_azure_subscription_id = $subscriptionInfo.id
    $env:TF_VAR_azure_tenant_id = $subscriptionInfo.tenantId
    
    Write-Success "Environment variables set"
}

# Initialize Terraform
function Initialize-Terraform {
    Write-Log "Initializing Terraform..."
    Set-Location $TerraformDir
    terraform init
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Log "Terraform initialization failed"
        exit 1
    }
    Write-Success "Terraform initialized"
}

# Validate Terraform configuration
function Test-TerraformConfiguration {
    Write-Log "Validating Terraform configuration..."
    Set-Location $TerraformDir
    terraform validate
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Log "Terraform validation failed"
        exit 1
    }
    Write-Success "Terraform configuration is valid"
}

# Format Terraform files
function Format-TerraformFiles {
    Write-Log "Formatting Terraform files..."
    Set-Location $TerraformDir
    terraform fmt -recursive
    Write-Success "Terraform files formatted"
}

# Plan Terraform deployment
function New-TerraformPlan {
    Write-Log "Creating Terraform plan for $Environment..."
    Set-Location $TerraformDir
    
    $varFile = "environments\$Environment.tfvars"
    if (-not (Test-Path $varFile)) {
        Write-Warning-Log "Environment file $varFile not found, using terraform.tfvars"
        $varFile = "terraform.tfvars"
    }
    
    terraform plan -var-file="$varFile" -out="$Environment.tfplan"
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Log "Terraform plan failed"
        exit 1
    }
    Write-Success "Terraform plan created: $Environment.tfplan"
}

# Apply Terraform deployment
function Submit-TerraformPlan {
    Write-Log "Applying Terraform plan for $Environment..."
    Set-Location $TerraformDir
    
    $planFile = "$Environment.tfplan"
    if (-not (Test-Path $planFile)) {
        Write-Error-Log "Plan file $planFile not found. Please run plan first."
        exit 1
    }
    
    Write-Warning-Log "This will create/modify Azure resources. Continue? (y/N)"
    $response = Read-Host
    if ($response -notmatch "^[Yy]$") {
        Write-Log "Deployment cancelled"
        exit 0
    }
    
    terraform apply $planFile
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Log "Terraform apply failed"
        exit 1
    }
    Write-Success "Terraform deployment completed"
}

# Destroy Terraform resources
function Remove-TerraformResources {
    Write-Log "Planning destruction of Terraform resources for $Environment..."
    Set-Location $TerraformDir
    
    $varFile = "environments\$Environment.tfvars"
    if (-not (Test-Path $varFile)) {
        Write-Warning-Log "Environment file $varFile not found, using terraform.tfvars"
        $varFile = "terraform.tfvars"
    }
    
    Write-Error-Log "WARNING: This will DESTROY all resources in $Environment environment!"
    Write-Warning-Log "Are you absolutely sure? Type 'yes' to confirm:"
    $response = Read-Host
    if ($response -ne "yes") {
        Write-Log "Destruction cancelled"
        exit 0
    }
    
    terraform destroy -var-file="$varFile"
    if ($LASTEXITCODE -ne 0) {
        Write-Error-Log "Terraform destroy failed"
        exit 1
    }
    Write-Success "Resources destroyed"
}

# Show Terraform state
function Show-TerraformState {
    Write-Log "Showing Terraform state for $Environment..."
    Set-Location $TerraformDir
    terraform show
}

# Main execution
function Main {
    Write-Log "Starting Azure SQL Database deployment script"
    Write-Log "Environment: $Environment"
    Write-Log "Action: $Action"
    
    Test-Prerequisites
    Set-EnvironmentVariables
    
    switch ($Action) {
        "init" {
            Initialize-Terraform
        }
        "validate" {
            Initialize-Terraform
            Test-TerraformConfiguration
        }
        "fmt" {
            Format-TerraformFiles
        }
        "plan" {
            Initialize-Terraform
            Test-TerraformConfiguration
            New-TerraformPlan
        }
        "apply" {
            Submit-TerraformPlan
        }
        "destroy" {
            Remove-TerraformResources
        }
        "show" {
            Show-TerraformState
        }
        default {
            Write-Error-Log "Unknown action: $Action"
            exit 1
        }
    }
    
    Write-Success "Script completed successfully"
}

# Show usage if help requested
if ($args -contains "-h" -or $args -contains "--help") {
    Write-Host @"
Usage: .\deploy.ps1 -Environment <env> -Action <action>

Parameters:
  -Environment    Target environment (dev, staging, prod). Default: dev
  -Action         Action to perform (init, plan, apply, destroy, validate, fmt, show). Default: plan

Examples:
  .\deploy.ps1 -Environment dev -Action plan        # Plan deployment for development
  .\deploy.ps1 -Environment prod -Action apply      # Apply production deployment
  .\deploy.ps1 -Environment dev -Action destroy     # Destroy development resources
"@
    exit 0
}

# Run main function
Main