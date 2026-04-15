#!/bin/bash
CERT_DIR="/etc/neuraldrive/tls"
mkdir -p "$CERT_DIR"

IP_ADDR=$(ip -4 route get 1 2>/dev/null | awk '{print $7; exit}')
SAN="DNS:neuraldrive.local,DNS:neuraldrive"
if [ -n "$IP_ADDR" ]; then
    SAN="${SAN},IP:${IP_ADDR}"
fi

openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes \
  -keyout "$CERT_DIR/server.key" -out "$CERT_DIR/server.crt" \
  -subj "/C=US/ST=State/L=City/O=NeuralDrive/CN=neuraldrive.local" \
  -addext "subjectAltName=${SAN}"
chmod 600 "$CERT_DIR/server.key"

cp "$CERT_DIR/server.crt" "$CERT_DIR/neuraldrive-ca.crt"
chmod 644 "$CERT_DIR/neuraldrive-ca.crt"
echo "Certificate generated. SAN: ${SAN}"
echo "Client CA cert: ${CERT_DIR}/neuraldrive-ca.crt"
