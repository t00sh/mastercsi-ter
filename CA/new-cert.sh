#!/bin/sh

# Create and sign certificate with CA's private key

if test ! -f root-ca.pem || test ! -f root-ca.key
then
    echo "[-] First, create CA !"
    exit 1
fi

# Create private key
openssl genrsa -out cert.key 4096

# Create request
openssl req -new -key cert.key -out cert.csr

# Sign certificate with CA
openssl x509 -req -in cert.csr -CA root-ca.pem -CAkey root-ca.key -CAcreateserial -out cert.pem -days 365 -sha256

echo "[+] Your certificate: cert.pem"
echo "[+] Your private key: cert.key"
