#!/usr/bin/python
"""
Test to validate MPTCP operation in given topology.
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
import netifaces

from mininet.net import Mininet
from mininet.log import lg
from mininet.node import OVSKernelSwitch as Switch
#from mininet.node import UserSwitch as Switch
from mininet.link import Link, TCLink
from mininet.util import makeNumeric, custom
from mininet.cli import CLI
from functools import partial
#from topo import TwoHostNInterfaceTopo
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import Controller, RemoteController,OVSController
from mininet.topo import Topo
##################################
#c2 = OVSController( 'c2', ip='127.0.0.1' )
#c2=RemoteController( 'c2', ip='172.16.116.79' )
#############################################################################
# TODO: move to common location; code shared with DCTCP.
def progress(t):
    while t > 0:
        print T.colored('  %3d seconds left  \r' % (t), 'cyan'),
        t -= 1
        sys.stdout.flush()
        sleep(1)
    print '\r\n'
#############################################################################
class MultiSwitch( Switch ):
    "Custom Switch() subclass that connects to different controllers"
    def start( self, controllers ):
    	try:
        	return Switch.start( self, [ cmap[ self.name ] ] )
        except Exception, e:
	        return Switch.start(self, [c0])
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
    	sysctl_set("net.mptcp.mptcp_path_manager", "default")
    #sysctl_set("net.mptcp.mptcp_ndiffports", ports)
#############################################################################
def parse_args():
    parser = argparse.ArgumentParser(description="MPTCP 2-host n-switch test")
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
                        default=2)
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
#############################################################################
def end(args):
    set_mptcp_enabled(False)
    set_mptcp_ndiffports(1)
#############################################################################
def checkAllSwitchConnected(net):
    for sw in net.switches:
       lg.info("Switch="+sw.name+" Connected="+str(sw.connected())+"\n")
#############################################################################
def startSwitchesWithControllers(net,cmap):
    for sw in net.switches:
       try:
           ctlr=cmap[sw.name]
       except Exception, e:
	   ctlr=net.controllers[0]
       sw.start([ctlr])
       lg.info("Switch="+sw.name+" Controller="+ctlr.name+" Connected="+str(sw.connected())+"\n")
#############################################################################
#############################################################################
def run_configure(args, net):
	seconds = int(args.t)
	hosts=net.hosts
	switches=net.switches
	#h1 = net.getNodeByName('h1')
	counter=0
	for hid,h in enumerate(hosts):
		name=h.name
		intfs= { id:intf for (id,intf) in h.intfs.iteritems() if intf.name!='lo'}
		for i in intfs.keys():
		# Setup IPs:
			h.cmdPrint('ifconfig %s-eth%i 10.0.%i.%i netmask 255.255.0.0' % (name,i, i,(hid+1)))
			if args.mptcp:
			    lg.info("configuring source-specific routing tables for MPTCP\n")
			    # This creates two different routing tables, that we use based on the
			    # source-address.
			    dev = '%s-eth%i' % (name,i)
			    table = '%s' % (i + 1)
			    ####################### CHANGE THE GRAPH First
			    #######################START TEST
			    h.cmdPrint('ip rule add from 10.0.%i.%i table %s' % (i,(hid+1), table))
			    h.cmdPrint('ip route add 10.0.%i.0/16 dev %s scope link table %s' % (i, dev, table))
			    h.cmdPrint('ip route add default via 10.0.%i.1 dev %s table %s' % (i, dev, table))
			    #######################END TEST


	# TODO: expand this to verify connectivity with a ping test.
	lg.info("pinging each destination interface\n")
	net.pingFull()
	lg.info("tcpdump\n")
	#h1.sendCmd("tcpdump -w server.pcap")
	#h2.sendCmd("tcpdump -w client.pcap")
	CLI(net)
	#sleep(1.0)  # hack to wait for iperf server output.
#############################################################################
def run(args, net):
    seconds = int(args.t)
    h1 = net.getNodeByName('h1')
    h2 = net.getNodeByName('h2')
    s1 = net.getNodeByName('s1')
    s2 = net.getNodeByName('s2')

    for i in range(args.n):
        # Setup IPs:
        #h1.cmdPrint('ifconfig h1-eth%i 10.0.%i.3 netmask 255.255.255.0' % (i, i))
        #h2.cmdPrint('ifconfig h2-eth%i 10.0.%i.4 netmask 255.255.255.0' % (i, i))

        if args.mptcp:
            lg.info("configuring source-specific routing tables for MPTCP in Node %s\n"  % (i + 1))
            # This creates two different routing tables, that we use based on the
            # source-address.
#           dev = 'h1-eth%i' % i
            #table = '%s' % (i + 1)
#            h1.cmdPrint('ip rule add from 10.0.%i.3 table %s' % (i, table))
#            h1.cmdPrint('ip route add 10.0.%i.0/24 dev %s scope link table %s' % (i, dev, table))
#            h1.cmdPrint('ip route add default via 10.0.%i.1 dev %s table %s' % (i, dev, table))

    # TODO: expand this to verify connectivity with a ping test.
#    lg.info("pinging each destination interface\n")
#    for i in range(args.n):
#        h2_out = h2.cmd('ping -c 1 10.0.%i.3' % i)
#        lg.info("ping test output: %s\n" % h2_out)

    lg.info("iperfing\n")
    cmd1='iperf -s'
    lg.info("h1.sendCmd(%s)\n" % cmd1)
    h1.sendCmd(cmd1)
    cmd2= 'iperf -c 10.0.0.4 -t %d -i 1' % seconds
    lg.info("h2.sendCmd(%s)\n" % cmd2)
    h2.sendCmd(cmd2)

    progress(seconds + 1)
    h1_out = h1.waitOutput()
    lg.info("client output:\n%s\n" % h1_out)
    sleep(0.1)  # hack to wait for iperf server output.
    #out=""
    out = h2.read(10000)
    lg.info("server output: %s\n" % out)
    return None
#############################################################################
def genericTest(args, topo, setup, run, end):
    link = custom(TCLink, bw=args.bw)
    #net = Mininet(topo=topo, switch=MultiSwitch, link=link, xterms=True, cleanup=True)
    net = Mininet(topo=topo, switch=Switch, controller = None, link=link,build=True, xterms=False, cleanup=True,waitConnected = False )
    lg.info( '*** Adding controller\n' )
    c0=net.addController(name='c0',
                      controller=OVSController,
                      protocol='tcp',
                      port=6633)
    

    c1=net.addController(name='c1',
                      controller=Controller,
                      protocol='tcp',
                      port=6634)
    c1=RemoteController( name='odl', ip='172.16.116.79' )
    net.addController(c1)
    cmap = { 's_0': c1, 's_1': c1, 's_2': c1 , 's_3': c1 , 's_4' : c1,  's_5':c0, 's_6':c0, 's_7': c0 ,'s_8': c0 ,'s_9': c0 }
    cmap = { 's_0': c1, 's_1': c1, 's_2': c1 , 's_3': c1 , 's_4' : c1,  's_5':c1, 's_6':c1, 's_7': c1 ,'s_8': c1 ,'s_9': c1 }

    #for c in [ c0, c1 ]:
    #net.addController(c2)
    #net.addController("ovs_ctrl",controller=OVSController)
    #net = Mininet(topo=topo, switch=Switch, link=link, xterms=False, cleanup=True)
    setup(args)
    #net.build()
    lg.info( '*** Starting network\n')
    #net.build()
    lg.info( '*** Starting controllers\n')
    for cntrlr in net.controllers:
        if cntrlr.checkListening() ==None:
	    lg.info("Controller ["+cntrlr.name+"] is Running\n")
        else:
	    cntrlr.start()
	    lg.info("Controller ["+cntrlr.name+"] Started\n")

    lg.info( '*** Starting switches\n')
    startSwitchesWithControllers(net,cmap)
    checkAllSwitchConnected(net)

    if args.pause:
        print "press enter to run test"
        raw_input()
    
    data = run_configure(args, net)
    #data = run(args, net)
    
    if args.pause:
        print "press enter to finish test"
        raw_input()
    net.stop()
    end(args)
    return data
#############################################################################
def main():
    args = parse_args()
    lg.setLogLevel('info')
    topo = pickle.load(open('input/topology_small.pkl'))
    if args.draw:
    	drawTopology(topo)
#    topo = TwoHostNInterfaceTopo(n=args.n)
    genericTest(args, topo, setup, run, end)
#############################################################################
if __name__ == '__main__':
    main()
#############################################################################
