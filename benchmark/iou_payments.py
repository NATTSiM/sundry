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

# Test IOU transfers of the same issuer + currency between accounts.

import testbase
import random
import sys
import json
import ripplepy

statuses = 5

class Prepare(testbase.PrepareBase):
    def __init__(self, params=dict()):
        accounts_file = open(params['accounts_file'], 'r')
        accounts = json.load(accounts_file)
        accounts_file.close()
        params['accounts'] = accounts


class Test(testbase.TestBase):
    def __init__(self, params=None, conf=None, instance=None):
        super().__init__(params, conf, instance)
        self._timeout = params['timeout']
        self._server = params['hosts'][instance % len(self._params['hosts'])]
        self._client = ripplepy.RippleClient(self._server,
                timeout=self._timeout)
#        self._client = ripplepy.RippleClient(
#            params['hosts'][instance % len(self._params['hosts'])],
#            timeout=self._timeout)
        self._accounts = list()
        for i in range(len(self._params['accounts']['accounts'])):
            if instance == (i % conf.workers) + 1:
                self._accounts.append(self._params['accounts']['accounts'][i])
        self._max_account = len(self._accounts) - 1
        self._max_total_account = len(self._params['accounts']['accounts']) - 1
        self._trans = {
            'Flags': 2147483648,
            'TransactionType': 'Payment',
            'Fee': '1000000',
            'Amount': {
                'currency': 'BUX',
                'value': '1',
                'issuer': self._params['accounts']['gateway']['account_id']
            }
        }


    def send(self, host=None):
        self._client.disconnect()
        sender = self._accounts[random.randint(0, self._max_account)]
        sender_id = sender['account_id']
        sender_seed = sender['master_seed']
        recipient_id = None
        while True:
            recipient_id = self._params['accounts']['accounts'][random.randint(0, self._max_total_account)]['account_id']
            if recipient_id != sender_id:
                break
        self._trans['Account'] = sender_id
        self._trans['Destination'] = recipient_id

        try:
            self._trans['Sequence'] = ripplepy.Cmd(client=self._client).account_info(sender_id)['result']['account_data']['Sequence']
        except ripplepy.RippleException:
            return [1, sender_id, recipient_id, self._server, sys.exc_info()[1]]
        except Exception:
            self._client.disconnect()
            return [2, sender_id, recipient_id, self._server, sys.exc_info()[1]]

        transaction = {'tx_json': self._trans, 'secret': sender_seed}
        tx_blob = ripplepy.ripple_serdes.ripple_json(json.dumps(transaction).encode())

        try:
            results = ripplepy.Cmd(client=self._client).submit(tx_blob)
            return [0, sender_id, recipient_id, self._server, results['result']['tx_json']['hash']]
        except ripplepy.RippleException:
            return [3, sender_id, recipient_id, self._server, sys.exc_info()[1]]
        except Exception:
            self._client.disconnect()
            return [4, sender_id, recipient_id, self._server, sys.exc_info()[1]]
