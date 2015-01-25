#!/bin/bash

one="CREATE INDEX ON account_transactions (account, ledger_index DESC, tx_seq DESC);"
two="CREATE INDEX ON account_transactions (tx_result);"
three="CREATE INDEX ON account_transactions (tx_type);"
four="CREATE INDEX ON account_transactions (executed_time DESC);"
five="ALTER TABLE account_transactions ADD PRIMARY KEY (tx_hash, account);"

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

