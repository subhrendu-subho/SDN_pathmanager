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
    c1=net.addController(name='c1',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    c0=net.addController(name='c0',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)

    info( '*** Add links\n')
    s1h1 = {'bw':30}
    net.addLink(s1, h1, cls=TCLink , **s1h1)
    s1s2 = {'bw':50}
    net.addLink(s1, s2, cls=TCLink , **s1s2)
    s2s3 = {'bw':50}
    net.addLink(s2, s3, cls=TCLink , **s2s3)
    s3h2 = {'bw':50}
    net.addLink(s3, h2, cls=TCLink , **s3h2)
    s6s5 = {'bw':50}
    net.addLink(s6, s5, cls=TCLink , **s6s5)
    s5s4 = {'bw':50}
    net.addLink(s5, s4, cls=TCLink , **s5s4)
    h1s6 = {'bw':40}
    net.addLink(h1, s6, cls=TCLink , **h1s6)
    s4h2 = {'bw':50}
    net.addLink(s4, h2, cls=TCLink , **s4h2)
    s2h3 = {'bw':10}
    net.addLink(s2, h3, cls=TCLink , **s2h3)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s3').start([c0])
    net.get('s4').start([c1])
    net.get('s5').start([c1])
    net.get('s6').start([c1])
    net.get('s1').start([c0])
    net.get('s2').start([c0])

    info( '*** Post configure switches and hosts\n')
    return(net)

    #CLI(net)
    #net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
topos = { 'myNetwork': ( lambda: myNetwork() ) }
