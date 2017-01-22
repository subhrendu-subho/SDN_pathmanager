#!/usr/bin/python
"""
RTT throughtput testing for mptcp
"""

import sys
from subprocess import Popen, PIPE
from time import sleep
import termcolor as T
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import pickle
import random
import re
import netifaces

from mininet.net import Mininet
from mininet.log import lg
#from mininet.node import OVSKernelSwitch as Switch
from mininet.node import UserSwitch as Switch
from mininet.link import Link, TCLink
from mininet.util import makeNumeric, custom
from mininet.cli import CLI
from functools import partial
#from topo import TwoHostNInterfaceTopo
from mininet.node import Controller, RemoteController,OVSController
from mininet.topo import Topo
import Switch6_part2 as sw_net
#############################################################################
def get_hID(host):
    name=host.name
    hid=re.findall(r'\d+', name)
    return int(hid[0])
#############################################################################
def start_tcpdump_controllers(controllers):
    #sudo tcpdump -w h3-eth0.pcap -i h3-eth0 &
    for n in controllers:
        n.cmdPrint("tcpdump -n \"dst host %s and port %s\" -w results/%s.pcap &" %(n.IP(), n.port, n.name))
#############################################################################
def start_tcpdump(nodes):
    #sudo tcpdump -w h3-eth0.pcap -i h3-eth0 &
    for n in nodes:
        intfs= intfs= { id:intf for (id,intf) in h.intfs.iteritems() if intf.name!='lo'}
        for i in intfs.keys():
            dev = '%s-eth%i' % (n.name,i)
            n.cmdPrint("tcpdump -w %s.pcap -i %s &" %(dev,dev))
#############################################################################
def stop_tcpDump(nodes):
    for n in nodes:
        n.cmdPrint("killall -9 tcpdump")
#############################################################################
def start_tcpprobe(nodes):
    for n in nodes:
        n.cmd("rmmod tcp_probe 1>/dev/null 2>&1; modprobe tcp_probe")
        n.cmd("cat /proc/net/tcpprobe > results/%s_tcp_probe.txt" % (n.name))
#############################################################################
def stop_tcpprobe(nodes):
    for n in nodes:
        n.cmd("killall -9 cat; rmmod tcp_probe")
#############################################################################
def start_monitor(hosts):
    """Uses bwm-ng tool to collect iface tx rate stats.  Very reliable."""
    #bwm-ng -t 1000 -o csv -u bits -T rate -C 
    for n in hosts:
        n.cmd("bwm-ng -t 1000 -o csv -u bits -T rate -C > results/%_bwm.txt"%(n.name))
#############################################################################
def stop_monitor(hosts):
    for n in hosts:
        n.cmd("killall -9 bwm-ng")
#############################################################################
def start_dataCollection(net):
    start_tcpdump_controllers(net.controllers)
    start_tcpdump(net.hosts)
    start_tcpprobe(net.hosts)
    start_monitor(net.hosts)
#############################################################################
def stop_dataCollection(net):
    stop_tcpdump_controllers(net.controllers)
    stop_tcpdump(net.hosts)
    stop_tcpprobe(net.hosts)
    stop_monitor(net.hosts)
#############################################################################
def sysctl_set(key, value):
    """Issue systcl for given param to given value and check for error."""
    p = Popen("sysctl -w %s=%s" % (key, value), shell=True, stdout=PIPE,
              stderr=PIPE)
    # Output should be empty; otherwise, we have an issue.  
    stdout, stderr = p.communicate()
    stdout_expected = "%s = %s\n" % (key, value)
    if stdout != stdout_expected:
        raise Exception("Popen returned unexpected stdout: %s != %s" %
                        (stdout, stdout_expected))
    if stderr:
        raise Exception("Popen returned unexpected stderr: %s" % stderr)
#############################################################################
def set_mptcp_enabled(enabled):
    """Enable MPTCP if true, disable if false"""
    e = 1 if enabled else 0
    lg.info("setting MPTCP enabled to %s\n" % e)
    sysctl_set('net.mptcp.mptcp_enabled', e)
#############################################################################
def set_mptcp_ndiffports(ports):
    """Set ndiffports, the number of subflows to instantiate"""
    lg.info("setting MPTCP ndiffports to %s\n" % ports)
    if(ports !=1):
    	sysctl_set("net.mptcp.mptcp_path_manager", "ndiffports")
    else:
    	sysctl_set('net.mptcp.mptcp_path_manager','fullmesh')
    #sysctl_set("net.mptcp.mptcp_ndiffports", ports)
