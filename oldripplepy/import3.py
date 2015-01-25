#!/usr/bin/env python3

import ripplepy
import binascii
import sys
import argparse
import os

# this is to convert rippled time that starts from 1/1/2000 to 1/1/1970
def toUnixTime(sec):
    return sec+946684800 # add the 30 years from 1970 to 2000

def resultString(byte):
    map = {
        0: 'tesSUCCESS',
        100: 'tecCLAIM',
        101: 'tecPATH_PARTIAL',
        102: 'tecUNFUNDED_ADD',
        103: 'tecUNFUNDED_OFFER',
        104: 'tecUNFUNDED_PAYMENT',
        105: 'tecFAILED_PROCESSING',
        121: 'tecDIR_FULL',
        122: 'tecINSUF_RESERVE_LINE',
        123: 'tecINSUF_RESERVE_OFFER',
        124: 'tecNO_DST',
        125: 'tecNO_DST_INSUF_XRP',
        126: 'tecNO_LINE_INSUF_RESERVE',
        127: 'tecNO_LINE_REDUNDANT',
        128: 'tecPATH_DRY',
        129: 'tecUNFUNDED',
        130: 'tecMASTER_DISABLED',
        131: 'tecNO_REGULAR_KEY',
        132: 'tecOWNERS',
        133: 'tecNO_ISSUER',
        134: 'tecNO_AUTH',
        135: 'tecNO_LINE',
        136: 'tecINSUFF_FEE',
        137: 'tecFROZEN',
        138: 'tecNO_TARGET',
        139: 'tecNO_PERMISSION',
        140: 'tecNO_ENTRY',
        141: 'tecINSUFFICIENT_RESERVE'
    };

    return map[byte]

def toPgHex(input):
    if type(input) is str:
        inbytes = bytes(input, 'utf-8')
    elif type(input) is int or type(input) is float:
        inbytes = bytes(str(input), 'utf-8')
    elif type(input) is bytes:
        inbytes = input
    else:
        raise ValueError('bad input')

    return '\\\\x' + binascii.hexlify(inbytes).decode()

def hexToPgHex(input):
    return toPgHex(ripplepy.Uint256(input).data())

def transactionResult(tx_meta):
    res = str()
    l = len(tx_meta)
    if tx_meta[l-3] == 3 and tx_meta[l-2] == 16:
        res = resultString(tx_meta[l-1])

    return res

# main
argparser = argparse.ArgumentParser()
argparser.add_argument('-o', '--output-dir', type=str, required=True)
argparser.add_argument('-s', '--start-ledger', type=int, required=False)
argparser.add_argument('-e', '--end-ledger', type=int, required=False)
args = argparser.parse_args()

ripdb = ripplepy.RipDb('/space/historydb/sqlite/', nodestore=None)

#lcur = ripdb._ledgerdb.cursor()
#ledgersfile = open(os.path.join(args.output_dir, 'ledgers'), 'w')
#for row in lcur.execute('SELECT LedgerHash, LedgerSeq, PrevHash, TotalCoins, ClosingTime, CloseTimeRes, AccountSetHash, TransSetHash FROM LEDGERS;'):
#    ledgersfile.write('\t'.join( (hexToPgHex(row[0]), str(row[1]),
#        hexToPgHex(row[2]), str(row[3]), str(toUnixTime(row[4])),
#        str(row[5]), hexToPgHex(row[6]), hexToPgHex(row[7])) ) + '\n')
#ledgersfile.close()
#lcur.close()

tcur = ripdb._transactiondb.cursor()
lcur = ripdb._ledgerdb.cursor()
transactionsfile = open(os.path.join(args.output_dir, 'transactions'), 'w')
for row in tcur.execute('SELECT TransID, RawTxn, TxnMeta, LedgerSeq, TransType, FromAcct, FromSeq FROM Transactions ORDER BY LedgerSeq;'):
    tx_hash = row[0]
    tx_raw = row[1]
    tx_meta = row[2]
    ledger_index = row[3]
    tx_type = row[4]
    account = row[5]
    account_seq = row[6]

    tx_result = str()
    l = len(tx_meta)
    tx_result = transactionResult(tx_meta)

    ledger_hash = str()
    executed_time = int()
    for ledger in lcur.execute('SELECT LedgerHash, ClosingTime FROM Ledgers WHERE LedgerSeq = ?;', (ledger_index,)):
        ledger_hash = ledger[0]
        executed_time = ledger[1]

    tx_seq = int()
    acur = ripdb._transactiondb.cursor()
    for accttrans in acur.execute('SELECT TxnSeq FROM AccountTransactions WHERE TransID = ? LIMIT 1;', (tx_hash,)):
        tx_seq = accttrans[0]
    acur.close()

    transactionsfile.write('\t'.join( (hexToPgHex(tx_hash), toPgHex(tx_raw),
        toPgHex(tx_meta), hexToPgHex(ledger_hash), str(ledger_index),
        str(tx_seq), str(toUnixTime(executed_time)), tx_result, tx_type,
        toPgHex(account), str(account_seq)) ) + '\n')

transactionsfile.close()
tcur.close()
lcur.close()

#prev_tx_hash = str()
#executed_time = int()
#tx_result = str()
#tx_type = str()
## if tx_hash is different, do queries for executed_time, tx_result, tx_type
## executed_time: ledgers, tx_result & tx_type: transactions

#acur = ripdb._transactiondb.cursor()
#lcur = ripdb._ledgerdb.cursor()
#tcur = ripdb._transactiondb.cursor()
#accounttransactionsfile = open(os.path.join(args.output_dir, 'account_transactions'), 'w')
#for row in acur.execute('SELECT Account, TransID, LedgerSeq, TxnSeq FROM AccountTransactions ORDER BY TransID DESC;'):
#    account = row[0]
#    tx_hash = row[1]
#    ledger_index = row[2]
#    tx_seq = row[3]
#    if tx_hash != prev_tx_hash:
#        for lrow in lcur.execute('SELECT ClosingTime FROM Ledgers WHERE LedgerSeq = ?;', (ledger_index,)):
#            executed_time = lrow[0]
#
#        for trow in tcur.execute('SELECT TransType, TxnMeta FROM Transactions WHERE TransID = ?', (tx_hash,)):
#            tx_type = trow[0]
#            tx_result = transactionResult(trow[1])
#
#        prev_tx_hash = tx_hash
#
#    accounttransactionsfile.write('\t'.join( (toPgHex(account),
#        hexToPgHex(tx_hash), str(ledger_index), str(tx_seq),
#        str(toUnixTime(executed_time)), tx_result, tx_type) ) + '\n')
#accounttransactionsfile.close()
#acur.close()
#tcur.close()
#lcur.close()

