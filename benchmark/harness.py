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
import time
import random

# Benchmark phases
# 1. prepare test, such as load initial data to randomize
# 2. launch workers
# 3. synchronize time
# 4. start

SCHEDULE_BACKOFF = 1

def worker(test, q, instance, workers, scheduler_state, rate, under_threshold,
           over_threshold):
    scheduler_state._waiting_lock.acquire()
    scheduler_state._waiting += 1
    scheduler_state._waiting_lock.release()
    # Faster than condition notify(a zillion).
    while scheduler_state._waiting < workers:
        time.sleep(1)
    if scheduler_state._start_second == 0:
        scheduler_state._start_second = int(time.time())

    while True:
        scheduler_state.pause()

        scheduler_state._started_lock.acquire()
        scheduler_state._started += 1
        scheduler_state._started_lock.release()

        start = time.time()
        results = test.send()
        finish = time.time()

        duration = int(round((finish - start) * 1000000))

        scheduler_state._finished_lock.acquire()
        scheduler_state._finished += 1
        scheduler_state._duration += duration
        scheduler_state._status[results[0]] += 1
        if under_threshold is not None and duration < under_threshold:
            scheduler_state._under_threshold += 1
        if over_threshold is not None and duration > over_threshold:
            scheduler_state.over_threshold += 1
        scheduler_state._finished_lock.release()

        q.put([time.asctime(time.localtime()), instance, duration, results[0],
               results[1:]])


class SchedulerState:
    _started = 0
    _finished = 0
    _duration = 0
    _under_threshold = 0
    _over_threshold = 0
    _bucket_second = 0
    _bucket_entries = 0
    _waiting = 0
    _start_second = 0

    def __init__(self, rate, ramp, statuses=1):
        self._rate = rate
        self._ramp = ramp
        self._status = [0] * statuses
        self._started_lock = threading.Lock()
        self._finished_lock = threading.Lock()
        self._bucket_lock = threading.Lock()
        self._waiting_lock = threading.Lock()
        self._start_second_lock = threading.Lock()

    def pause(self):
        rate = int()
        if self._bucket_second - self._start_second >= self._ramp:
            rate = self._rate
        else:
            rate = round(self._rate * (
                (self._bucket_second - self._start_second) / self._ramp))

        self._bucket_lock.acquire()
        self._bucket_entries += 1
        if (self._bucket_entries >= rate):
            self._bucket_second += 1
            self._bucket_entries = 0
        self._bucket_lock.release()

        now = int(round(time.time()))
        # Have we fallen behind?
        if scheduler_state._bucket_second < now:
            scheduler_state._bucket_second = now + SCHEDULE_BACKOFF
        time.sleep(scheduler_state._bucket_second - now +\
                       ((float(random.randint(0, 1000)))/1000 ))


def logger(q, log_file):
    outfile = open(log_file, 'a', 1, newline='')
    outwriter = csv.writer(outfile, delimiter='\t', lineterminator='\n')
    while True:
        outwriter.writerow(q.get())


# main
argparser = argparse.ArgumentParser()
argparser.add_argument('-t', '--test', type=str, required=True)
argparser.add_argument('-c', '--conf', type=str, required=True)
args = argparser.parse_args()

test = __import__(args.test)
conf = __import__(args.conf)

scheduler_state = SchedulerState(conf.rate, conf.ramp, test.statuses)

# prepare phase, have the params
params = dict()
preparation = test.Prepare(params)
q = queue.Queue()
qt = threading.Thread(target=logger, args=(q, conf.log_file), daemon=True)
qt.start()

if conf.stack_size is not None:
    threading.stack_size(conf.stack_size * 1024)

for i in (range(1, conf.workers+1)):
    w = threading.Thread(target=worker, args=(test.Test(conf.hosts,
                                                        params), q, i,
                                              conf.workers,
                                              scheduler_state, conf.rate,
                                              conf.under_threshold,
                                              conf.over_threshold),
                         daemon=True)
    w.start()

outfile = open(conf.summary_file, 'a', 1, newline='')
outwriter = csv.writer(outfile, delimiter='\t', lineterminator='\n')
outwriter.writerow(['time', 'started', 'finished' 'in_flight',
                    'duration', 'under_threshold', 'over_threshold',
                    '|', '[ statuses... ]'])
while True:
    outwriter.writerow([])
    started = scheduler_state._started
    finished = scheduler_state._finished
    outwriter.writerow([time.asctime(time.localtime()),
                        started,
                        finished,
                        started-finished,
                        scheduler_state._duration,
                        scheduler_state._under_threshold,
                        scheduler_state._over_threshold,
                        '|',
                        scheduler_state._status])
    time.sleep(conf.summary_interval)