#############################################################################
def parse_args():
    parser = argparse.ArgumentParser(description="MPTCP 2-host 2-path 6-switch test")
    parser.add_argument('--bw', '-B',
                        action="store",
                        help="Bandwidth of links",
                        default=10)
#                        required=True)
    
    parser.add_argument('-n',
                        action="store",
                        help="Number of switches.  Must be >= 2",
                        default=2)
    
    parser.add_argument('-t',
                        action="store",
                        help="Seconds to run the experiment",
                        default=2)
    
    parser.add_argument('--mptcp',
                        action="store_true",
                        help="Enable MPTCP (net.mptcp.mptcp_enabled)",
                        default=True)
#                        default=False)

    parser.add_argument('--pause',
                        action="store_true",
                        help="Pause before test start & end (to use wireshark)",
                        default=False)

    parser.add_argument('--ndiffports',
                        action="store",
                        help="Set # subflows (net.mptcp.mptcp_ndiffports)",
                        default=1)
    parser.add_argument('--draw',
                        action="store_true",
                        help="Wheater visualization of topology is required (will be saved in topo.png/topo.dot)",
                        default=True)

    args = parser.parse_args()
    args.bw = float(args.bw)
    args.n = int(args.n)
    args.ndiffports = int(args.ndiffports)
    return args
#############################################################################
def setup(args):
    set_mptcp_enabled(args.mptcp)
    set_mptcp_ndiffports(args.ndiffports)
#############################################################################
def drawTopology(topo):
    G=topo.convertTo(nx.MultiGraph,data=True,keys=True)
    nx.write_dot(G,'topo.dot')
    !neato -T png topo.dot > topo.png
#########################################################################def get_hID(host):
    name=host.name
    hid=re.findall(r'\d+', name)
    return int(hid[0])
#############################################################################
####
def end(args):
    set_mptcp_enabled(False)
    set_mptcp_ndiffports(1)
#############################################################################
def checkAllSwitchConnected(net):
    for sw in net.switches:
       lg.info("Switch="+sw.name+" Connected="+str(sw.connected())+"\n")
#############################################################################
def run_configure(args, net):
	seconds = int(args.t)
	hosts=net.hosts
	for h in hosts:
		hid=get_hID(h)
		name=h.name
		intfs= { id:intf for (id,intf) in h.intfs.iteritems() if intf.name!='lo'}
		for i in intfs.keys():
		# Setup IPs:
			dev = '%s-eth%i' % (name,i)
			h.cmdPrint('ifconfig %s 10.0.%i.%i netmask 255.255.255.0' % (dev, i,hid))
			if args.mptcp:
			    lg.info("configuring source-specific routing tables for MPTCP\n")
			    # This creates two different routing tables, that we use based on the
			    # source-address.
			    table = '%s' % (i + 1)
			    ####################### CHANGE THE GRAPH First
			    #######################START TEST
			    h.cmdPrint('ip rule add from 10.0.%i.%i table %s' % (i,hid, table))
			    h.cmdPrint('ip route add 10.0.%i.0/24 dev %s scope link table %s' % (i, dev, table))
			    h.cmdPrint('ip route add default via 10.0.%i.1 dev %s table %s' % (i, dev, table))
#############################################################################
#############################################################################
#############################################################################
#############################################################################
#############################################################################
def main():
    args = parse_args()
    lg.setLogLevel('info')
    net = sw_net.myNetwork()
    net.pingAll()
    CLI(net)
    '''
    h1 ping 10.0.0.2 -c 5
    h1 ping 10.0.1.2 -c 5
    h2 ping 10.0.0.1 -c 5
    h2 ping 10.0.1.1 -c 5
    exit
    '''
    run_configure(args,net)
    start_dataCollection(net)
    CLI(net)
    '''
    h1 iperf -s&
    h2 iperf -c 10.0.0.1 -i 2 -t 100 -m -o results/h2_iperf_.txt
    h2 iperf -c 10.0.1.1 -i 2 -t 100 -m -o results/h2_iperf.txt
    '''
    stop_dataCollection(net)
    net.stop()
    end(args)

#############################################################################
if __name__ == '__main__':
    main()
#############################################################################
