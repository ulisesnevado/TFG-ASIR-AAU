#!/bin/bash
set -eu

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-pip git ansible awscli jq

# Recuperar credenciales de RDS desde Secrets Manager
SECRET=$(aws secretsmanager get-secret-value \
  --region ${aws_region} \
  --secret-id ${secret_id} \
  --query SecretString --output text)

DB_HOST=$(echo "$SECRET" | jq -r .host)
DB_USER=$(echo "$SECRET" | jq -r .username)
DB_PASS=$(echo "$SECRET" | jq -r .password)
DB_NAME=$(echo "$SECRET" | jq -r .dbname)

ansible-pull \
  -U ${github_repo} \
  -d /home/ubuntu/TFG-ASIR-AAU \
  -i ansible/inventory \
  --extra-vars "db_host=$DB_HOST db_user=$DB_USER db_pass=$DB_PASS db_name=$DB_NAME github_repo=${github_repo}" \
  ansible/playbooks/webserver.yml