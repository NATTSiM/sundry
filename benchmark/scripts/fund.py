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

# Create and fund a gateway and users with XRP and the gateway's currency.
# Save addresses in json for later use.

import ripplepy
import argparse
import json
import time

FUNDER = 'rHb9CJAWyB4rj91VRWn96DkukG4bwdtyTh'
SECRET = 'masterpassphrase'
DROPS = 1000000
PAUSE = 0.25

cfg = {
    'currency': 'BUX',
    'accounts': 5000,
    'amount_gateway_xrp': str(100000 * DROPS),
    'amount_xrp': str(10000000 * DROPS),
    'trust_currency': '1000000000000',
    'amount_currency': '1000000000'
}

def fund(server, sender, recipient, amount, secret):
    tx_json = {
        'Flags': 2147483648,
        'TransactionType': 'Payment',
        'Account': sender,
        'Amount': amount,
        'Destination': recipient,
        'Fee': '1000000',
    }
    tx_json['Sequence'] = ripplepy.Cmd(server).account_info(sender)['result']['account_data']['Sequence']
    transaction = {'tx_json': tx_json, 'secret': secret}
    print(ripplepy.Cmd(server).submit(ripplepy.ripple_serdes.ripple_json(json.dumps(transaction).encode())))

def trust(server, limit, gateway, sender, secret):
    limitAmount = {
        'currency': cfg['currency'],
        'value': limit,
        'issuer': gateway
    }
    tx_json = {
        'Flags': 131072,
        'TransactionType': 'TrustSet',
        'Account': sender,
        'Fee': '1000000'
    }
    tx_json['LimitAmount'] = limitAmount
    tx_json['Sequence'] = ripplepy.Cmd(server).account_info(sender)['result']['account_data']['Sequence']
    transaction = {'tx_json': tx_json, 'secret': secret}
    print(ripplepy.Cmd(server).submit(ripplepy.ripple_serdes.ripple_json(json.dumps(transaction).encode())))

# main
argparser = argparse.ArgumentParser()
argparser.add_argument('-o', '--output-file', type=str, required=True)
argparser.add_argument('-s', '--server', type=str, required=True)
args = argparser.parse_args()

outfile = open(args.output_file, 'w')

res = {'cfg': cfg}
res['gateway'] = ripplepy.Cmd(args.server).wallet_propose()['result']
gateway = res['gateway']['account_id']
gateway_seed = res['gateway']['master_seed']
fund(args.server, FUNDER, gateway, cfg['amount_gateway_xrp'], SECRET)

gateway = res['gateway']['account_id']

res['accounts'] = list()
for i in range(1, cfg['accounts']+1):
    account = ripplepy.Cmd(args.server).wallet_propose()['result']
    fund(args.server, FUNDER, account['account_id'], cfg['amount_xrp'], SECRET)
    amount = {
        'currency': cfg['currency'],
        'value': cfg['amount_currency'],
        'issuer': gateway
    }
    trust(args.server, cfg['trust_currency'], gateway, account['account_id'],
         account['master_seed'])
    fund(args.server, gateway, account['account_id'], amount, gateway_seed)
    res['accounts'].append(account)
    time.sleep(PAUSE)

json.dump(res, outfile)
