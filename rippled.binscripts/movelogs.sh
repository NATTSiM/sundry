#!/bin/bash

RSYNC=/usr/bin/rsync
DEST=10.202.1.11::logs/debug
HOSTNAME=`/bin/hostname`
LOGDIR=/data/rippled/var/log
TRUE=/bin/true
RM=/bin/rm

for log in $LOGDIR/*.gz
do
    destname=$HOSTNAME.`/usr/bin/basename $log`
    if `$RSYNC $log $DEST/$destname`
    then
        $RM $log
    fi
done

