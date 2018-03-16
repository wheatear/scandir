#!/usr/bin/env python
"""emergency provisioning ps control model"""

import sys
import os
import time
import multiprocessing
import pexpect
import pexpect.pxssh
import threading

import refreshscanitem
from config import *

def main():
    callName = sys.argv[0]
    cfg = Conf(callName)
    loger = LogWriter(cfg)
    loger.writeLog('connect to oracle')
    cfg.getDb()
    refs = refreshscanitem.RefreshScanItem(cfg)
    refs.loger = loger
    refs.makeCluster()
    cfg.db.close()
    print 'cluster: %s' % refs.aClus
    print 'scp config dir:'
    for f in os.listdir('../config'):
        refs.spreadCluFile('/nms/scandir/config', f)
        print 'scp file %s ok.' % f
    print 'scp bin dir:'
    for f in os.listdir('../bin'):
        refs.spreadCluFile('/nms/scandir/bin', f)
        print 'scp file %s ok.' % f
    print 'all files done.'

if __name__ == '__main__':
    print 'scp files to all cluster...'
    main()