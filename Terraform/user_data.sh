#!/bin/bash
apt update -y
apt upgrade -y
apt install -y python3 python3-pip git

pip3 install flask

cd /home/ubuntu
git clone https://github.com/ulisesnevado/TFG-ASIR-AAU
cd TFG-ASIR-AAU

if [ -f requirements.txt ]; then
  pip3 install -r requirements.txt
fi

cat <<EOT > /etc/systemd/system/flaskapp.service
[Unit]
Description=Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/TFG-ASIR-AAU
ExecStart=/usr/bin/python3 /home/ubuntu/TFG-ASIR-AAU/app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOT

systemctl daemon-reload
systemctl enable flaskapp
systemctl start flaskapp