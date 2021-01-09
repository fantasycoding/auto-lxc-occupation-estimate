#!/usr/bin/env python3

import json
import random
import math

template_json = """
{
  "netid": "n1",
  "routers": [
    {
      "category": "VirRouter",
      "name": "r1",
      "interfaces": [
        {
          "name": "r1-eth0",
          "ip": "100.0.101.1",
          "mask": "24",
          "bw": "10000M"
        },
        {
          "name": "r1-eth1",
          "ip": "100.0.1.1",
          "mask": "24",
          "bw": "1000M"
        },
        {
          "name": "r1-eth2",
          "ip": "100.0.6.2",
          "mask": "24",
          "bw": "1000M"
        },
        {
          "name": "r1-eth3",
          "ip": "100.0.201.1/24"
        }
      ],
      "routings": {
        "ospf": [
          "network 0.0.0.0/0"
        ]
      }
    }
  ],
  "switches": null,
  "hosts": [
    {
      "category": "AlpineBase",
      "name": "h1",
      "interfaces": [
        {
          "name": "h1-eth0",
          "ip": "100.0.201.2/24"
        }
      ],
      "apps": [
        {
          "key": "ITGSend",
          "value": "-T UDP -a 100.0.204.2 -c 100 -C 10 -t 15000"
        }
      ]
    }
  ],
  "links": [
    {
      "from": "r1-eth0",
      "to": "r7-eth0"
    }
  ]
}
"""

def genTopo(id, router_num, host_num, link_num):
    topo = {
        "netid": id,
        "routers": [],
        "switches": [],
        "hosts": [],
        "links": []
    }

    nodenum = router_num + host_num
    routerids = {}
    hostids = {}
    idnodes = {}

    for i in range(router_num):
        routerids['r' + str(i)] = i
        idnodes[i] = 'r' + str(i)
    for i in range(host_num):
        hostids['h' + str(i)] = i + router_num
        idnodes[i + router_num] = 'h' + str(i)
    
    linkmap = [[0 for i in range(nodenum)] for j in range(nodenum)]

    if link_num < 0 or link_num > (nodenum * (nodenum - 1) / 2):
        print("Link num is invalid for {}: {}".format(nodenum, link_num))
        return

    for i in range(link_num - host_num):
        fromnode, tonode = 0, 0 
        while fromnode == tonode or linkmap[fromnode][tonode] == 1:
            fromnode = random.randint(0, router_num - 1)
            tonode = random.randint(0, router_num - 1)
        linkmap[fromnode][tonode] = i + 1
        linkmap[tonode][fromnode] = i + 1

    for (_, hostid) in hostids.items():
      fromnode = hostid
      tonode = random.randint(0, router_num - 1)
      linkmap[fromnode][tonode] = i + 1
      linkmap[tonode][fromnode] = i + 1
      i += 1

    # print(linkmap)
    for i in range(nodenum):
        ethind = 0
        for j in range(nodenum):
            if linkmap[i][j] == 0:
                linkmap[i][j] = []
            else:
                linkmap[i][j] = [idnodes[i] + "-eth" + str(ethind), linkmap[i][j]]
                ethind += 1

    # print(linkmap)
    for (nodename, nodeid) in routerids.items():
        router = {
            "name": nodename,
            "category": "VirRouter",
            "interfaces": [],
            "routings": {
                "ospf": ["network 0.0.0.0/0 area 0"]
            }
        }
        for j in range(nodenum):
            if len(linkmap[nodeid][j]) != 0:
                router["interfaces"].append({
                    "name": linkmap[nodeid][j][0],
                    "ip": "10.{}.{}.{}".format(linkmap[nodeid][j][1] // 255, linkmap[nodeid][j][1] % 255, 1 if nodeid < j else 2),
                    "mask": "24",
                    "bw": "1000"
                })
        topo["routers"].append(router)

    for (nodename, nodeid) in hostids.items():
        host = {
            "name": nodename,
            "category": "AlpineBase",
            "interfaces": [],
            "apps": []
        }
        for j in range(nodenum):
            if len(linkmap[nodeid][j]) != 0:
                host["interfaces"].append({
                    "name": linkmap[nodeid][j][0],
                    "ip": "10.{}.{}.{}".format(linkmap[nodeid][j][1] // 255, linkmap[nodeid][j][1] % 255, 1 if nodeid < j else 2),
                    "mask": "24",
                    "bw": "1000"
                })
        topo["hosts"].append(host)

    for i in range(nodenum):
        for j in range(i + 1, nodenum):
            if len(linkmap[i][j])!= 0:
                topo["links"].append({
                    "from": linkmap[i][j][0],
                    "to": linkmap[j][i][0]
                })

    return topo

def checkTopo(name, topo):
    links = topo["links"]
    for link in links:
        fromname, toname = link["from"], link["to"]
        fromnode, tonode = None, None
        for router in topo["routers"]:
            if router["name"] == fromname.split("-")[0]:
                fromnode = router
            elif router["name"] == toname.split("-")[0]:
                tonode = router
        for host in topo["hosts"]:
            if host["name"] == fromname.split("-")[0]:
                fromnode = host
            elif host["name"] == toname.split("-")[0]:
                tonode = host
        if fromnode == None or tonode == None:
            print("{} Check Failed! Node {} or {} doesn't exist!".format(name, fromname, toname))
            return False
        frominterface, tointerface = None, None
        for interface in fromnode["interfaces"]:
            if interface["name"] == fromname:
                frominterface = interface
        for interface in tonode["interfaces"]:
            if interface["name"] == toname:
                tointerface = interface
        if frominterface == None or tointerface == None:
            print("{} Check Failed! Interface {} or {} doesn't exist!".format(name, fromname, toname))
            return False
        if frominterface["ip"].split(".")[:3] != tointerface["ip"].split(".")[:3]:
            print("{} Check Failed! IP {} or {} doesn't fit!".format(name, fromname, toname))
            return False
    print("{} Check OK!".format(name))
    return True

name = "n10"
node_num = 10
router_num = int(0.6 * node_num)
host_num = node_num - router_num

link_lowerbound = host_num + router_num - 1
link_upperbound = host_num + math.floor(router_num * (router_num - 1) / 6)

link_num = random.randint(link_lowerbound, link_upperbound)
topo = genTopo(name, router_num, host_num, link_num)
if checkTopo(name, topo):
    with open(name + ".json", "w") as f:
        f.write(json.dumps(topo, indent=4))
