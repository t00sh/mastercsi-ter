#!/bin/sh

hostname opeth
ifconfig eth0 147.210.12.1/24
route add default gw 147.210.12.2

### PHP ###
cp /mnt/host/php7.0-fpm.conf /etc/nginx/conf.d/php7.0-fpm.conf
service php7.0-fpm restart

### NGINX load new configuration ###
sed -i 's/# server_names_hash_bucket_size/server_names_hash_bucket_size/' /etc/nginx/nginx.conf
cp /mnt/host/nginx.conf /etc/nginx/sites-enabled/default
chmod -R 0755 /mnt/
chown www-data: -R /mnt/host/www
service nginx restart

### DNSMASQ configuration ###
cp /mnt/host/dnsmasq.conf /etc/
echo "147.210.12.1 www.opeth.local opeth.local" >> /etc/hosts
echo "147.210.12.1 www.opeth.secure opeth.secure" >> /etc/hosts
service dnsmasq restart
