#!/usr/bin/env python
"""emergency provisioning ps control model"""

import sys
import os
import time
import multiprocessing
from multiprocessing.managers import BaseManager
import signal
# import cx_Oracle as orcl
import socket
import hostdirs
from config import *

class ListDir(object):
    'list dir for file number'
    def __init__(self, cfg,servip):
        self.cfg = cfg
        self.servIp = servip
        self.cluster = None
        self.hostname = None
        self.enJfdata = None
        self.enDataHome = None
        self.enHome = None
        self.enJfdataOnline = None
        self.hostDirs = hostdirs.HostDirs()

    def getEnv(self):
        self.enJfdata = os.getenv('JFDATA')
        self.enDataHome = os.getenv('DATA_HOME')
        self.enHome = os.getenv('HOME')
        self.enJfdataOnline = os.getenv('JFDATA_ONLINE')
        self.loger.writeLog('env: %s %s %s %s' % (self.enJfdata,self.enDataHome,self.enHome,self.enJfdataOnline))

    def getDirs(self):
        fHostDirs = open(self.cfg.hostDirs, 'r')
        self.hostDirs.ip = self.ip
        self.hostDirs.cluster = self.cluster
        for line in fHostDirs:
            line = line.strip()
            aDirs = line.split(' ')
            if aDirs[0] == self.cluster:
                vpath = aDirs[2]
                if vpath.find('$') > -1:
                    cpath = self.replaceEnv(vpath)
                else:
                    cpath = vpath
                if cpath in self.hostDirs.dirs:
                    if aDirs[1] == 'XFER':
                        continue
                self.hostDirs.dirs[cpath] = aDirs[1]
        fHostDirs.close()
        self.loger.writeLog('scan dir: %s' % self.hostDirs.dirs)

    def listPath(self):
        for di in self.hostDirs.dirs.keys():
            self.loger.writeLog( di)
            sTime = time.strftime("%Y%m%d%H%M%S", time.localtime())
            try:
                fileNum = len(os.listdir(di))
            except OSError,e:
                errmsg = 'OSError:%s' % e
                self.loger.writeLog('can not list dir %s. %s' % (di,errmsg))
                self.hostDirs.dirs[di] = [self.hostDirs.dirs[di],sTime, errmsg]
                continue
            self.hostDirs.dirs[di] = [self.hostDirs.dirs[di],sTime,fileNum]
            self.loger.writeLog('scan dir files: %s' % self.hostDirs.dirs)

    def sendDir(self):
        DirsManager.register('getQueue')
        self.manager = DirsManager(address=(self.servIp, 50000), authkey='scandirmang')
        self.loger.writeLog('connect to server %s:50000' % self.servIp)
        self.manager.connect()
        dirQueue = self.manager.getQueue()
        dirQueue.put(self.hostDirs)

    def replaceEnv(self,sdir):
        # if not self.enJfdata:
        #     self.getEnv()
        if self.enJfdataOnline:
            sdir = sdir.replace('$JFDATA_ONLINE', self.enJfdataOnline)
        if self.enDataHome:
            sdir = sdir.replace('$DATA_HOME', self.enDataHome)
        if self.enHome:
            sdir = sdir.replace('$HOME', self.enHome)
        if self.enJfdata:
            sdir = sdir.replace('$JFDATA', self.enJfdata)
        return sdir

    def getCluster(self):
        self.hostname = socket.gethostname()
        self.loger.writeLog('host: %s' % (self.hostname))
        self.ip = socket.gethostbyname(self.hostname)
        self.loger.writeLog('host ip: %s' % (self.ip))
        # ipList = socket.gethostbyname_ex(hostname)
        # ipList
        strlocalip = str(self.ip)
        fHosts = open(self.cfg.hostClu,'r')
        for line in fHosts:
            line = line.strip()
            # print line
            ahoclu = line.split(' ')
            if ahoclu[0] == strlocalip:
                self.cluster = ahoclu[1]
                break
        fHosts.close()
        self.loger.writeLog('cluster: %s' % self.cluster)
        if not self.cluster:
            self.loger.writeLog('cannot get cluster of the host %s' % self.ip)
            exit(-1)


class DirsManager(BaseManager):
    pass


def main():
    callName = sys.argv[0]
    servIp = sys.argv[1]
    cfg = Conf(callName)
    loger = LogWriter(cfg)
    # loger.writeLog('connect to oracle')
    # cfg.getDb()
    # baseName = os.path.basename(callName)
    # sysName = os.path.splitext(baseName)[0]
    # logFile = '%s/%s%s' % ('../log', sysName, '.log')
    # cfgFile = '%s.cfg' % 'scandir'
    # cfg = Conf(cfgFile)
    lister = ListDir(cfg,servIp)
    lister.loger = loger
    lister.pid = os.getpid()
    lister.getCluster()
    lister.getEnv()
    lister.getDirs()
    lister.loger.writeLog('list host path')
    lister.listPath()
    lister.loger.writeLog(lister.hostDirs.dirs)
    lister.sendDir()

if __name__ == '__main__':
    main()


