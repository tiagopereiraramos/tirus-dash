#!/bin/bash
while true; do
    python backend_server.py
    echo "Backend parou, reiniciando..."
    sleep 2
done