#!/bin/bash

cd /usr/local/rippled/etc

while true
do
  date
  echo
  ../sbin/rippled -q get_counts 0
  echo -------------------------------------
  sleep 10
done

