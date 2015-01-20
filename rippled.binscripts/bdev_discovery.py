#!/usr/bin/env python3

# jout = {"data": [ {"{#BDEV}": "xvdf"}, {"{#BDEV}": "foo"} ]}
# print(json.dumps(jout, indent=4, separators=(',', ': ')))

import json

bdevs=[]

diskstats = open("/proc/diskstats", "r", -1)
for line in diskstats:
    fields = line.split()
    if fields[2].count("ram") or fields[2].count("loop"):
        continue
    bdevs.append({"{#BDEV}": fields[2]})
diskstats.close()

print(json.dumps({"data": bdevs}, indent=4, separators=(",", ": ")))
