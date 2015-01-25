#!/bin/bash

for table in ledgers transactions account_transactions
do
  echo $table
  time psql -U postgres -c "COPY $table from '/space/historydb/input/$table';" rippled_history
done

