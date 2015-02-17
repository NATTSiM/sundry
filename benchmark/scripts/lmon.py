#!/usr/bin/env python3

# Copyright (c) 2014 Ripple Labs Inc.
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# Summarize validated ledgers.
# -l <logfile> appends output to <logfile>
# -s <server> is server to connect to
# -c start monitoring ledgers as of the next validated
# -b <#> begin with ledger # or min possible (is overridden by -c)
# -e <#> end with ledger #, or max possible
# -x exit without waiting for next ledger to be validated
#
# Output is tab-delimited ledger index, timestamp, and transaction quantity
#
# Examples:
# Start from current ledger and summarize indefinitely:
# <lmon.py> -l /tmp/foo.log -s https://s1.ripple.com:51234 --current
#
# Summarize all existing validated ledgers, then stop:
# <lmon.py> -l /tmp/foo.log -s https://s1.ripple.com:51234
#
# Note: validated logic assumes a single server being connected to, not
# round-robbined. validated flag in ledger should be fixed.

import ripplepy
import argparse
import csv
import time
import sys

PAUSE = 1

# main
argparser = argparse.ArgumentParser()
argparser.add_argument('-l', '--logfile', type=str, required=True)
argparser.add_argument('-s', '--server', type=str, required=True)
argparser.add_argument('-c', '--current', action='store_true')
argparser.add_argument('-b', '--begin', type=int, required=False, default=1)
argparser.add_argument('-e', '--end', type=int, required=False,
                       default=ripplepy.RIPPLE_MAX_LEDGER)
argparser.add_argument('-x', '--exit', action='store_true')
args = argparser.parse_args()

begin = args.begin
if args.current is True:
    begin = int(ripplepy.Cmd(args.server).ledger(ledger_hash=ripplepy.Cmd(args.server).server_info()['result']['info']['validated_ledger']['hash'])['result']['ledger']['seqNum']) + 1

outfile = open(args.logfile, 'a', 1, newline='')
outwriter = csv.writer(outfile, delimiter='\t', lineterminator='\n')

max_validated = int()
i = begin
while i <= args.end:
    while i > max_validated:
        try:
            max_validated = int(ripplepy.Cmd(args.server).ledger(ledger_index='validated')['result']['ledger']['ledger_index'])
        except Exception as ee:
            sys.stderr.write('Exception getting max_validated with ledger: '
                             + str(i) + ' ' + time.ctime() + '\n' +
                             str(sys.exc_info()) + '\n')
        time.sleep(PAUSE)

    Ledger = None
    try:
        ledger = ripplepy.Cmd(args.server).ledger(transactions=True,
                                                  ledger_index=i)
    except:
        sys.stderr.write('Exception ledger: ' + str(i) + ' ' + time.ctime() +
                '\n' + str(sys.exc_info()) + '\n')
        time.sleep(PAUSE)
        continue

    when = ripplepy.RippleTime(int(ledger['result']['ledger']['close_time'])).human()
    outwriter.writerow((i,
                        when,
                        len(ledger['result']['ledger']['transactions'])
    ))
    i += 1
