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
import random
import urllib.parse
import ssl
import http.client
import sys

statuses = 5

class Prepare(testbase.PrepareBase):
    def __init__(self, params=dict()):
        accounts_file = open(params['accounts_file'], 'r')
        accounts = list()
        for line in accounts_file:
            l = line.strip()
            if len(l):
                accounts.append(l)
            params['accounts'] = accounts

class Test(testbase.TestBase):
    def __init__(self, params=None):
        super().__init__(params)
        self._accounts = params['accounts']
        self._max_account = len(self._accounts) - 1
        self._timeout = params['timeout']

    def send(self, host):
        account = self._accounts[random.randint(0, self._max_account)]
        parsed_url = urllib.parse.urlparse(host)

        try:
            if parsed_url.scheme == 'https':
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                conn = http.client.HTTPSConnection(parsed_url.netloc,
                                                   timeout=self._timeout,
                                                   context=context)
            else:
                conn = http.client.HTTPConnection(parsed_url.netloc,
                                                  timeout=self._timeout)
            conn.connect()
        except Exception:
            return [1, host, account, 0, sys.exc_info()[1]]

        try:
            conn.request('GET', '/v1/accounts/' + account +
                         '/transactions?type=Payment')
        except Exception:
            return [2, host, account, 0, sys.exc_info()[1]]

        response = None
        try:
            response = conn.getresponse()
        except Exception:
            return [3, host, 0, sys.exc_info()[1]]

        body = response.read()
        if response.reason != 'OK':
            return [4, host, account, len(body), response.reason, response.status]
            print(ret)
            sys.exit(4)

        return [0, host, account, len(body), response.reason]
