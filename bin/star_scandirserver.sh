#!/bin/ksh
. /nms/.bash_profile

cd /nms/scandir/bin
python scandirserver.py >>/nms/scandir/log/crontab_scanserver.log 2>&1

