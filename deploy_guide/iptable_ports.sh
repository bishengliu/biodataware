#!/usr/bin/env bash

iptables -I INPUT 1 -i eth0 -p tcp --dport 8000 -j ACCEPT
iptables -I INPUT 1 -i eth0 -p tcp --dport 8080 -j ACCEPT

iptables -nvL
