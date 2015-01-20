#!/bin/bash

BASEDIR=/data/rippled
sleep $[ ( $RANDOM % 60 )  + 1 ]s

NOW=`/bin/date -Iseconds`

mv $BASEDIR/var/log/debug.log $BASEDIR/var/log/debug.log.$NOW
cd /etc/rippled
/usr/sbin/rippled logrotate > /dev/null 2>&1
if `/usr/bin/ionice -c 3 /bin/gzip -c $BASEDIR/var/log/debug.log.$NOW > $BASEDIR/var/log/debug.log.$NOW.gz`
then
    /usr/bin/ionice -c 3 /bin/rm $BASEDIR/var/log/debug.log.$NOW
fi
/usr/bin/find $BASEDIR/var/log -name '*.gz' -mtime +45 -exec /bin/rm {} \;

