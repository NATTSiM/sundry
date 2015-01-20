#!/bin/bash

cd /usr/local/rippled/etc

while true
do
  date
  echo
  /usr/bin/lsof -n
  echo -------------------------------------
  sleep 600
done

