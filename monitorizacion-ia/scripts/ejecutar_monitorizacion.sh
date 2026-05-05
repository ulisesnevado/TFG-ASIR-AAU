#!/bin/bash

LOG="/home/ubuntu/cron_monitorizacion.log"
FECHA=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$FECHA] Inicio" >> "$LOG"

/usr/bin/python3 /home/ubuntu/cw_test.py             >> "$LOG" 2>&1
/usr/bin/python3 /home/ubuntu/ia_model.py            >> "$LOG" 2>&1
/usr/bin/python3 /home/ubuntu/send_to_cloudwatch.py  >> "$LOG" 2>&1

FECHA_FIN=$(date '+%Y-%m-%d %H:%M:%S')
echo "[$FECHA_FIN] Fin" >> "$LOG"
echo "-----------------------------" >> "$LOG"
