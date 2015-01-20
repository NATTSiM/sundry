#!/bin/sh

while true
do
    date
    netstat -s | grep -i retrans
    echo ----------------
    sleep 60
done

