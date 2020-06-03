#!/bin/bash
IP=$1
rules=$(iptables-save | grep ${IP})
if [ ! "${rules}" ]; then
        iptables -A INPUT -s ${IP} -j ACCEPT
        netfilter-persistent save
        echo "Add ${IP} to whitelist"
else
	exit
fi
