#!/usr/bin/python
"""
Plot results
"""

import glob, os
from subprocess import Popen, PIPE
#############################################################################
os.chdir("results/")
#########################################
""" Plot bandwidth """
for file in glob.glob("*_bwm.txt"):
    hname=file.replace("_bwm.txt","")
    devs="\"%s-eth*\""%(hname)
    cmd="python util/my_plot_rate.py -f results/%s_bwm.txt --out results/%s_bwm.png -i %s &" %(hname,hname,devs)
    print cmd
    #Popen(cmd)
#########################################
""" Plot tcpprobes """
for file in glob.glob("*_tcp_probe.txt"):
    hname=file.replace("_tcp_probe.txt","")
    cmd= "python util/plot_tcpprobe.py -f results/%s_tcp_probe.txt --out results/%s_tcpprobe.png &" %(hname,hname)
    print cmd
    #Popen(cmd)
#########################################
""" Plot RTT """
for file in glob.glob("*.pcap"):
    hname=file.replace(".pcap","")
    cmd= "python util/plot_pcap_rtt.py --files results/%s.pcap --out results/%s_rtt.png &"%(hname,hname)
    print cmd
    #Popen(cmd)
#############################################################################
