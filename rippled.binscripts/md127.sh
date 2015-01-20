#!/bin/bash

VARDIR=/usr/local/rippled/var

BDEVS=`/bin/lsblk -l -n | /bin/grep ^xvd[bcde] | /usr/bin/cut -d ' ' -f 1`

if  [ `/bin/echo $BDEVS | /usr/bin/wc -l` -gt 0 ]
then
  echo $BDEVS
  /sbin/mdadm --stop /dev/md127

  NUMBDEVS=`/bin/echo $BDEVS | /usr/bin/wc -w`
  mdcmd="/sbin/mdadm --create /dev/md127 --level=0 --chunk=256 --force --raid-devices=$NUMBDEVS -R "
  for dev in $BDEVS
  do
    mdcmd="$mdcmd /dev/$dev"
    /sbin/mdadm --zero-superblock /dev/$dev
  done
  echo $mdcmd
  $mdcmd
  /sbin/mkfs.ext4 -F /dev/md127
  /bin/mount -o noatime /dev/md127 $VARDIR
  /bin/chown rippled:rippled $VARDIR
  for subdir in run log ephemeral cores
  do
    /bin/mkdir $VARDIR/$subdir
    /bin/chown rippled:rippled $VARDIR/$subdir
  done
fi

