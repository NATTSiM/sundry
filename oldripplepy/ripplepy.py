__author__ = 'mtravis'

import urllib.parse
import urllib.request
import websocket
import enum
import sys
import time
import json
import ssl
import http.client
import socket
import string
import binascii
import sqlite3
import os
import hashlib
import struct
try:
    import rocksdb
except ImportError:
    print(sys.exc_info())
    print("Functions that require RocksDB will not work.")


def get_hash(data):
    return hashlib.sha512(data[9:]).digest()[:32]


def hash_integrity(hashval, data):
    if type(hashval) is bytes:
        pass
    elif type(hashval) is str:
        hashval = Uint256(hashval).data()
    else:
        raise ValueError('bad hash format')

    return hashval == get_hash(data)


class Ripple:
    class ConnectionType(enum.Enum):
        none = 0
        rpc = 1
        websocket = 2

    _connectionType = ConnectionType.none
    _connectionString = str()
    _timeout = 0
    _no_ssl_verify = False
    _parsedUrl = None
    _ws = websocket.WebSocket
    _rpc = http.client
    _isConnected = False
    # log keys: connectionString, activity, remoteIP, connectTime,
    # disconnectTime
    # activityStartTime, activityFinishTime, exception
    _log = dict()

    def __init__(self, connection_string, timeout=None, no_ssl_verify=False):
        self._connectionString = connection_string
        self._timeout = timeout
        self._no_ssl_verify = no_ssl_verify
        self._log = dict()
        self._log["connectionString"] = connection_string

        self._parsedUrl = urllib.parse.urlparse(self._connectionString)

        if self._parsedUrl.scheme == 'http'\
                or self._parsedUrl.scheme == 'https':
            self._connectionType = Ripple.ConnectionType.rpc
            socket.setdefaulttimeout(self._timeout)
        elif self._parsedUrl.scheme == 'ws' or self._parsedUrl.scheme == 'wss':
            self._connectionType = Ripple.ConnectionType.websocket
        else:
            raise Exception("Bad URL Scheme", self._parsedUrl.scheme)

    def connect(self):
        if self._isConnected:
            self.disconnect()

        # http.client does not actually connect the socket until a request is
        # sent
        if self._connectionType == Ripple.ConnectionType.rpc:
            if self._parsedUrl.scheme == "https":
                context = ssl.create_default_context()
                self._rpc = http.client.HTTPSConnection(self._parsedUrl.netloc,
                                                        timeout=self._timeout,
                                                        context=context)
            elif self._parsedUrl.scheme == "http":
                self._rpc = http.client.HTTPConnection(self._parsedUrl.netloc,
                                                       timeout=self._timeout)

            self._isConnected = True

        elif self._connectionType == Ripple.ConnectionType.websocket:
            try:
                if self._no_ssl_verify:
                    self._ws = websocket.create_connection(
                        self._connectionString, self._timeout,
                        sslopt={"cert_reqs": ssl.CERT_NONE})
                else:
                    self._ws = websocket.create_connection(
                        self._connectionString, self._timeout)

                self._isConnected = True
                self._log["remoteIP"] = self._ws.sock.getpeername()[0]
                self._log["connectTime"] = time.time()
                if "exception" in self._log:
                    del self._log["exception"]
            except Exception as e:
                if hasattr(e, 'remote_ip'):
                    self._log["remoteIP"] = e.remote_ip
                self._log["exception"] = sys.exc_info()
                self._log["disconnectTime"] = time.time()

            self._log["activity"] = "connect"

        return self._isConnected

    def get_remote_ip(self):
        return self._log["remoteIP"]

    def get_is_connected(self):
        return self._isConnected

    def disconnect(self):
        if self._connectionType == Ripple.ConnectionType.rpc:
            try:
                self._rpc.close()
            except:
                pass
        elif self._connectionType == Ripple.ConnectionType.websocket:
            try:
                self._ws.close()
            except:
                pass

        self._isConnected = False
        self._log["activity"] = "disconnect"
        self._log["disconnectTime"] = time.time()

    def command(self, command, activity=None, params=None, id_arg=None, subcommand=None):
        auto_connect = False
        if self._isConnected is False:
            self.connect()
            if self._isConnected is False:
                return False
            auto_connect = True

        indata = {"method": str(command)}
        if id_arg is not None:
            indata["id"] = id_arg
        if params is not None:
            indata["params"] = params
        if subcommand is not None:
            indata["subcommand"] = subcommand

        output = None
        if self._connectionType == Ripple.ConnectionType.rpc:
            try:
                self._log["connectTime"] = time.time()
                self._rpc.request("GET", "/", json.dumps(indata).encode())
                reply = self._rpc.getresponse()
                output = json.loads(reply.read().decode())
                if "exception" in self._log:
                    del self._log["exception"]
            except:
                self._log["exception"] = sys.exc_info()
                output = None

            self._log["disconnectTime"] = time.time()
            self._log["activity"] = activity

        if auto_connect:
            self.disconnect()

        return output

    def cmd_server_info(self):
        return self.command("server_info", activity="server_info")

    def cmd_ledger(self, ledger, full=False, accounts=False, transactions=False,
                   expand=False):
        params = list()
        params.append({"full": full, "accounts": accounts,
                       "transactions": transactions, "expand": expand})
        params[0]["ledger"] = ledger

        return self.command("ledger", activity="ledger," + str(ledger),
                            params=params)

    def cmd_get_counts(self, min_count=0):
        return self.command("get_counts", params=[{'min_count': min_count}])

