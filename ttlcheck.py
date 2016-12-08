#!/usr/bin/env python
#
# TTL check
#
# Looking for TTL modifier devices
#
# Written by Andras Majdan
# Bug reports to: majdan.andra@gmail.com
#
from __future__ import with_statement
from multiprocessing import Process, Manager, Lock
import os.path
import sys, socket
import pcap, dpkt

if len(sys.argv) != 4:
	print "Usage: ./ttlcheck.py <ttl min> <ttl diff> <iface name or pcap file>"
	exit(1);

ttlmin = int(sys.argv[1])
ttldiff = int(sys.argv[2])
dev = sys.argv[3]

manager = Manager()
ttls = manager.dict()
lock = Lock()

def proc_ipttl(ip, ttlstr, ttlmin, ttldiff):
	ret_res = "FAIL"
	ret_diff = "NA"
	ret_cause = " "

	ttl = list(ttlstr.split())
	
	if len(ttl) == 2:
		a = int(ttl[0])
		b = int(ttl[1])
		if (a < ttlmin) or (b < ttlmin):
			ret_cause += "MIN TTL "
		ret_diff = abs(int(ttl[0]) - int(ttl[1]))
		if ret_diff != ttldiff:
			ret_cause += "DIFF TTL " 
	else:
		ret_cause += "TTL NUM "
	
	if ret_cause == " ":
		ret_res = "OK"
	
	return ip, " ".join(sorted(ttl)), str(ret_diff), ret_res, ret_cause
		
		
	

def packet_capture(dev, lock):
	if os.path.isfile(dev):
		pcapfile = open(dev)
		pc = dpkt.pcap.Reader(pcapfile)
	else:
		pc = pcap.pcap(dev)
		pc.setfilter('icmp')

	for ts, pkt in pc:
		eth = dpkt.ethernet.Ethernet(pkt)
		if eth.type == dpkt.ethernet.ETH_TYPE_IP:
			ip = eth.data
			if ip.p == dpkt.ip.IP_PROTO_ICMP:
 				icmp = ip.data
				if icmp.type == dpkt.icmp.ICMP_ECHO:
					ipaddr = socket.inet_ntoa(ip.src)
					# Cannot use set and other containers here because
					# of a Python bug fixed in upcoming Python 3.6
					with lock:
						if not ipaddr in ttls:
							ttls[ipaddr] = str(ip.ttl);
						else:
							tmpset = set(ttls[ipaddr].split())
							tmpset.add(str(ip.ttl))
							ttls[ipaddr] = " ".join(tmpset)

pktcap = Process(target=packet_capture, args=(dev,lock,))
pktcap.start()

print "ttlcheck interactive shell\n"
while(True):
	cmd = raw_input("ttlcheck " + dev + "> ")
	if cmd == "quit":
		break;
	elif cmd == "help":
		print "Commands:"
		print "help\t\tPrint help"
		print "print\t\tPrint results"
		print "write <file>\tWrite results to file"
		print "quit\t\tQuit"
	elif cmd == "print":
		print "IP address\tTTL\tDiff\tResult\tCause"
		if ttls:
			with lock:
				for k in ttls.keys() :
					ip, ttl, diff, res, cause = proc_ipttl(k, ttls[k], ttlmin, ttldiff)
					print ip + "\t" + ttl + "\t" + diff + "\t" + res + "\t" + cause
	elif cmd.startswith("write ") and len(cmd)>6:
		filename = cmd[6:]
		
		if ttls:
			with lock:
				f = open(filename, "w")
				for k in ttls.keys() :
					ip, ttl, diff, res, cause = proc_ipttl(k, ttls[k], ttlmin, ttldiff)
					f.write(ip + ";" + ttl + ";" + diff + ";" + res + ";" + cause + "\n")
				f.close()

	elif cmd != "":
		print "Invalid command!"
		print "Type 'help' for list of commands"

pktcap.terminate()
