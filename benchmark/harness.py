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

import ripplepy
import argparse
import threading
import sys
import queue
import csv

# Benchmark phases
# 1. prepare test, such as load initial data to randomize
# 2. launch workers
# 3. synchronize time
# 4. start

def worker(instance, test, scheduler_state, hosts):
    while True:
        pause()

        scheduler_state._started_lock.acquire()
        scheduler_state._started += 1
        scheduler_state._started_lock.release()

        test.send()

        scheduler_state._finished_lock.acquire()
        scheduler_state._finished += 1
        scheduler_state._finished_lock.release()

def pause():
    pass

class SchedulerState:
    _started = 0
    _finished = 0
    def __init__(self):
        self._started_lock = threading.Lock()
        self._finished_lock = threading.Lock()

def logger(q, logfile):
    outfile = open(logfile, 'a', 1)
    while True:
        msg = q.get()
        outfile.write(str(msg) + '\n')


# main
argparser = argparse.ArgumentParser()
argparser.add_argument('-t', '--test', type=str, required=True)
argparser.add_argument('-c', '--conf', type=str, required=True)
args = argparser.parse_args()

test = __import__(args.test)
conf = __import__(args.conf)

scheduler_state = SchedulerState()

# prepare phase, have the params
preparation = test.Prepare()
q = queue.Queue()
qt = threading.Thread(target=logger, args=(q,), daemon=True)

for t in (range(1, conf.workers+1)):
    w = threading.Thread(target=worker, args=(t, test.Test(q, conf.logfile),
                                              scheduler_state, conf.hosts),
                         daemon=True)
    w.start()

outfile = open(conf.summaryfile, 'a', 1)
while True:
    # write to csv sent, inflight, etc
    pass
