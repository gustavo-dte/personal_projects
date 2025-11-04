# Azure SQL Terraform Modules - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# Navigate to module
cd D:\DevOps\DTE\vmware\source_code\cloud-platform-vm-migration\terraform\azure_sql

# Initialize
terraform init

# Validate
terraform validate

# Plan (Dev)
terraform plan -var-file="environments/dev.tfvars"

# Apply (Dev)
terraform apply -var-file="environments/dev.tfvars"

# Destroy
terraform destroy -var-file="environments/dev.tfvars"
```

## 📦 Module Locations

| Module | Path | Purpose |
|--------|------|---------|
| **SQL Server** | `./modules/sql-server/` | Logical SQL Server |
| **SQL Database** | `./modules/sql-database/` | Individual databases |
| **SQL Managed Instance** | `./modules/sql-managed-instance/` | Enterprise SQL Server |

## 🎯 Common Use Cases

### 1. Simple SQL Database (Dev/Test)
```hcl
# Use: environments/dev.tfvars
terraform apply -var-file="environments/dev.tfvars"
# Cost: ~$15-75/month
# Time: 5-10 minutes
```

### 2. Production SQL Database
```hcl
# Use: environments/prod.tfvars
terraform apply -var-file="environments/prod.tfvars"
# Cost: ~$930-2,790/month (3 databases)
# Time: 5-10 minutes
```

### 3. SQL Managed Instance (Lift-and-Shift)
```hcl
# Requires: VNet setup first
# Cost: ~$670-5,360/month
# Time: 4-6 hours (first deployment)
```

## 💰 Cost Quick Reference

| SKU | Type | vCores/DTUs | Monthly Cost | Use Case |
|-----|------|-------------|--------------|----------|
| **S0** | Standard | 10 DTUs | $15 | Dev/Test |
| **S1** | Standard | 20 DTUs | $30 | Small apps |
| **S2** | Standard | 50 DTUs | $75 | Medium apps |
| **S4** | Standard | 200 DTUs | $465 | Production |
| **GP_Gen5_4** | vCore | 4 vCores | $672 ($302 AHB) | General Purpose |
| **GP_Gen5_8** | MI | 8 vCores | $1,340 ($603 AHB) | Lift-and-shift |
| **BC_Gen5_16** | MI | 16 vCores | $5,360 ($2,412 AHB) | Enterprise |

**AHB = Azure Hybrid Benefit (55% savings for MI, 40% for DB)**

## 🔐 Security Quick Commands

```bash
# Add firewall rule for your IP
az sql server firewall-rule create \
  --resource-group "rg-vm-migration-sql-dev" \
  --server "sql-vm-migration-dev" \
  --name "AllowMyIP" \
  --start-ip-address $(curl -s ifconfig.me) \
  --end-ip-address $(curl -s ifconfig.me)

# List databases
az sql db list \
  --resource-group "rg-vm-migration-sql-dev" \
  --server "sql-vm-migration-dev" \
  --output table

# Test connection
sqlcmd -S sql-vm-migration-dev.database.windows.net -U devadmin -P '<password>' -d migration-db-dev
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Can't connect** | Check firewall rules: `az sql server firewall-rule list` |
| **Deployment slow (MI)** | Normal - MI takes 4-6 hours on first deployment |
| **High costs** | Review SKU: `az sql db show --query sku` |
| **MI subnet error** | Use minimum /28 subnet (16 IPs) |

## 📖 File Reference

| File | Purpose |
|------|---------|
| `main.tf` | Root module configuration |
| `variables.tf` | Input variable definitions |
| `outputs.tf` | Output values |
| `terraform.tfvars` | Default variable values |
| `environments/dev.tfvars` | Development environment config |
| `environments/prod.tfvars` | Production environment config |
| `modules/sql-server/` | SQL Server module |
| `modules/sql-database/` | SQL Database module |
| `modules/sql-managed-instance/` | SQL Managed Instance module |

## 🎯 Decision: SQL Database vs Managed Instance

**Choose SQL Database when:**
- ✅ Building new cloud-native applications
- ✅ Need elastic scaling
- ✅ Budget-conscious ($15-$1,000/month)
- ✅ Don't need SQL Agent, cross-DB queries, CLR

**Choose Managed Instance when:**
- ✅ Lift-and-shift from on-premises SQL Server
- ✅ Need 99.9% SQL Server compatibility
- ✅ Require SQL Agent, Service Broker, CLR
- ✅ Need cross-database queries
- ✅ Have SQL Server licenses (Azure Hybrid Benefit)

---

**Quick Reference Version:** 1.0  
**Last Updated:** November 2024
