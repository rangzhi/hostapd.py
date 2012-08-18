#!/usr/bin/env python2.7
import subprocess
from time import sleep
from config import IN,OUT,IP,NETMASK
from common_methods import exit_script
import sys
def start_hostapd():
	"""
	Configs the IN interface, starts dhcpd, configs iptables, Starts Hostapd
	"""
	print
	try:
		with open('/etc/py_hostapd.conf') as f: pass
	except IOError as e:
		exit_error('[ERROR] /etc/py_hostapd.conf doesn\'t exist')
	
	# Configure network interface
	print 'configuring',IN,'...'
	setup_wlan = subprocess.Popen(['ifconfig', IN, 'up', IP, 'netmask', NETMASK])
	sleep(1)
	dhcp_log = open('./dhcp.log', 'w')

	# Start dhcpd
	print 'Starting dhcpd...'
	dhcp_proc = subprocess.Popen(['dhcpd',IN],stdout = dhcp_log, stderr = dhcp_log) 
	sleep(1)
	dhcp_log.close();

	# Configure iptables
	print 'Configuring iptables...'
	subprocess.call(['iptables','--flush'])
	subprocess.call(['iptables','--table','nat','--flush'])
	subprocess.call(['iptables','--delete-chain'])
	subprocess.call(['iptables','--table','nat','--delete-chain'])
	subprocess.call(['iptables','--table','nat','--append','POSTROUTING','--out-interface',OUT,'-j','MASQUERADE'])
	subprocess.call(['iptables','--append','FORWARD','--in-interface',IN,'-j','ACCEPT'])
	subprocess.call(['sysctl','-w','net.ipv4.ip_forward=1'])
	
	# Start hostapd
	print 'Starting Hostapd...'
	hostapd_proc = subprocess.Popen(['hostapd -t -d /etc/py_hostapd.conf >./hostapd.log'],shell=True)
	print 'Done... (Hopefully!)'
	print

def stop_hostapd():
	"""
	Stops Hostapd and dhcpd
	"""
	print
	print 'Killing Hostapd...'
	subprocess.call(['killall','hostapd'])
	print 'Killing dhcpd...'
	subprocess.call(['killall','dhcpd'])
	print

def restart_hostapd():
	stop_hostapd()
	# Workaround for issues with dhcpd
	sleep(2)

	start_hostapd()
