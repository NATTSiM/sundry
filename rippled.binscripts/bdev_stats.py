#!/usr/bin/env python3

import sys

bdev = sys.argv[1]
stat = sys.argv[2]

stats = { 'reads_completed': 3,
          'reads_merged': 4,
          'sectors_read': 5,
          'time_reading': 6,
          'writes_completed': 7,
          'writes_merged': 8,
          'sectors_written': 9,
          'time_writing': 10,
          'ios_in_progress': 11,
          'time_ios': 12,
          'weighted_time_ios': 13
}

diskstats = open("/proc/diskstats", "r", -1)
for line in diskstats:
    line = line.rstrip('\n')
    fields = line.split()
    if fields[2] != bdev:
        continue
    print(fields[stats[stat]])
    sys.exit
