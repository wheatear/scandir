#!/usr/bin/env python
"""emergency provisioning ps control model"""

import sys
import os
import time
import multiprocessing
import signal
import cx_Oracle as orcl
import pexpect
import pexpect.pxssh
import threading
import base64

from config import *

class CtyptoTool(object):
    def __init__(self,cfg):
        self.cfg = cfg

    def encryptStr(self,str):
        return base64.encodestring(str)

    def decryptStr(self,str):
        return base64.decodestring(str)

    def encryptCluster(self):
        sql = 'select CLUSTER_CODE,USER_PW from SCANDIR_CLUSTER'
        updateSql = 'update SCANDIR_CLUSTER set USER_PW=:1 where CLUSTER_CODE=:2'
        cur = self.cfg.db.cursor()
        cur.execute(sql)
        aClus = cur.fetchall()
        cur.prepare(updateSql)
        for row in aClus:
            clusterCode = row[0]
            passwd = row[1]
            encryPwd = base64.encodestring(passwd)
            cur.execute(None,(encryPwd,clusterCode))
            cur.connection.commit()
        cur.close()

    def enctyptHost(self):
        sql = 'select VM_IP,USER_PW from SCANDIR_HOST'
        updatePwd = 'update SCANDIR_HOST set USER_PW=:1 where VM_IP=:2'
        cur = self.cfg.db.cursor()
        cur.execute(sql)
        aHosts = cur.fetchall()
        cur.prepare(updatePwd)
        for row in aHosts:
            hostIp = row[0]
            passwd = row[1]
            encryPwd = base64.encodestring(passwd)
            cur.execute(None,(encryPwd,hostIp))
            cur.connection.commit()
        cur.close()

def main():
    # cfg = Conf('cryptotool')
    # cfg.getDb()
    cfg = None
    crypter = CtyptoTool(cfg)
    # crypter.encryptCluster()
    # crypter.enctyptHost()
    # cfg.db.close()

    operator = '-d'
    param = ''
    if len(sys.argv) == 3:
        operator = sys.argv[1]
        param = sys.argv[2]
    else:
        param = sys.argv[1]
    result = sys.argv[1]
    if operator == '-d':
        result = base64.b64decode(param)
    else:
        result = base64.b64encode(param)
    print result

if __name__ == '__main__':
    main()