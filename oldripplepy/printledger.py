#!/usr/bin/env python3

import argparse
import time
import sys
import ripplepy

# main
db = ripplepy.RipDb('/space/tmp/db')

argparser = argparse.ArgumentParser()
argparser.add_argument('-s', '--sequence', type=int, required=True)
args = argparser.parse_args()

lrec = db.get_ledger_record(args.sequence)
print(lrec)
print('close time: ' + db.ledger_close(args.sequence))
print("")
l = db.whole_ledger(args.sequence)

for node in l['sha_map']:
    print('\t'.join((ripplepy.Uint256(node).hexstr(), str(l['sha_map'][node]['pos']))))
#print(l['sha_map'][ripplepy.Uint256(args.nodehash).data()])

#for i in range(8765345, 8770719):
#    print(time.ctime() + ' ledger: ' + str(i))
#    l = db.whole_ledger(i)
