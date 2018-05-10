#!/bin/sh

hostname immortal
ifconfig eth0 147.210.12.2/24
ifconfig eth1 147.210.13.1/24
echo 1 > /proc/sys/net/ipv4/ip_forward

# Configure dnsmasq
cp /mnt/host/dnsmasq.conf /etc/
