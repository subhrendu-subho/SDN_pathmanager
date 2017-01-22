from mininet.topo import Topo
from mininet.net import Mininet
import networkx as nx
from mininet.link import TCLink
from mininet.util import custom
import matplotlib.pyplot as plt
import pickle
import random


def main():
    "Topology for a networkx network with a given filename."
    custom=pickle.load(open("input/sample.pickle", "r"))
    '''
    net = Mininet( topo=custom,
                   build=False,
                   ipBase='10.0.0.0/8')
    '''

