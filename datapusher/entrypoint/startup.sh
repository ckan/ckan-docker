#!/bin/bash
  
# turn on bash's job control
set -m
  
# Start the primary process and put it in the background
${VENV}/bin/uwsgi --socket=/tmp/uwsgi.sock --enable-threads -i ${CFG_DIR}/uwsgi.ini --wsgi-file=${SRC_DIR}/datapusher-plus/wsgi.py &
  
# Start the test process
#cd ${SRC_DIR}/testing-datapusher-plus && ${VENV}/bin/python test.py

fg %1
