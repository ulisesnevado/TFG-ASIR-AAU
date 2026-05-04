#!/bin/bash
set -eux

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-pip git ansible

# Variables que el playbook leerá del entorno
cat <<EOF >> /etc/environment
DB_HOST=${db_host}
DB_USER=${db_user}
DB_PASS=${db_password}
DB_NAME=${db_name}
EOF

# Cargar el environment para esta misma sesión
set -o allexport
source /etc/environment
set +o allexport

# Ansible-pull desde el repo del TFG
ansible-pull \
  -U ${github_repo} \
  -d /home/ubuntu/TFG-ASIR-AAU \
  -i ansible/inventory \
  ansible/playbooks/webserver.yml