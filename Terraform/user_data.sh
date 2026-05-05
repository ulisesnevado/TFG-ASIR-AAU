#!/bin/bash
set -eu
 
export DEBIAN_FRONTEND=noninteractive
 
apt-get update -y
apt-get install -y python3 python3-pip git ansible
 
# Ansible-pull, pasando las credenciales de RDS como extra-vars
ansible-pull \
  -U ${github_repo} \
  -d /home/ubuntu/TFG-ASIR-AAU \
  -i ansible/inventory \
  --extra-vars "db_host=${db_host} db_user=${db_user} db_pass=${db_password} db_name=${db_name} github_repo=${github_repo}" \
  ansible/playbooks/webserver.yml