class Uint256:
    def __init__(self, arg=""):
        if type(arg) is bytes and len(arg) == 32:
            self._data = arg
        elif type(arg) is str and len(arg) == 64 and\
                all(c in string.hexdigits for c in arg):
            self._data = bytes(binascii.unhexlify(arg))
        elif len(arg) == 0:
            data = bytearray()
            for i in range(0, 32):
                data += b"\x00"
            self._data = bytes(data)
        else:
            raise ValueError('not valid uint256 input')

    def data(self):
        return self._data

    def hexstr(self):
        hstr = str()
        for i in self._data:
            hstr += ("%02x" % i).upper()

        return hstr

    def is_zero(self):
        return all(b in b'\x00' for b in self._data)


class RipDb:
    def __init__(self, dbdir, ledger="ledger.db", transaction="transaction.db",
            nodestore="hashnode"):
        if ledger:
            self._ledgerdb =\
                sqlite3.connect(os.path.join(dbdir, ledger))
        if transaction:
            self._transactiondb =\
                sqlite3.connect(os.path.join(dbdir, transaction))
        if nodestore:
            opts = rocksdb.Options()
            opts.create_if_missing = False
            self._nodedb = rocksdb.DB(os.path.join(dbdir, nodestore), opts)

    def get_ledger_record(self, ledger):
        cur = self._ledgerdb.cursor()
        if type(ledger) is bytes:
            sql = "SELECT * FROM Ledgers WHERE LedgerHash=?"
            cur.execute(sql, (Uint256(ledger).hexstr(),))
        elif type(ledger) is str:
            sql = "SELECT * FROM Ledgers WHERE LedgerHash=?"
            cur.execute(sql, (ledger,))
        elif type(ledger) is int:
            sql = "SELECT * FROM Ledgers WHERE LedgerSeq=?"
            cur.execute(sql, (ledger,))
        else:
            raise ValueError('bad ledger lookup value')

        res = cur.fetchone()
        if res is not None:
            rec = dict()
            rec["LedgerHash"] = res[0]
            rec["LedgerSeq"] = res[1]
            rec["PrevHash"] = res[2]
            rec["TotalCoins"] = res[3]
            rec["ClosingTime"] = res[4]
            rec["PrevClosingTime"] = res[5]
            rec["CloseTimeRes"] = res[6]
            rec["CloseFlags"] = res[7]
            rec["AccountSetHash"] = res[8]
            rec["TransSetHash"] = res[9]

            return rec

    def get_hash(self, ledger):
        return self.get_ledger_record(ledger)["LedgerHash"]

    def get_parent_hash(self, ledger):
        return self.get_ledger_record(ledger)["PrevHash"]

    def get_seq(self, ledger):
        return self.get_ledger_record(ledger)["LedgerSeq"]

    def sequences(self):
        sql = "SELECT LedgerSeq FROM Ledgers ORDER BY LedgerSeq ASC;"
        cur = self._ledgerdb.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        res = list()
        for row in rows:
            res.append(row[0])

        return res

    def get_node(self, keyarg):
        key = bytearray()
        if type(keyarg) is bytes:
            key = keyarg
        elif type(keyarg) is str:
            key = Uint256(keyarg).data()
            pass
        else:
            raise ValueError('bad key value')

        val = self._nodedb.get(key)
        if val is None:
            raise LookupError(Uint256(keyarg).hexstr())
        return val

        return self._nodedb.get(key)

    def walker(self, node_hash, pos, slot, return_dict):
        node = PersistentNode(self.get_node(node_hash))
        mypos = pos + [slot]

        return_dict[node_hash] = {'type': NodeObjectType(node._type),
                                  'hash_prefix': HashPrefix(node._hash_prefix),
                                  'pos': mypos}

        if node._hash_prefix == HashPrefix.innerNode.value:
            for idx, val in enumerate(node.hashes()):
                if Uint256(val).is_zero() == False:
                    self.walker(val, mypos, idx, return_dict)

    def whole_ledger(self, ledger):
        res = dict()
        res['ledger_master'] = PersistentNode(
            self.get_node(self.get_hash(ledger))).ledger_master()

        sha_map = dict()
        self.walker(res['ledger_master']['TransHash'], list(), 0, sha_map)
        self.walker(res['ledger_master']['AccountHash'], list(), 0, sha_map)
        res['sha_map'] = sha_map

        return res

    def ledger_close(self, ledger):
        return time.ctime(self.get_ledger_record(ledger)['ClosingTime'] +\
            946684800)


