#!/bin/bash

ifconfig eth0 add 147.210.13.2 netmask 255.255.255.0 up
route add default gw 147.210.13.1

echo "147.210.12.1 www.opeth.local" > /etc/hosts

# Add CA certificate to firefox
su - toto -c 'certutil -A -n "ca@ca.local" -t "C,C,C" -i /mnt/host/cert.pem -d /home/toto/.mozilla/firefox/*.default'
