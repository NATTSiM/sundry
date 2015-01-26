#!/bin/bash

one="ALTER TABLE transactions ADD PRIMARY KEY (tx_hash);"
two="CREATE INDEX ON transactions (ledger_hash);"
three="CREATE INDEX ON transactions (ledger_index DESC, tx_seq DESC);"
four="CREATE INDEX ON transactions (executed_time DESC);"
five="CREATE INDEX ON transactions (tx_result);"
six="CREATE INDEX ON transactions (tx_type);"
seven="CREATE INDEX ON transactions (account, account_seq DESC);"

echo $one
time psql -U rippled -c "$one" rippled_history
echo $two
time psql -U rippled -c "$two" rippled_history
echo $three
time psql -U rippled -c "$three" rippled_history
echo $four
time psql -U rippled -c "$four" rippled_history
echo $five
time psql -U rippled -c "$five" rippled_history
echo $six
time psql -U rippled -c "$six" rippled_history
echo $seven
time psql -U rippled -c "$seven" rippled_history

