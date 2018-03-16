#!/usr/bin/env python
'''emergency provisioning ps control model'''

import sys
import os
import time
import multiprocessing
import cx_Oracle as orcl

# import loader
# import spliter
# import netinter


class Conf(object):
    'data source configuration'
    def __init__(self, callname,cfgfile='scandir.cfg'):
        self.dbusr = None
        self.pawd = None
        self.sid = None
        self.host = None
        self.port = None
        self.dLevel = None
        self.level = 'INFO'
        self.logFile = None
        self.log = None
        self.db = None
        self.logWriter = None

        #		execfile(cfgFile)
        self.parseSysEnv(callname,cfgfile)
        fCfg = open(self.cfgFile, 'r')
        exec fCfg
        fCfg.close()
        if dbusr: self.dbusr = dbusr
        if pawd: self.pawd = pawd
        if sid: self.sid = sid
        if host: self.host = host
        if port: self.port = port
        if dLOGLEVEL: self.dLevel = dLOGLEVEL
        if LOGLEVEL: self.level = LOGLEVEL
        if hostDirs: self.hostDirs = '%s/%s' % (self.cfgDir,hostDirs)
        if hostClu: self.hostClu = '%s/%s' % (self.cfgDir,hostClu)
        if cluster: self.cluster = '%s/%s' % (self.cfgDir,cluster)
    def getDb(self):
        if self.db: return self.db
        try:
            connstr = '%s/%s@%s/%s' % (self.dbusr,self.pawd,self.host,self.sid)
            # dsn = orcl.makedsn(self.host, self.port, self.sid)
            # dsn = dsn.replace('SID=', 'SERVICE_NAME=')
            self.db = orcl.Connection(connstr)
        # cursor = con.cursor()
        except Exception, e:
            print 'could not connec to oracle(%s:%s/%s), %s' % (self.host, self.port, self.sid, e)
            exit()
        return self.db

    def closeDb(self):
        self.db.close()

    def parseSysEnv(self,callname,cfgfile):
        baseName = os.path.basename(callname)
        self.binDir = os.path.dirname(callname)
        if self.binDir == '':
            self.binDir = '.'
        if self.binDir == '.':
            self.appHome = '..'
        else:
            self.appHome = os.path.dirname(self.binDir)
        if self.appHome == '':
            self.appHome = '.'
        self.logDir = '%s/%s' % (self.appHome,'log')
        # self.cfgDir = '%s/%s' % (self.appHome,'config')
        self.cfgDir = '%s/%s' % (self.appHome, 'config')
        self.cfgFile = '%s/%s' % (self.cfgDir,cfgfile)
        self.sysName = os.path.splitext(baseName)[0]
        self.logFile = '%s/%s.log' % (self.logDir,self.sysName)
        print 'bindir: %s, apphome: %s' % (self.binDir,self.appHome)


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            cls._instance = super(Singleton, cls).__new__(cls, *args, **kw)
        return cls._instance


class MultiLog(multiprocessing.Process):
    'Log class'
    def __init__(self, conf,qulog):
        multiprocessing.Process.__init__(self)
        if not hasattr(self, 'fLog'):
            self.dLevel = conf.dLevel
            self.level = self.dLevel[conf.level]
            self.logName = conf.logFile
            self.fLog = open(self.logName, 'a')
            self.quLog = qulog
            self.exit = None
    def run(self):
        while not self.exit:
            # print('psqueue size: %d' % (self.quLog.qsize()))
            (pid,logType, message) = self.quLog.get()
            if self.dLevel[logType] < self.level:
                return
            sTime = time.strftime("%Y%m%d%H%M%S", time.localtime())
            msg = '%s %s %s %s%s' % (sTime, pid, logType, message, '\n')
            self.fLog.write(msg)
            print msg
            self.fLog.flush()
            if message is None:
                print 'exit'
                self.close()
                break
    def close(self):
        self.fLog.close()


class MultiLogWriter(object):
    def __init__(self,qlog):
        self.qLog = qlog
        self.pid = os.getpid()
    def writeLog(self,logtype, message):
         self.qLog.put((self.pid, logtype, message))
         print message

class LogWriter(object):
    def __init__(self,conf):
        self.pid = os.getpid()
        self.dLevel = conf.dLevel
        self.level = self.dLevel[conf.level]
        self.logName = conf.logFile
        # self.fLog = open(self.logName, 'a')
        # self.quLog = qulog
        # self.exit = None
        try:
            self.fLog = open(self.logName,'a')
        except Exception,e:
            print 'cannot open log file:%s' % self.logName
            exit -1

    def writeLog(self,message,logtype='INFO'):
        if self.dLevel[logtype] < self.level:
            return
        sTime = time.strftime("%Y%m%d%H%M%S", time.localtime())
        msg = '%s %s %s %s%s' % (sTime, self.pid, logtype, message, '\n')
        self.fLog.write(msg)
        print msg
        self.fLog.flush()

    def openLog(self,logname):
        self.pid = os.getpid()
        self.logName = logname
        if self.fLog:
            self.fLog.close()
        try:
            self.fLog = open(self.logName,'a')
        except Exception,e:
            print 'cannot open log file:%s' % logfile
            exit -1


