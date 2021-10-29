#!/bin/sh

echo "[start_datapusher.sh] Starting supervisord."
# Start supervisord
supervisord --configuration /etc/supervisord.conf
