#!/bin/bash
set -eu

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-pip git ansible awscli jq

sleep 10

# Recuperar credenciales de RDS desde Secrets Manager
SECRET=$(aws secretsmanager get-secret-value \
  --region ${aws_region} \
  --secret-id ${secret_id} \
  --query SecretString --output text)

DB_HOST=$(echo "$SECRET" | jq -r .host)
DB_USER=$(echo "$SECRET" | jq -r .username)
DB_PASS=$(echo "$SECRET" | jq -r .password)
DB_NAME=$(echo "$SECRET" | jq -r .dbname)

# Escribir variables a fichero JSON temporal para evitar problemas
# con caracteres especiales en la contraseña
cat > /tmp/ansible_vars.json <<EOF
{
  "db_host": $(echo "$DB_HOST" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
  "db_user": $(echo "$DB_USER" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
  "db_pass": $(echo "$DB_PASS" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
  "db_name": $(echo "$DB_NAME" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))"),
  "github_repo": $(echo "${github_repo}" | python3 -c "import sys,json; print(json.dumps(sys.stdin.read().strip()))")
}
EOF

ansible-pull \
  -U ${github_repo} \
  -d /home/ubuntu/TFG-ASIR-AAU \
  -i ansible/inventory \
  --extra-vars "@/tmp/ansible_vars.json" \
  ansible/playbooks/webserver.yml