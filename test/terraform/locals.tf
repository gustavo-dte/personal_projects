locals {
  // tflint-ignore: terraform_unused_declarations
  prefix = "cloud-platform"
  // tflint-ignore: terraform_unused_declarations
  environment      = lower(var.environment)
  primary_prefix   = "${local.prefix}-${local.environment}-cu-${var.application}"
  secondary_prefix = "${local.prefix}-${local.environment}-e2-${var.application}"

  tags = {
    Environment         = var.environment
    Portfolio           = "CCOE"
    Application         = "CorpApps"
    BillTo              = "100000069697"
    ContactEmail        = "cloudplatform@dteenergy.com"
    BusinessCriticality = "Tier4"
    DataClassification  = "Internal"
    CreatedBy           = "Cloud Platform Team"
  }
}
