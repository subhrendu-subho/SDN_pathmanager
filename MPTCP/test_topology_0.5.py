#!/usr/bin/python
"""
RTT throughtput testing for mptcp
"""

import sys
from subprocess import Popen, PIPE, call
from time import sleep
import termcolor as T
import argparse
import random
import re
import netifaces
from itertools import chain

from mininet.net import Mininet
from mininet.log import lg
#from mininet.node import OVSKernelSwitch as Switch
from mininet.node import UserSwitch as Switch
from mininet.link import Link, TCLink, Intf
from mininet.util import makeNumeric, custom
from mininet.cli import CLI
from functools import partial
#from topo import TwoHostNInterfaceTopo
from mininet.node import Controller, RemoteController,OVSController
from mininet.topo import Topo

sys.path.append('topos')
#import Switch6_part1 as sw_net
#import basic2switch as sw_net
#import Switch4_part3 as sw_net
#import Switch4_part4 as sw_net
#import Switch4_part5 as sw_net
#import S4C1_remote as sw_net
import Switch4_part8 as sw_net
#import Switch4_part5B as sw_net
#import Switch4_part5C as sw_net
#import Switch4_1cntlr as sw_net
#import Switch4_part6 as sw_net
#import Switch4_part7 as sw_net
import framework
#import Switch12_part3 as sw_net
#import test_4 as sw_net
#############################################################################
def monitor_controller(net):
    cnt_process_name_list=[ "mininet:"+c.name for c in net.controllers]
    for pname in cnt_process_name_list:
    	Popen(["sh","watch_controller_usage.sh",pname,"&"])
    return
#############################################################################

def main():
    framework.preconfigure()
    args = framework.parse_args()
    lg.setLogLevel('info')
    net = sw_net.myNetwork()
    hIpDict=framework.getAllIP(net)
    lg.info("Before configuring routing table")
    framework.pingAllIP(hIpDict,1)
    if(len(net.controllers)>1):
	framework.run_configure(args,net)
    else:
    	framework.run_configure_single_nw(args,net)
    hIpDict=framework.getAllIP(net)
    lg.info("After configuring routing table")
    framework.pingAllIP(hIpDict,3)
    pathA=False
    call(["sysctl", "-w", "net.ipv4.tcp_congestion_control=balia"])
    %system sh clean.sh
    %system /etc/init.d/networking restart
    %system cat /dev/null > /var/log/kern.log
    net.getNodeByName("h1").cmdPrint("iperf -s &")
    framework.start_dataCollection(net,"")
    net.getNodeByName("h2").cmdPrint("sleep 5; iperf -c 10.0.0.1 -i 2 -t 100 -m  > results/h2_iperf.txt")
    %system cat /var/log/kern.log |grep "mptcp_balia_recalc_ai 183" > results/kernel.txt
    %system wc -l results/kernel.txt
    %system cat /var/log/kern.log |grep "mptcp" > results/kernel_mptcp.txt
    framework.stop_dataCollection(net)
    net.stop()
    %system cat /dev/null > /var/log/kern.log
    framework.end(args)

#############################################################################
if __name__ == '__main__':
    main()
#############################################################################
