#!/bin/bash
set -eu

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-pip git ansible

# Ansible-pull: clona el repo y ejecuta el playbook del monitor.
# Toda la configuracion (dependencias, scripts, .pkl, cron) vive en
# ansible/playbooks/roles/monitor/tasks/main.yml para mantener el mismo
# patron que las EC2 Flask.
ansible-pull \
  -U ${github_repo} \
  -d /home/ubuntu/TFG-ASIR-AAU \
  -i ansible/inventory \
  ansible/playbooks/monitor.yml
