#!/bin/bash
socat TCP-LISTEN:80,fork,reuseaddr TCP:localhost:{{port}}

systemctl disable --now systemd-resolved

nano /etc/resolv.conf

Add the following line above the line "nameserver 8.8.8.8":

nameserver your-server-ip # localhost


dnsmasq --test


systemctl restart dnsmasq
