locals {
  // tflint-ignore: terraform_unused_declarations
  prefix = "cloud-platform"
  // tflint-ignore: terraform_unused_declarations
  environment                 = lower(var.environment)
  primary_prefix              = "${local.prefix}-prod-cu-${var.application}"
  secondary_prefix            = "${local.prefix}-prod-e2-${var.application}"
  primary_vnet_cidr           = module.primary_ipam.allocated_cidr
  primary_sqlmi_fbk_vnet_cidr = module.primary_sqlmi_fbk_ipam.allocated_cidr
  secondary_vnet_cidr         = module.secondary_ipam.allocated_cidr

  tags = {
    Environment         = var.environment
    Portfolio           = "CCOE"
    Application         = "CorpApps"
    BillTo              = "100000069697"
    ContactEmail        = "cloudplatform@dteenergy.com"
    BusinessCriticality = "Tier3"
    DataClassification  = "Internal"
    CreatedBy           = "Cloud Platform Team"
  }
}
