#!/bin/bash

one="ALTER TABLE ledgers ADD PRIMARY KEY (ledger_hash);"
two="CREATE INDEX ON ledgers (ledger_index DESC);"
three="CREATE INDEX ON ledgers (parent_hash);"

echo $one
time psql -U rippled -c "$one" rippled_history
echo $two
time psql -U rippled -c "$two" rippled_history
echo $three
time psql -U rippled -c "$three" rippled_history

