#!/bin/bash

cd /home/rippled/stats

nohup ./meminfo.sh >> meminfo.out 2>&1 &
nohup ./getcounts.sh >> getcounts.out 2>&1 &
nohup ./gather.py >> gather.out 2>&1 &
nohup ./retrans.sh >> retrans.out 2>&1 &
#nohup ./lsof.sh >> lsof.out 2>&1 &
nohup top -b -d 60 >> top.out 2>&1 &
nohup iostat -t -x 60 >> iostat.out 2>&1 &
nohup ./sqlsize.sh >> sqlsize.out 2>&1 &
