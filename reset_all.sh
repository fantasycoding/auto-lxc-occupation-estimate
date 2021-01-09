#!/bin/bash

for i in $(lxc ls -c n --format csv); do echo $i; lxc stop $i --force; lxc delete $i; done

for i in $(ip link | egrep -o cn[0-9]+[rh][0-9]+-eth[0-9]+); do echo $i; sudo ip link del $i; done
for i in $(ip link | egrep -o n[0-9]+[rh][0-9]+-eth[0-9]+); do echo $i; sudo ip link del $i; done
for i in $(ip link | egrep -o n[0-9]+[a-zA-Z0-9]+-[a-zA-Z0-9]+); do echo $i; sudo ip link del $i; done

for i in $(ip link | egrep -o enp94s0f0.[0-9]+); do echo $i; sudo ip link del $i; done

for i in $(ip link | egrep -o enp2s0f1.[0-9]+); do echo $i; sudo ip link del $i; done

for i in $(lxc network ls --format csv | awk -F, '{ print $1 }' | grep -v lxdbr0); do echo $i;lxc network delete $i; done

cat reset_nettopd_go.sql | mysql -uroot -pwelcome nettopd_go

rm *.log
