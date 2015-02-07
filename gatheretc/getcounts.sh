#!/bin/bash

while true
do
  date
  echo
  /usr/sbin/rippled --conf /etc/rippled/rippled.cfg -q get_counts 0
  echo -------------------------------------
  sleep 10
done

