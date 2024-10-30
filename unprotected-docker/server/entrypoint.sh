#!/bin/sh

# Configure iptables rules
# Drop connections if more than 20 concurrent connections are established on port 5000
iptables -A INPUT -p tcp --dport 5000 -m connlimit --connlimit-above 20 -j DROP

# Set a rate limit to allow 25 connections per minute, with bursts of up to 100
iptables -A INPUT -p tcp --dport 5000 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT

# Detect potential DDoS attempts and temporarily blacklist IPs with excessive connections
# Track each IP: if an IP makes 20 or more new connections in 35 seconds, drop all further packets from that IP
iptables -A INPUT -p tcp --dport 5000 -m state --state NEW -m recent --set --name blacklist
iptables -A INPUT -p tcp --dport 5000 -m state --state NEW -m recent --update --seconds 35 --hitcount 20 --name blacklist -j DROP

# Permanently blacklist any IP that exceeds 100 connections in 60 seconds
iptables -A INPUT -p tcp --dport 5000 -m state --state NEW -m recent --set --name permanent_blacklist
iptables -A INPUT -p tcp --dport 5000 -m state --state NEW -m recent --update --seconds 70 --hitcount 100 --name permanent_blacklist -j DROP

# Configure UFW to allow only port 5000 and enable logging
ufw allow 5000/tcp
ufw --force enable
ufw logging on

# Start the application
python /app/webapp.py
