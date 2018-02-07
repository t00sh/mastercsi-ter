#!/bin/sh

iptables -t nat -F
iptables -t nat -A PREROUTING -d 147.210.12.1 -p tcp --dport 443 -j REDIRECT --to-port 4242
/mnt/host/https-interception.py
