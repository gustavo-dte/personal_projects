trim trailing whitespace.................................................Passed
Detect secrets...........................................................Failed
- hook id: detect-secrets
- exit code: 1

ERROR: Potential secrets about to be committed to git repo!

Secret Type: Secret Keyword
Location:    terraform\azure_sql\terraform-docs.yml:16

Possible mitigations:
  - For information about putting your secrets in a safer place, please ask in
    #security
  - Mark false positives with an inline `pragma: allowlist secret` comment

If a secret has already been committed, visit
https://help.github.com/articles/removing-sensitive-data-from-a-repository

Terraform fmt............................................................Failed
- hook id: terraform_fmt
- exit code: 127

Neither Terraform nor OpenTofu binary could be found. Please either set the "--tf-path" hook configuration argument, or set the "PCT_TFPATH" environment variable, or set the "TERRAGRUNT_TFPATH" environment variable, or install Terraform or OpenTofu globally.
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
Neither Terraform nor OpenTofu binary could be found. Please either set the "--tf-path" hook configuration argument, or set the "PCT_TFPATH" environment variable, or set the "TERRAGRUNT_TFPATH" environment variable, or install Terraform or OpenTofu globally.
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 
C:\Users\u69819\.cache\pre-commit\repo8xcyvp87\hooks\terraform_fmt.sh: line 52: : command not found 

Terraform validate with tflint...........................................Failed
- hook id: terraform_tflint
- exit code: 127

Command 'tflint --init' failed:
epo8xcyvp87\hookse\pre-cerraform_tflint.sh: line 25: tflint: command not found

Terraform docs...........................................................Failed
- hook id: terraform_docs
- exit code: 1

ERROR: terraform-docs is required by terraform_docs pre-commit hook but is not installed or in the system's PATH.

(.vmware_env) PS C:\Users\u69819\Documents\DevOps\vmware\cloud-platform-vm-migration> pip install tflint
ERROR: Could not find a version that satisfies the requirement tflint (from versions: none)
ERROR: No matching distribution found for tflint