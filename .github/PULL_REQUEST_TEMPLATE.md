<!--
Please include the ticket number in the title of your PR in the format AB#{ID} (example: AB#125)
For more details about GitHub PR linking to Azure Boards, see:
<https://learn.microsoft.com/en-us/azure/devops/boards/github/link-to-from-github?view=azure-devops#use-ab-to-link-from-github-to-azure-boards-work-items>
-->
### Summary
<!-- Quickly describe your changes and purpose of this Pull Request -->

#### Changes Made
<!-- Bullet point list of changes made in this Pull Request -->

#### ADO Story
<!-- Replace {ID} with your ticket number. It will automatically be converted into a hyperlink -->
AB#{ID}

#### Areas for Discussion/Feedback
<!-- Optional - List any parts of this PR that you would like discussion/feedback on -->

---

### 📋 Terraform Pull Request Review Checklist
<!--
Acknowledge each point by placing an 'x' in the brackets (e.g., [x])
If a section is not not application, please state as such
-->

#### 🔐 Secrets & Sensitive Data

- [ ] No secrets are hardcoded in `.tf` files
- [ ] Secrets (passwords, keys, connection strings) are pulled from **Azure Key Vault** or passed securely
- [ ] Sensitive variables are marked with `sensitive = true`

#### 📛 Naming Conventions

- [ ] Terraform resource names are in **lowercase** and use **underscores** (e.g., `storage_account_name`)
- [ ] Terraform file and module names follow the same **lowercase** and **underscore** naming convention
- [ ] Names are concise, consistent, and reflect their purpose

#### 📄 Documentation & Comments

- [ ] Module changes include updates to `README.md` (if applicable) - **rewrite on tfdocs**
- [ ] PR includes documentation or notes for any breaking changes
- [ ] Inline comments explain complex or non-obvious logic

#### 🏷 Resource Tagging

- [ ] All resources are tagged with required tags
- [ ] Tag values are standardized across resources
- [ ] All resources are tagged with required tags (e.g., `Application`, `BillTo`, `BusinessCriticality`, `ContactEmail`, `DataClassification`,`Environment`,`Portfolio` and `Project`)

#### 📐 Code Quality

- [ ] Code is formatted using `terraform fmt`
- [ ] Code passes `terraform validate`
- [ ] `terraform plan` check has passed
- [ ] Obsolete resources, variables, or comments are cleaned up

#### 📁 Structure & File Organization

- [ ] Variables are defined in `variables.tf`
- [ ] Locals are defined in `locals.tf`
- [ ] Outputs are defined in `outputs.tf`
- [ ] Code is logically split across files (e.g., one type of resource category per file, i.e network related resources can be defined in a network.tf)

#### 🧱 Modularization

- [ ] Reusable Terraform code should be organized into modules. Each module should be published to a Terraform registry with proper versioning to ensure separation of concerns and avoid repeating logic.
- [ ] Modules include clear input and output definitions
- [ ] Module variables are validated with type, description, and default (if applicable)
- [ ] Modules are versioned and environment-agnostic
