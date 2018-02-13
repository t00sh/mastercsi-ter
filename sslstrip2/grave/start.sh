#!/bin/bash

ifconfig eth0 add 147.210.13.2 netmask 255.255.255.0 up
route add default gw 147.210.13.1

echo "147.210.12.1 www.opeth.local" >> /etc/hosts
echo "147.210.12.1 www.opeth.secure" >> /etc/hosts
