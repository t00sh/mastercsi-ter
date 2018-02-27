#!/bin/sh

# Create the certificate + private key for the certificat authority


# Create root key
openssl genrsa -out root-ca.key 4096

# Self-sign certificate
openssl req -x509 -new -nodes -key root-ca.key -sha256 -days 512 -out root-ca.pem

echo "[+] CA private-key: root-ca.key"
echo "[+] CA certificate: root-ca.pem"