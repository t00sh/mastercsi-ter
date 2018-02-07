#!/bin/bash

ifconfig eth0 add 147.210.13.2 netmask 255.255.255.0 up
route add default gw 147.210.13.1

cp /mnt/host/cert.pem /etc/ssl/certs/