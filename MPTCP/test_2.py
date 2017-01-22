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

    c3=net.addController(name='c3',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    c2=net.addController(name='c2',
                      controller=Controller,
                      protocol='tcp',
                      port=6633)

    info( '*** Add switches\n')
    s6 = net.addSwitch('s6', cls=OVSKernelSwitch)
    s11 = net.addSwitch('s11', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)
    s8 = net.addSwitch('s8', cls=OVSKernelSwitch)
    s9 = net.addSwitch('s9', cls=OVSKernelSwitch)
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s7 = net.addSwitch('s7', cls=OVSKernelSwitch)
    s10 = net.addSwitch('s10', cls=OVSKernelSwitch)
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch)
    s12 = net.addSwitch('s12', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch)

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)

    info( '*** Add links\n')
    h1s12 = {'bw':20,'delay':'2','loss':0}
    net.addLink(h1, s12, cls=TCLink , **h1s12)
    net.addLink(h1, s1, cls=TCLink , **h1s12)
    net.addLink(h1, s6, cls=TCLink , **h1s12)
    net.addLink(h1, s7, cls=TCLink , **h1s12)

    s3h2 = {'bw':50,'delay':'2','loss':0}
    net.addLink(s3, h2, cls=TCLink , **s3h2)
    net.addLink(s4, h2, cls=TCLink , **s3h2)
    net.addLink(s10, h2, cls=TCLink , **s3h2)
    net.addLink(s9, h2, cls=TCLink , **s3h2)

    net.addLink(s1, s2, cls=TCLink , **s3h2)
    net.addLink(s2, s3, cls=TCLink , **s3h2)
    net.addLink(s5, s4, cls=TCLink , **s3h2)
    net.addLink(s6, s5, cls=TCLink , **s3h2)
    net.addLink(s7, s8, cls=TCLink , **s3h2)
    net.addLink(s8, s9, cls=TCLink , **s3h2)
    net.addLink(s12, s11, cls=TCLink , **s3h2)
    net.addLink(s11, s10, cls=TCLink , **s3h2)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s6').start([c1])
    net.get('s11').start([c3])
    net.get('s2').start([c0])
    net.get('s8').start([c2])
    net.get('s9').start([c2])
    net.get('s1').start([c0])
    net.get('s7').start([c2])
    net.get('s10').start([c3])
    net.get('s5').start([c1])
    net.get('s12').start([c3])
    net.get('s3').start([c0])
    net.get('s4').start([c1])

    info( '*** Post configure switches and hosts\n')
    return(net)

    #CLI(net)
    #net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()
topos = { 'myNetwork': ( lambda: myNetwork() ) }
