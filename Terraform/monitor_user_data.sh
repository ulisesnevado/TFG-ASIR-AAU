#!/bin/bash
set -eu

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y \
  python3 \
  python3-pip \
  python3-pandas \
  python3-joblib \
  python3-sklearn \
  python3-boto3 \
  git \
  cron

# Clonar el repo del TFG en /home/ubuntu
sudo -u ubuntu git clone ${github_repo} /home/ubuntu/TFG-ASIR-AAU

# Copiar los scripts y el modelo a /home/ubuntu/ para que las rutas absolutas
# de los scripts funcionen sin modificar el repo
cp /home/ubuntu/TFG-ASIR-AAU/monitorizacion-ia/scripts/cw_test.py             /home/ubuntu/
cp /home/ubuntu/TFG-ASIR-AAU/monitorizacion-ia/scripts/ia_model.py            /home/ubuntu/
cp /home/ubuntu/TFG-ASIR-AAU/monitorizacion-ia/scripts/send_to_cloudwatch.py  /home/ubuntu/
cp /home/ubuntu/TFG-ASIR-AAU/monitorizacion-ia/scripts/ejecutar_monitorizacion.sh /home/ubuntu/
cp /home/ubuntu/TFG-ASIR-AAU/monitorizacion-ia/modelo/isolation_forest_model.pkl /home/ubuntu/
cp /home/ubuntu/TFG-ASIR-AAU/monitorizacion-ia/modelo/scaler.pkl              /home/ubuntu/

# Permisos correctos
chmod +x /home/ubuntu/ejecutar_monitorizacion.sh
chown ubuntu:ubuntu /home/ubuntu/*.py /home/ubuntu/*.sh /home/ubuntu/*.pkl

# Crear log file
touch /home/ubuntu/cron_monitorizacion.log
chown ubuntu:ubuntu /home/ubuntu/cron_monitorizacion.log

# Programar cron cada 5 minutos para el usuario ubuntu
(crontab -u ubuntu -l 2>/dev/null; echo "*/5 * * * * /home/ubuntu/ejecutar_monitorizacion.sh") | crontab -u ubuntu -

# Asegurar que cron esta corriendo
systemctl enable cron
systemctl start cron
