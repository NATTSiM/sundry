#!/usr/bin/env python

import os
import subprocess
import json
import time
import datetime
import sys
import socket

interval=0

if len(sys.argv)==2:
    interval=int(sys.argv[1])

if interval <= 0:
    interval=10
    
devnull=open(os.devnull, "w")

hostname=socket.gethostname()

print '\t'.join(["datetime", "epochtime", "hostname", "queryresult",
    "server_state", "age", "peers", "proposers", "load_factor", "complete_ledgers"])

while 1:
    output=[]
    nowsecond=time.time()
    output.append(time.asctime(time.localtime(nowsecond)))
    output.append(str(int(nowsecond)))
    output.append(hostname)
    try:
        res=subprocess.check_output(["/usr/sbin/rippled", "--conf", "/etc/rippled/rippled.cfg", "server_info"], stderr=devnull)
        output.append("ok")
        j=json.loads(res)

        try:
            output.append(j["result"]["info"]["server_state"])
        except:
            output.append("-")
        try:
            output.append(str(j["result"]["info"]["validated_ledger"]["age"]))
        except:
            output.append("-")
        try:
            output.append(str(j["result"]["info"]["peers"]))
        except:
            output.append("-")
        try:
            output.append(str(j["result"]["info"]["last_close"]["proposers"]))
        except:
            output.append("-")
        try:
            output.append(str(j["result"]["info"]["load_factor"]))
        except:
            output.append("-")
        try:
            output.append(str(j["result"]["info"]["complete_ledgers"]))
        except:
            output.append("-")
 
    except:
        output.append("nok")

    print '\t'.join(output)
    sys.stdout.flush()
    time.sleep(interval)

