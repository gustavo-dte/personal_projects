Run # Set patching status based on validation
  # Set patching status based on validation
  if [ "true" = "true" ]; then
    echo "patching_configured=true" >> $GITHUB_OUTPUT
    echo "✅ Patching configuration was included in workflow"
  else
    echo "patching_configured=false" >> $GITHUB_OUTPUT
    if [ -n "patching_schedules/testing_vm_patching_schedules.json" ]; then
      echo "⚠️ Patching file provided but not found - skipped"
    else
      echo "ℹ️ Patching not configured (no schedules file provided)"
    fi
  fi
  shell: /bin/bash -e {0}
  env:
    ANSIBLE_ROLES_PATH: ansible/roles
    ANSIBLE_CONFIG: ansible/ansible.cfg
✅ Patching configuration was included in workflow

Run echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "✅ Workflow completed successfully!"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  echo "🔍 Intelligent Processing Summary:"
  echo "   The workflow automatically determined which VMs needed cutover"
  echo "   and which were already migrated, then configured patching for all."
  echo ""
  echo "📊 View detailed output in the workflow console logs above"
  echo ""
  echo "Next: Verify VMs and patching configuration in Azure portal"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  shell: /bin/bash -e {0}
  env:
    ANSIBLE_ROLES_PATH: ansible/roles
    ANSIBLE_CONFIG: ansible/ansible.cfg
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ Workflow completed successfully!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 Intelligent Processing Summary:
   The workflow automatically determined which VMs needed cutover
   and which were already migrated, then configured patching for all.

📊 View detailed output in the workflow console logs above

Next: Verify VMs and patching configuration in Azure portal
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━