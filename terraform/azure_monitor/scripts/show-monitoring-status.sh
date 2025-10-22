#!/bin/bash

# Script to display monitoring status after Terraform deployment

echo "=== Azure Monitor Deployment Status ==="
echo ""

# Get Terraform outputs
terraform output -json > /tmp/terraform_outputs.json

# Display infrastructure status
echo "Infrastructure Components:"
echo "- Resource Group: $(terraform output -raw resource_group_name)"
echo "- Log Analytics Workspace: $(terraform output -raw log_analytics_workspace_id | cut -d'/' -f9)"
echo "- Application Insights: $(terraform output -raw application_insights_id | cut -d'/' -f9)"
echo "- Action Group: $(terraform output -raw action_group_id | cut -d'/' -f9)"
echo ""

# Display monitored VMs
echo "Monitored Virtual Machines:"
terraform output -json monitored_windows_vms | jq -r 'to_entries[] | "- Windows VM: \(.key) (Status: \(.value.monitoring_enabled))"'
terraform output -json monitored_linux_vms | jq -r 'to_entries[] | "- Linux VM: \(.key) (Status: \(.value.monitoring_enabled))"'
echo ""

# Display alert summary
echo "Alert Configuration:"
terraform output -json monitoring_summary | jq -r '.alerting | "- Total Alert Rules: \(.total_alert_rules)", "- Notification Email: \(.notification_email)"'
echo ""

# Display features enabled
echo "Features Enabled:"
terraform output -json monitoring_summary | jq -r '.features_enabled | to_entries[] | "- \(.key | gsub("_"; " ") | ascii_upcase): \(.value)"'
echo ""

echo "=== Deployment Complete ==="
