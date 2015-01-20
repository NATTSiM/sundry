#!/usr/bin/env python3

import sys
import os

outdir = "/tmp"

bdev = sys.argv[1]
stat = sys.argv[2]

#stats = { 'reads_completed': 3,
#          'reads_merged': 4,
#          'sectors_read': 5,
#          'time_reading': 6,
#          'writes_completed': 7,
#          'writes_merged': 8,
#          'sectors_written': 9,
#          'time_writing': 10,
#          'ios_in_progress': 11,
#          'time_ios': 12,
#          'weighted_time_ios': 13
#}

ms = 0
iops = 0
reads = 0
rmerged = 0
wmerged = 0
writes = 0
wmerged = 0
sread = 0
swritten = 0

diskstats = open("/proc/diskstats", "r", -1)
for line in diskstats:
    line = line.rstrip('\n')
    fields = line.split()
    if fields[2] != bdev:
        continue

    if stat == "rlatency":
        ms = int(fields[6])
        reads = int(fields[3])
    elif stat == "wlatency":
        ms = int(fields[10])
        writes = int(fields[7])
    elif stat == "iolatency":
        ms = int(fields[6]) + int(fields[10])
        iops = int(fields[3]) + int(fields[7])
    elif stat == "rmergedpct":
        reads = int(fields[3])
        rmerged = int(fields[4])
    elif stat == "wmergedpct":
        writes = int(fields[7])
        wmerged = int(fields[8])
    elif stat == "rsize":
        reads = int(fields[3])
        sread = int(fields[5])
    elif stat == "wsize":
        writes = int(fields[7])
        swritten = int(fields[9])
    else:
        sys.exit(1)

    break

prev_ms = 0
prev_iops = 0
prev_reads = 0
prev_rmerged = 0
prev_wmerged = 0
prev_writes = 0
prev_wmerged = 0
prev_sread = 0
prev_swritten = 0

outfile = outdir + "/" + bdev + "." + stat
if os.path.exists(outfile) == True:
    outfd = open(outfile, "r", -1)
    contents = outfd.read()
    outfd.close()
    fields = contents.split()

    if stat == "rlatency":
        prev_ms = int(fields[0])
        prev_reads = int(fields[1])
    elif stat == "wlatency":
        prev_ms = int(fields[0])
        prev_writes = int(fields[1])
    elif stat == "iolatency":
        prev_ms = int(fields[0])
        prev_iops = int(fields[1])
    elif stat == "rmergedpct":
        prev_reads = int(fields[0])
        prev_rmerged = int(fields[1])
    elif stat == "wmergedpct":
        prev_writes = int(fields[0])
        prev_wmerged = int(fields[1])
    elif stat == "rsize":
        prev_reads = int(fields[0])
        prev_sread = int(fields[1])
    elif stat == "wsize":
        prev_writes = int(fields[0])
        prev_swritten = int(fields[1])

outline = ""
if stat == "rlatency":
    if reads-prev_reads:
        print( (ms-prev_ms)/(reads-prev_reads) )
    else:
        print(0)
    outline = "\t".join([str(ms), str(reads)])
elif stat == "wlatency":
    if writes-prev_writes:
        print( (ms-prev_ms)/(writes-prev_writes) )
    else:
        print(0)
    outline = "\t".join([str(ms), str(writes)])
elif stat == "iolatency":
    if iops-prev_iops:
        print( (ms-prev_ms)/(iops-prev_iops) )
    else:
        print(0)
    outline = "\t".join([str(ms), str(iops)])
elif stat == "rmergedpct":
    if reads-prev_reads:
        print ( ((rmerged-prev_rmerged)/(reads-prev_reads))*100 )
    else:
        print(0)
    outline = "\t".join([str(reads), str(rmerged)])
elif stat == "wmergedpct":
    if writes-prev_writes:
        print ( ((wmerged-prev_wmerged)/(writes-prev_writes))*100 )
    else:
        print(0)
    outline = "\t".join([str(writes), str(wmerged)])
elif stat == "rsize":
    if reads-prev_reads:
        print ( ((sread-prev_sread)/(reads-prev_reads))*512 )
    else:
        print(0)
    outline = "\t".join([str(reads), str(sread)])
elif stat == "wsize":
    if writes-prev_writes:
        print ( ((swritten-prev_swritten)/(writes-prev_writes))*512 )
    else:
        print(0)
    outline = "\t".join([str(writes), str(swritten)])
else:
    print("Can't handle stat {}.".format(stat), file=sys.stderr)
    sys.exit(1)

outfd = open(outfile, "w", -1)
outfd.write(outline)
outfd.close()

