#!/usr/bin/env python3

import argparse
import time
import sys
import ripplepy

# main
db = ripplepy.RipDb('/space/tmp/db')

argparser = argparse.ArgumentParser()
argparser.add_argument('-n', '--nodehash', type=str, required=True)
argparser.add_argument('-s', '--sequence', type=int, required=True)
args = argparser.parse_args()

l = db.whole_ledger(args.sequence)
print(l['sha_map'][ripplepy.Uint256(args.nodehash).data()])
#for i in range(8765345, 8770719):
#    print(time.ctime() + ' ledger: ' + str(i))
#    l = db.whole_ledger(i)