class NodeObjectType(enum.Enum):
    hotUNKNOWN = b'\x00'
    hotLEDGER = b'\x01'
    hotTRANSACTION = b'\x02'
    hotACCOUNT_NODE = b'\x03'
    hotTRANSACTION_NODE = b'\x04'

class HashPrefix(enum.Enum):
    transactionID = b'TXN\x00'
    txNode = b'SND\x00'
    leafNode = b'MLN\x00'
    innerNode = b'MIN\x00'
    ledgerMaster = b'LWR\x00'
    txSign = b'STX\x00'
    validation = b'VAL\x00'
    proposal = b'PRP\x00'

def hashes(blob):
    return struct.unpack("32s 32s 32s 32s 32s 32s 32s 32s 32s 32s 32s 32s 32s 32s 32s 32s", blob)

class PersistentNode:
    def __init__(self, blob):
        self._blob = blob
        pos = 9
        res = struct.unpack("> I 4x c", blob[:pos])
        self._type = res[1]
        res2 = struct.unpack('4s', blob[pos:pos+4])
        self._hash_prefix = res2[0]
        pos += 4

        if self._hash_prefix == HashPrefix.ledgerMaster.value:
            self._record = struct.unpack("> I Q 32s 32s 32s I I B B", blob[pos:])
        elif self._hash_prefix == HashPrefix.innerNode.value:
            self._record = hashes(blob[pos:])

    def ledger_master(self):
        if self._hash_prefix == HashPrefix.ledgerMaster.value:
            lm = dict()
            lm['LedgerSeq'] = self._record[0]
            lm['TotCoins'] = self._record[1]
            lm['ParentHash'] = self._record[2]
            lm['TransHash'] = self._record[3]
            lm['AccountHash'] = self._record[4]
            lm['ParentCloseTime'] = self._record[5]
            lm['CloseTime'] = self._record[6]
            lm['CloseResolution'] = self._record[7]
            lm['CloseFlags'] = self._record[8]

            return lm

    def hashes(self):
        if self._hash_prefix == HashPrefix.innerNode.value:
            return self._record

