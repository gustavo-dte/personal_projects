#!/bin/bash

# Azure SQL Database Deployment Script
# Usage: ./deploy.sh [environment] [action]
# Example: ./deploy.sh dev plan
# Example: ./deploy.sh prod apply

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TERRAFORM_DIR="$(dirname "$SCRIPT_DIR")"
ENVIRONMENT=${1:-dev}
ACTION=${2:-plan}

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Validation functions
validate_environment() {
    if [[ ! "$ENVIRONMENT" =~ ^(dev|staging|prod)$ ]]; then
        error "Invalid environment: $ENVIRONMENT. Must be one of: dev, staging, prod"
        exit 1
    fi
}

validate_action() {
    if [[ ! "$ACTION" =~ ^(init|plan|apply|destroy|validate|fmt|show)$ ]]; then
        error "Invalid action: $ACTION. Must be one of: init, plan, apply, destroy, validate, fmt, show"
        exit 1
    fi
}

check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if terraform is installed
    if ! command -v terraform &> /dev/null; then
        error "Terraform is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Azure CLI is installed and logged in
    if ! command -v az &> /dev/null; then
        error "Azure CLI is not installed or not in PATH"
        exit 1
    fi
    
    # Check if logged into Azure
    if ! az account show &> /dev/null; then
        error "Not logged into Azure. Please run 'az login'"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Set environment variables
set_environment_variables() {
    log "Setting environment variables for $ENVIRONMENT..."
    
    case $ENVIRONMENT in
        dev)
            export TF_VAR_environment="Development"
            ;;
        staging)
            export TF_VAR_environment="Staging"
            ;;
        prod)
            export TF_VAR_environment="Production"
            ;;
    esac
    
    # Get Azure subscription info
    SUBSCRIPTION_ID=$(az account show --query id -o tsv)
    TENANT_ID=$(az account show --query tenantId -o tsv)
    
    export TF_VAR_azure_subscription_id="$SUBSCRIPTION_ID"
    export TF_VAR_azure_tenant_id="$TENANT_ID"
    
    success "Environment variables set"
}

# Initialize Terraform
terraform_init() {
    log "Initializing Terraform..."
    cd "$TERRAFORM_DIR"
    terraform init
    success "Terraform initialized"
}

# Validate Terraform configuration
terraform_validate() {
    log "Validating Terraform configuration..."
    cd "$TERRAFORM_DIR"
    terraform validate
    success "Terraform configuration is valid"
}

# Format Terraform files
terraform_fmt() {
    log "Formatting Terraform files..."
    cd "$TERRAFORM_DIR"
    terraform fmt -recursive
    success "Terraform files formatted"
}

# Plan Terraform deployment
terraform_plan() {
    log "Creating Terraform plan for $ENVIRONMENT..."
    cd "$TERRAFORM_DIR"
    
    local var_file="environments/${ENVIRONMENT}.tfvars"
    if [[ ! -f "$var_file" ]]; then
        warning "Environment file $var_file not found, using terraform.tfvars"
        var_file="terraform.tfvars"
    fi
    
    terraform plan -var-file="$var_file" -out="${ENVIRONMENT}.tfplan"
    success "Terraform plan created: ${ENVIRONMENT}.tfplan"
}

# Apply Terraform deployment
terraform_apply() {
    log "Applying Terraform plan for $ENVIRONMENT..."
    cd "$TERRAFORM_DIR"
    
    local plan_file="${ENVIRONMENT}.tfplan"
    if [[ ! -f "$plan_file" ]]; then
        error "Plan file $plan_file not found. Please run plan first."
        exit 1
    fi
    
    warning "This will create/modify Azure resources. Continue? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log "Deployment cancelled"
        exit 0
    fi
    
    terraform apply "$plan_file"
    success "Terraform deployment completed"
}

# Destroy Terraform resources
terraform_destroy() {
    log "Planning destruction of Terraform resources for $ENVIRONMENT..."
    cd "$TERRAFORM_DIR"
    
    local var_file="environments/${ENVIRONMENT}.tfvars"
    if [[ ! -f "$var_file" ]]; then
        warning "Environment file $var_file not found, using terraform.tfvars"
        var_file="terraform.tfvars"
    fi
    
    error "WARNING: This will DESTROY all resources in $ENVIRONMENT environment!"
    warning "Are you absolutely sure? Type 'yes' to confirm:"
    read -r response
    if [[ "$response" != "yes" ]]; then
        log "Destruction cancelled"
        exit 0
    fi
    
    terraform destroy -var-file="$var_file"
    success "Resources destroyed"
}

# Show Terraform state
terraform_show() {
    log "Showing Terraform state for $ENVIRONMENT..."
    cd "$TERRAFORM_DIR"
    terraform show
}

# Main execution
main() {
    log "Starting Azure SQL Database deployment script"
    log "Environment: $ENVIRONMENT"
    log "Action: $ACTION"
    
    validate_environment
    validate_action
    check_prerequisites
    set_environment_variables
    
    case $ACTION in
        init)
            terraform_init
            ;;
        validate)
            terraform_init
            terraform_validate
            ;;
        fmt)
            terraform_fmt
            ;;
        plan)
            terraform_init
            terraform_validate
            terraform_plan
            ;;
        apply)
            terraform_apply
            ;;
        destroy)
            terraform_destroy
            ;;
        show)
            terraform_show
            ;;
        *)
            error "Unknown action: $ACTION"
            exit 1
            ;;
    esac
    
    success "Script completed successfully"
}

# Show usage if no arguments
if [[ $# -eq 0 ]]; then
    echo "Usage: $0 [environment] [action]"
    echo ""
    echo "Environments: dev, staging, prod"
    echo "Actions: init, plan, apply, destroy, validate, fmt, show"
    echo ""
    echo "Examples:"
    echo "  $0 dev plan        # Plan deployment for development"
    echo "  $0 prod apply      # Apply production deployment"
    echo "  $0 dev destroy     # Destroy development resources"
    exit 1
fi

# Run main function
main "$@"