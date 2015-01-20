#!/bin/bash

# startup rippled things on boot
BASEDIR=/usr/local/rippled

# set up raid0 for ephemeral devices
$BASEDIR/bin/md127.sh

su -c "nohup $BASEDIR/bin/collectrpc.py > /dev/null 2>&1 &" rippled

