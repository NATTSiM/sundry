#!/usr/bin/env python3

import os
import time
import subprocess
import json
import sys
import socket
#import psycopg2


basedir="/usr/local/rippled"

os.chdir("/etc/rippled")
devnull=open(os.devnull, "w")

reports = {"server_info": None, "get_counts": "0"}
procs = {}
outfiles = {}
for i in reports:
    procs[i] = None
    outfiles[i] = None

while 1:
    for report in reports:
        outfiles[report] = \
            open(basedir + "/var/run/" + report + ".new", "w+", -1)
        if reports[report] == None:
            procs[report] = subprocess.Popen(["/usr/sbin/rippled", "-q", report],
                stdout = outfiles[report], stderr = devnull)
        else:
            procs[report] = subprocess.Popen(["/usr/sbin/rippled", "-q", report,
              reports[report]], stdout = outfiles[report], stderr = devnull)
        time.sleep(1)

    time.sleep(5)

    for report in reports:
        try:
            if procs[report].poll() == None:
                procs[report].kill()
                raise Exception()
            if procs[report].returncode != 0:
                raise Exception()
            outfiles[report].seek(0)
            okay = True
            output = json.load(outfiles[report])
            if output["result"]["status"] != "success":
                raise Exception()
        except:
            outfiles[report].close()
            os.unlink(basedir + "/var/run/" + report + ".new")
        else:
            outfiles[report].close()
            if os.path.isfile(basedir + "/var/run/" + report):
                os.rename(basedir + "/var/run/" + report,
                  basedir + "/var/run/" + report + ".old")
            os.rename(basedir + "/var/run/" + report + ".new",
              basedir + "/var/run/" + report)

    time.sleep(15)
