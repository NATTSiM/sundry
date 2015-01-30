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

# noop test for benchmark

import testbase

statuses = 1

class Prepare(testbase.PrepareBase):
    def __init__(self, params=dict()):
        accounts_file = open('/tmp/accounts.txt', 'r')
        accounts = set()
        for line in accounts_file:
            l = line.strip()
            if len(l):
                accounts.add(l)
            params['accounts'] = accounts

class Test(testbase.TestBase):
    _iterations = 0

    def __init__(self, instance, q, hosts=None, params=None):
        super().__init__(instance, q, hosts, params)

    def send(self):
        ret = super().send()
        self.log(self._iterations)
        self._iterations += 1
        return ret
