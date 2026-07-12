#!/bin/bash
# Simple HTTPS wrapper for Cortex RAG server using socat
set -e

echo "Creating self-signed certificate..."
openssl req -x509 -newkey rsa:4096 -keyout /tmp/cortex-key.pem -out /tmp/cortex-cert.pem \
    -days 365 -nodes -subj "/CN=100.97.25.117"

echo "Combining cert and key..."
cat /tmp/cortex-cert.pem /tmp/cortex-key.pem > /tmp/cortex.pem

echo "Starting HTTPS proxy on port 8443..."
echo "Proxying https://100.97.25.117:8443 -> http://localhost:8100"
echo ""
echo "Press Ctrl+C to stop"

socat OPENSSL-LISTEN:8443,cert=/tmp/cortex.pem,verify=0,fork TCP:localhost:8100
