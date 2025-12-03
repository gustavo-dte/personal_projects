Terraform validate with tflint...........................................Failed
- hook id: terraform_tflint
- exit code: 2

Command 'tflint --init' successfully done:
All plugins are already installed



TFLint in dev/terraform/:
1 issue(s) found:

Warning: Module source "github.com/dteenergy/terraform-azurerm-mssqlmi" is not pinned (terraform_module_pinned_source)

  on dev        erraform        ests_sql_dmi.tf line 9:
   9:   source = "github.com/dteenergy/terraform-azurerm-mssqlmi"

Reference: https://github.com/terraform-linters/tflint-ruleset-terraform/blob/v0.13.0/docs/rules/terraform_module_pinned_source.md