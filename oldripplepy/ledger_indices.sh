#!/bin/bash

one="ALTER TABLE ledgers ADD PRIMARY KEY (ledger_hash);"
two="CREATE INDEX ON ledgers (ledger_index DESC);"
three="CREATE INDEX ON ledgers (parent_hash);"

echo $one
time psql -c "$one" rippled_history
echo $two
time psql -c "$two" rippled_history
echo $three
time psql -c "$three" rippled_history

