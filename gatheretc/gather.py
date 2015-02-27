#!/usr/bin/env python

import os
import subprocess
import json
import time
import datetime
import sys
import socket
import csv
import argparse

argparser = argparse.ArgumentParser()
argparser.add_argument('-r', '--rippled', type=str,
    default='/usr/sbin/rippled')
argparser.add_argument('-c', '--conf', type=str,
    default='/etc/rippled/rippled.cfg')
argparser.add_argument('-i', '--interval', type=int, default=10)
argparser.add_argument('-o', '--outfile', type=str)
args = argparser.parse_args()

devnull = open(os.devnull, 'w')
outfile = None
if args.outfile is not None:
    outfile = open(args.outfile, 'a')

hostname=socket.gethostname()
csv_writer = csv.writer(sys.stdout, delimiter='\t', lineterminator='\n')

csv_writer.writerow(['datetime', 'epochtime', 'hostname', 'queryresult',
    'server_state', 'age', 'peers', 'proposers', 'load_factor',
    'complete_ledgers'])

while 1:
    output = []
    nowsecond = time.time()
    output.append(time.asctime(time.localtime(nowsecond)))
    output.append(str(int(nowsecond)))
    output.append(hostname)

    res = ''
    try:
        res = subprocess.check_output([args.rippled, '--conf', args.conf,
            'server_info'], stderr=devnull)
        output.append('ok')
        j = json.loads(res)

        if 'server_state' in j['result']['info']:
            output.append(j['result']['info']['server_state'])
        else:
            output.append('-')
        if 'age' in j['result']['info']['validated_ledger']:
            output.append(str(j['result']['info']['validated_ledger']['age']))
        else:
            output.append('-')
        if 'peers' in j['result']['info']:
            output.append(str(j['result']['info']['peers']))
        else:
            output.append('-')
        if 'proposers' in j['result']['info']['last_close']:
            output.append(str(j['result']['info']['last_close']['proposers']))
        else:
            output.append('-')
        if 'load_factor' in j['result']['info']:
            output.append(str(j['result']['info']['load_factor']))
        else:
            output.append('-')
        if 'complete_ledgers' in j['result']['info']:
            output.append(str(j["result"]["info"]["complete_ledgers"]))
        else:
            output.append('-')
 
    except:
        output.append('nok')

    csv_writer.writerow(output)
    sys.stdout.flush()

    if outfile is not None:
        outfile.write(time.asctime(time.localtime(nowsecond)) + '\n' + res +
            '\n----------------------------\n')
        outfile.flush()

    time.sleep(args.interval)
