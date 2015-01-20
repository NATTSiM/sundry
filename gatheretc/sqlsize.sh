#!/bin/bash

while true
do
  date
  ls -l /usr/local/rippled/db/ledger.db /usr/local/rippled/db/transaction.db
  du -sk /usr/local/rippled/db/hashnode/*
  sleep 60
done
