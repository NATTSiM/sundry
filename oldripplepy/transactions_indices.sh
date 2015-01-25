#!/bin/bash

one="ALTER TABLE transactions ADD PRIMARY KEY (tx_hash);"
two="CREATE INDEX ON transactions (ledger_hash);"
three="CREATE INDEX ON transactions (ledger_index DESC, tx_seq DESC);"
four="CREATE INDEX ON transactions (executed_time DESC);"
five="CREATE INDEX ON transactions (tx_result);"
six="CREATE INDEX ON transactions (tx_type);"
seven="CREATE INDEX ON transactions (account, account_seq DESC);"

echo $one
time psql -c "$one" rippled_history
echo $two
time psql -c "$two" rippled_history
echo $three
time psql -c "$three" rippled_history
echo $four
time psql -c "$four" rippled_history
echo $five
time psql -c "$five" rippled_history
echo $six
time psql -c "$six" rippled_history
echo $seven
time psql -c "$seven" rippled_history

