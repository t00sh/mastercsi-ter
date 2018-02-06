#!/bin/sh
hostname grave
ifconfig eth0 147.210.13.2/24
route add -net 147.210.12.0/24 gw 147.210.13.1

cat /mnt/host/cert.pem >> /etc/ssl/certs/ca-certificates.crt
