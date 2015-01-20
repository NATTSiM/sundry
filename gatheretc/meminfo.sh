#!/bin/bash

while true
do
  for pid in `pgrep rippled`
  do
    echo `date` $pid meminfo: `cat /proc/$pid/statm`
  done

  sleep 60
done
