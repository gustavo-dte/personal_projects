# Playbooks

These YAML files are **entrypoints** into Ansible. They are intended to be invoked by workflows or users to run a given migration operation (e.g. start replication, cutover, generate Terraform). They should **not** house significant logic or code; orchestration and implementation live in **roles** under `ansible/roles/`. Each playbook wires a manifest and any inputs into the appropriate role(s).
