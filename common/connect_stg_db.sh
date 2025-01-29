#! /bin/bash

sudo sysctl -w net.ipv4.conf.all.route_localnet=1
sudo iptables -A INPUT -i br+ -p TCP -j ACCEPT
sudo iptables -t nat -I PREROUTING  -d 172.17.0.1 -p tcp --dport 3310 -j DNAT --to 127.0.0.1:3310
ssh -L 3310:mysql-stg.internal-stg.mutablep.com:3306 -N bastion-stg.mutablep.com &