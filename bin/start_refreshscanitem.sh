#!/bin/ksh
. /nms/.bash_profile

cd /nms/scandir/bin
python refreshscanitem.py > /dev/null 2>&1 &
