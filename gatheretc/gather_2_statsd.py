#!/usr/bin/env python
import os
import sys
import datetime
import dateutil.parser
import socket
import tailer

STATES = {
    'offline': 0,
    'connected': 1,
    'syncing': 2,
    'tracking': 3,
    'full': 4
}

filename = os.environ['GATHER_OUT_FILE'] or 'gather.out'
statsd_host = os.environ['STATSD_HOST']
statsd_port = int(os.environ['STATSD_PORT'])
statsd_path = os.environ['STATSD_PATH']

sock = socket.socket()
sock.connect((statsd_host, statsd_port))

def log_metric(name, value, timestamp):
    sock.send('%s %d %d\n' % (name, value, timestamp))

def server_state_num(s):
    return STATES[s]

for line in tailer.follow(open(filename)):
    row = line.split('\t')
    server_state = 'offline'
    if len(row) == 4:
      timestamp, epoch, hostname, queryresult = row
      age = 0
      peers = 0
      load_factor = 0
      complete_ledgers = 0
    elif len(row) == 10:
      timestamp, epoch, hostname, queryresult, server_state, age, peers, \
      proposers, load_factor, complete_ledgers = row
    else:
      continue
    timestamp = dateutil.parser.parse(timestamp)
    try:
      epoch = int(epoch)
      peers = int(peers)
      load_factor = float(load_factor)
    except ValueError, e:
      print "Bad line:", row, e
      continue

    try:
      age = int(age)
    except ValueError, e:
      age = 0
    log_metric(statsd_path+'.server_state',
        server_state_num(server_state), epoch)
    log_metric(statsd_path+'.age', age, epoch)
    log_metric(statsd_path+'.peers', peers, epoch)
    log_metric(statsd_path+'.load_factor', load_factor, epoch)
