#!/bin/sh
hostname opeth
ifconfig eth0 147.210.12.1/24
route add default gw 147.210.12.2

### PHP ###
cp /mnt/host/php7.0-fpm.conf /etc/nginx/conf.d/php7.0-fpm.conf
service php7.0-fpm restart

### NGINX load new configuration ###
cp /mnt/host/nginx.conf /etc/nginx/sites-enabled/default
## Restart service ##
service nginx restart
