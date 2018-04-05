#!/bin/sh
hostname immortal
ifconfig eth0 147.210.12.2/24
ifconfig eth1 147.210.13.1/24

echo 1 > /proc/sys/net/ipv4/ip_forward
route add default gw 147.210.13.2

# Set host
echo "147.210.12.1 www.opeth.local www.opeth.secure" > /etc/hosts
