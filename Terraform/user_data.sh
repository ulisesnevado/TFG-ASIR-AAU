#!/bin/bash
set -x
apt update -y
apt upgrade -y
apt install -y python3 python3-pip git mysql-client ansible
pip3 install flask

cd /home/ubuntu
git clone https://github.com/ulisesnevado/TFG-ASIR-AAU
cd TFG-ASIR-AAU
[ -f requirements.txt ] && pip3 install -r requirements.txt

cat <<EOT > /etc/systemd/system/flaskapp.service
[Unit]
Description=Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/TFG-ASIR-AAU
ExecStart=/usr/bin/python3 /home/ubuntu/TFG-ASIR-AAU/app.py
Restart=always
Environment="DB_HOST=${db_host}"
Environment="DB_USER=${db_username}"
Environment="DB_PASS=${db_password}"
Environment="DB_NAME=foca_teste"

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable --now flaskapp
