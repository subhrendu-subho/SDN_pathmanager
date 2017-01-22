#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)

    info( '*** Add links\n')
    h1s1 = {'bw':20,'delay':'5'}
    net.addLink(h1, s1, cls=TCLink , **h1s1)
    s1s2 = {'bw':20,'delay':'5'}
    net.addLink(s1, s2, cls=TCLink , **s1s2)
    s2s3 = {'bw':20,'delay':'5'}
    net.addLink(s2, s3, cls=TCLink , **s2s3)
    s3h2 = {'bw':20,'delay':'5'}
    net.addLink(s3, h2, cls=TCLink , **s3h2)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([])
    net.get('s3').start([])
    net.get('s2').start([])

    info( '*** Post configure switches and hosts\n')
    return(net)

    #CLI(net)
    #net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
topos = { 'myNetwork': ( lambda: myNetwork() ) }
