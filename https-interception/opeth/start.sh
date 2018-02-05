#!/bin/sh
hostname opeth
ifconfig eth0 147.210.12.1/24
route add default gw 147.210.12.2
