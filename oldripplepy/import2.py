#!/usr/bin/env python3

import ripplepy

ripdb = ripplepy.RipDb('/space/historydb/sqlite', nodestore=None)
cur = ripdb._transactiondb

ttl = 0
hit = 0
miss = 0

sql = "SELECT TxnMeta FROM Transactions LIMIT 100;"
for res in cur.execute(sql):
    length = len(res[0])
    ttl += 1
    if res[0][length-3] == 3 and res[0][length-2] == 16:
        hit += 1
    else:
        miss += 1

print('ttl {0}, hit {1}, miss {2}.'.format(ttl, hit, miss))
