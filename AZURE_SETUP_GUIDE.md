# Azure Service Principal Setup for GitHub Actions

This guide explains how to set up Azure authentication for the GitHub Actions workflow using a service principal with Federated Identity (OIDC).

## Prerequisites

- Azure subscription with appropriate permissions to create service principals
- Azure CLI installed (`az` command)
- GitHub repository access to add secrets

## Option 1: Using Azure CLI (Recommended)

### Step 1: Create a Service Principal

```bash
# Set your Azure subscription ID
SUBSCRIPTION_ID="<your-subscription-id>"
RESOURCE_GROUP="<your-resource-group>"
SERVICE_PRINCIPAL_NAME="github-actions-uninstall-tools"

# Create the service principal
az ad sp create-for-rbac \
  --name "$SERVICE_PRINCIPAL_NAME" \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID
```

This will output JSON with:
- `appId` (Client ID)
- `tenant` (Tenant ID)
- `password` (Client Secret - only needed for non-OIDC auth)

### Step 2: Create Federated Identity Credential (OIDC)

```bash
# Variables
APP_ID="<appId-from-previous-step>"
GITHUB_OWNER="dteenergy"
GITHUB_REPO="cloud-platform-vm-migration"
ENVIRONMENT="dev"  # or your GitHub environment name

# Create the federated credential
az ad app federated-credential create \
  --id "$APP_ID" \
  --parameters '{
    "name": "github-actions-'$ENVIRONMENT'",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:'$GITHUB_OWNER'/'$GITHUB_REPO':environment:'$ENVIRONMENT'",
    "description": "GitHub Actions OIDC for '$ENVIRONMENT' environment",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### Step 3: Add GitHub Repository Secrets

Go to your GitHub repository:
1. **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret** and add:

| Name | Value |
|------|-------|
| `AZURE_CLIENT_ID` | `<appId>` from Step 1 |
| `AZURE_TENANT_ID` | `<tenant>` from Step 1 |
| `AZURE_SUBSCRIPTION_ID` | Your Azure subscription ID |

## Option 2: Using Azure Portal UI

### Step 1: Create a Service Principal in Azure Portal

1. Go to **Azure Portal** → **Azure Active Directory** → **App registrations**
2. Click **New registration**
3. Fill in:
   - **Name**: `github-actions-uninstall-tools`
   - **Supported account types**: Accounts in this organizational directory only
4. Click **Register**

### Step 2: Get Client ID and Tenant ID

In the app registration page:
- Copy **Application (client) ID** → This is your `AZURE_CLIENT_ID`
- Copy **Directory (tenant) ID** → This is your `AZURE_TENANT_ID`

### Step 3: Add Federated Credential

1. In the app registration, go to **Certificates & secrets** → **Federated credentials**
2. Click **Add credential**
3. Select **GitHub Actions deploying to Azure** scenario
4. Fill in:
   - **Organization**: `dteenergy`
   - **Repository**: `cloud-platform-vm-migration`
   - **Entity type**: Environment
   - **Environment name**: `dev` (or your GitHub environment)
5. Click **Add**

### Step 4: Assign Role to Service Principal

```bash
# Assign Contributor role to the service principal
az role assignment create \
  --assignee "<appId>" \
  --role "Contributor" \
  --scope "/subscriptions/<subscription-id>"
```

### Step 5: Add Secrets to GitHub

Same as Option 1, Step 3.

## Verify the Setup

### Test Azure Login

Run this command locally to verify:

```bash
# Using OIDC (no credentials needed on your machine)
az login --service-principal \
  -u $AZURE_CLIENT_ID \
  -t $AZURE_TENANT_ID \
  --allow-no-subscriptions
```

Or run the workflow in GitHub Actions and check the logs.

## Workflow Execution

Once secrets are configured, the workflow will:

1. Check out the repository
2. **Authenticate to Azure** using the service principal via OIDC
3. Run the Ansible playbook with Azure access
4. Upload logs as artifacts

## Troubleshooting

### "Failed to authenticate with Azure"
- Verify all three secrets are set correctly in GitHub
- Check that the federated credential is created correctly
- Ensure the GitHub environment name matches the federated credential

### "Permission denied" errors
- Ensure the service principal has **Contributor** role on the subscription
- Check that the resource group and VMs are in the correct subscription

### "Resource not found" errors
- Verify VMs exist in Azure in the resource group specified in the manifest
- Check subscription ID in manifest matches `AZURE_SUBSCRIPTION_ID` secret

## Security Best Practices

1. ✅ Use **Federated Identity (OIDC)** - No secrets stored on disk
2. ✅ Limit scope to specific **resource groups** instead of full Contributor
3. ✅ Use **GitHub environments** to control which branches can deploy
4. ✅ Enable **Branch protection rules** for production deployments
5. ✅ Regularly audit **role assignments** and remove unused service principals

## References

- [Azure Login GitHub Action](https://github.com/Azure/login)
- [Federated Identity Credential Setup](https://learn.microsoft.com/en-us/graph/api/application-post-federatedidentitycredentials)
- [GitHub Actions OIDC](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
