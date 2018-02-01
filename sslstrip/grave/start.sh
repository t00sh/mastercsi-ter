#!/bin/sh
hostname grave
ifconfig eth0 147.210.13.2/24
ifconfig eth1 147.210.14.1/24
echo 1 > /proc/sys/net/ipv4/ip_forward
route add -net 147.210.12.0/24 gw 147.210.13.1
route add -net 147.210.15.0/24 gw 147.210.14.2
