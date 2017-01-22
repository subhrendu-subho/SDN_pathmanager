python util/plot_rate.py -f results/h1_bwm.txt --out results/h1_bwm.png -i "h1-eth*" &
python util/plot_rate.py -f results/h2_bwm.txt --out results/h2_bwm.png -i "h2-eth*" &
python util/plot_tcpprobe.py -f results/h1_tcp_probe.txt --out results/h1_tcpprobe.png &
python util/plot_tcpprobe.py -f results/h2_tcp_probe.txt --out results/h2_tcpprobe.png &
python util/plot_pcap_rtt.py --files results/c0.pcap --out results/c0_rtt.png &
python util/plot_pcap_rtt.py --files results/h2-eth1.pcap --out results/h2-eth1_rtt.png &
python util/plot_pcap_rtt.py --files results/h1-eth1.pcap --out results/h1-eth1_rtt.png &
python util/plot_pcap_rtt.py --files results/c1.pcap --out results/c1_rtt.png &
python util/plot_pcap_rtt.py --files results/h1-eth0.pcap --out results/h1-eth0_rtt.png &
python util/plot_pcap_rtt.py --files results/h2-eth0.pcap --out results/h2-eth0_rtt.png &

