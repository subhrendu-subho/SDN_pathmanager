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
import Switch4_part6 as sw_net
#import Switch4_part7 as sw_net
import framework
#import Switch12_part3 as sw_net
#import test_4 as sw_net
#############################################################################

def main():
    framework.preconfigure()
    args = framework.parse_args()
    lg.setLogLevel('info')
    net = sw_net.myNetwork()
    hIpDict=framework.getAllIP(net)
    lg.info("Before configuring routing table")
    framework.pingAllIP(hIpDict,1)

    framework.run_configure(args,net)
    hIpDict=framework.getAllIP(net)
    lg.info("After configuring routing table")
    framework.pingAllIP(hIpDict,3)
    pathA=None
    #####CLI(net)## for debugging
    '''
    h1 ping 10.0.0.2 -c 3
    h1 ping 10.0.1.2 -c 3
    h1 ping 10.0.2.2 -c 3
    h1 ping 10.0.3.2 -c 3
    h2 ping 10.0.0.1 -c 3
    h2 ping 10.0.1.1 -c 3
    h2 ping 10.0.2.1 -c 3
    h2 ping 10.0.3.1 -c 3
    exit
    '''
    #%system sysctl -w net.mptcp.mptcp_enabled=0
    #%system sysctl -a|grep mptcp
    #%system sysctl -w net.mptcp.mptcp_path_manager=ndiffports
    #call(["sysctl", "-w", "net.ipv4.tcp_congestion_control=lia"])
    
    pathA=False
    call(["sysctl", "-w", "net.ipv4.tcp_congestion_control=balia"])
    
    %system sh clean.sh
    %system /etc/init.d/networking restart
    %system cat /dev/null > /var/log/kern.log
    #net.getNodeByName("h1").cmdPrint("iperf3 -s&")
    net.getNodeByName("h1").cmdPrint("iperf -s&")
    framework.start_dataCollection(net,"")
    if(pathA!=None):
	    if(pathA):
	    	print("Use Path A")
	    	net.getNodeByName("h2").cmdPrint("iperf3 -Z -c 10.0.0.1 -i 2 -t 100 > results/h2_iperf.txt &")
	    else:
	    	print("Use Path B")
	    	net.getNodeByName("h2").cmdPrint("iperf3 -Z -c 10.0.1.1 -i 2 -t 100 > results/h2_iperf.txt &")
    	    #net.getNodeByName("h3").cmdPrint("sh scripts_for_hosts/udpGenerator.sh")
    else:
    	CLI(net)
    '''
    h3 iperf3 -Z -c 10.0.0.1 -u -b 5m -i 2 -t 0 &
    #xterm h1 h2 h3
    #h3 iperf3 -Z -c 10.0.0.1 -i 2 -t 50 > results/h3_iperf.txt &
    h2 iperf -c 10.0.0.1 -i 2 -t 100 -m -F mptcpClientServer/h1-eth1.pcap > results/h2_iperf.txt
    h2 iperf -c 10.0.0.1 -i 2 -t 100 -m > results/h2_iperf.txt
    h2 iperf -c 10.0.1.1 -i 2 -t 100 -m > results/h2_iperf.txt  
    #h2 iperf3 -Z -c 10.0.0.1 -i 2 -t 100 > results/h2_iperf.txt 
    #h2 iperf3 -Z -c 10.0.1.1 -i 2 -t 100 > results/h2_iperf.txt 
    #h2 iperf3 -Z -c 10.0.2.1 -i 2 -t 100 > results/h2_iperf.txt 
    #h2 iperf3 -Z -c 10.0.3.1 -i 2 -t 100 > results/h2_iperf.txt 
    exit
    '''
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
