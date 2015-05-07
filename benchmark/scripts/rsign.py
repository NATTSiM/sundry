#!/usr/bin/env python3

import subprocess
import struct
import json
import time
import sys

p = subprocess.Popen(['./rsign'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)

# transaction
# {"tx_json":{"Fee":"12000","Sequence":9360,"Destination":"ruaDHgKC3xPRyqyKASHzXVsnvuoXydQmQ","Flags":2147483648,"Account":"rNcnNRJw7pH5kXVJksAyGakNtGTUqS9BY4","Amount":"1500000","TransactionType":"Payment"},"secret":"spjcfWsJhNu71QnFgs93pXwYMCK1L"}
# signed
# 1200002280000000240000249161400000000016E360684000000000002EE0732103CE5A2004B568A65AF607F1E5CD3391451BE1C5B246AB72DADF9E983FAA74AA8E7446304402202B8B925BEE3A03A35B9437C048336F73B4E3DF76ECEFB5EC72FEDF852486F9E302206F6CC21B74E3BF1824B143EFD3C211A66E07972DCEB16DCAD967437240F410148114953BB9DC03A4C796A55D137739473BD212C2CD0B831409D9FB0BDFD746EC2D509FD8D6D9F5F84005A8FC
#p.stdin.write(b'haha\n')
#print(p.stdout.readline())

while True:
    js = '{"tx_json":{"Fee":"12000","Sequence":9360,"Destination":"ruaDHgKC3xPRyqyKASHzXVsnvuoXydQmQ","Flags":2147483648,"Account":"rNcnNRJw7pH5kXVJksAyGakNtGTUqS9BY4","Amount":"1500000","TransactionType":"Payment"},"secret":"spjcfWsJhNu71QnFgs93pXwYMCK1L"}'
    sys.stdout.write(js + '\n');
    print(time.time())
    p.stdin.write(struct.pack('! I', len(js)) + bytes(js, 'utf-8'))
    bufsize = struct.unpack('! I', p.stdout.read(4))[0]
    blob = struct.unpack(str(bufsize) + 's', p.stdout.read(bufsize))
    print(time.time())
    print(blob)
    time.sleep(2)

