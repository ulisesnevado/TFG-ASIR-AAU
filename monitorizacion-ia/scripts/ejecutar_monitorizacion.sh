#!/usr/bin/env bash
set -Eeuo pipefail

cd /home/ubuntu

LOG_FILE="/home/ubuntu/cron_monitorizacion.log"

{
  echo "===== $(date '+%Y-%m-%d %H:%M:%S') - inicio monitorización ====="

  /usr/bin/python3 /home/ubuntu/cw_test.py
  /usr/bin/python3 /home/ubuntu/ia_model.py
  /usr/bin/python3 /home/ubuntu/send_to_cloudwatch.py

  echo "===== $(date '+%Y-%m-%d %H:%M:%S') - fin OK ====="
  echo ""
} >> "$LOG_FILE" 2>&1
