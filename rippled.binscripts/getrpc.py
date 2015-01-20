#!/usr/bin/env python3

basedir = "/usr/local/rippled"

import sys
import string
import time
import json

report = str(sys.argv[1])
key = str(sys.argv[2]).split(".")

if len(sys.argv) != 3:
    sys.exit(1)

reportfile = basedir + "/var/run/" + report

fd = None

try:
    fd = open(reportfile, "r", -1)
except:
    time.sleep(1)
    fd = open(reportfile, "r", -1)

js = json.load(fd)
for i in key:
    if i.count("#"):
        i = i.replace('#', '')
        js = js[int(i)]
    else:
        js = js[i]
print(js)
