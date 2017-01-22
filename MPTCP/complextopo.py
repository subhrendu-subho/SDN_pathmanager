from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.util import custom
import networkx as nx
import pickle
import random

# Topology to be instantiated in Mininet
class ComplexTopo(Topo):
    "Mininet Complex Topology"

    def __init__(self, cpu=.1, max_queue_size=None, **params):

        # Initialize topo
        Topo.__init__(self, **params)

        #TODO: Create your Mininet Topology here!
        H= pickle.load(open('input/input.pkl'))# CheckPoint
        # Hosts and switches
	hostConfig = {'cpu': cpu}
        s ={u:self.addSwitch('s'+u) for u in H.nodes()}
        sender = self.addHost('sender', **hostConfig)
        receiver = self.addHost('receiver', **hostConfig)
#	Links 
#       linkConfig = {'bw': 10, 'delay': '1ms', 'loss': 0,'max_queue_size': max_queue_size }
        for u,v in list(set(H.edges())):
        	link_info=H[u][v]
        	
