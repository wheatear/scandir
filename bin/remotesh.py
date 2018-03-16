#!/usr/bin/env python
"""emergency provisioning ps control model"""

import sys
import os
import time
import multiprocessing
import Queue
import signal
# import cx_Oracle as orcl
import socket
import hostdirs
from multiprocessing.managers import BaseManager
import pexpect
import pexpect.pxssh
import base64
import logging
import re
from config import *


class RemoteSh(multiprocessing.Process):
    def __init__(self,cfg,cmdfile,dest):
        multiprocessing.Process.__init__(self)
        self.cfg = cfg
        self.cmdFile = cmdfile
        self.dest = dest
        self.aHosts = []
        self.aCmds = []
        self.cmdUser = 'nms'
        self.cmdPwd = 'ailk,123'

    def readCmd(self):
        fCmd = open(self.cmdFile,'r')
        for line in fCmd:
            line = line.strip()
            if len(line) == 0:
                continue
            if line[0] == '#':
                continue
            self.aCmds.append(line)
        fCmd.close()

    def run(self):
        # self.loger.openLog('%s/CLIENTCALLER.log' % self.cfg.logDir)
        logging.info('client starter(%d) running' ,os.getpid())
        self.getLocalIp()
        self.getAllHosts()
        self.readCmd()
        self.startAll()
        # self.asyncAll()

    def getAllHosts(self):
        # for host
        # fHosts = open(self.cfg.hostClu, 'r')
        # for cluster
        if self.dest == '-c':
            hostFile = self.cfg.cluster
        elif self.dest == '-h':
            hostFile = self.cfg.hostClu
        print hostFile
        fHosts = open(hostFile, 'r')
        for line in fHosts:
            line = line.strip()
            if len(line) == 0:
                continue
            aLine = line.split(' ')
            if self.dest == '-c':
                aInfo = aLine
            elif self.dest == '-h':
                aInfo = [aLine[1],aLine[0],aLine[2],aLine[3]]
            if aInfo[1] == self.localIp:
                continue
            self.aHosts.append(aInfo)
        fHosts.close()

    def startAll(self):
        logging.info('all host to connect: %s' , self.aHosts)
        # aHosts = self.aHosts
        # pool = multiprocessing.Pool(processes=10)
        for h in self.aHosts:
            # h.append(self.localIp)
            if h[1] == self.localIp:
                continue
            logging.info('run client %s@%s(%s)' , h[2], h[0], h[1])
            self.runClient(*h)
            # pool.apply_async(self.runClient,h)
        # pool.close()
        # pool.join()

    # for hosts
    # def runClient(self,float_ip,cluster_code,user_name,user_pw):
    # for cluster
    def runClient(self,cluster_code, float_ip, user_name, user_pw):
        clt = pexpect.pxssh.pxssh()
        flog = open('%s/pxssh.log' % (self.cfg.logDir),'w')
        # clt.logfile = flog
        clt.logfile = sys.stdout
        logging.info('connect to host: %s %s %s' ,cluster_code,float_ip,user_name)
        print 'connect to host: %s %s %s' % (cluster_code,float_ip,user_name)

        plain_pw = base64.decodestring(user_pw)
        # con = clt.login(float_ip,user_name,plain_pw)
        con = clt.login(float_ip, user_name, 'Ngtst!234')
        logging.info('connect: %s' ,con)
        cmdcontinue = 0
        for cmd in self.aCmds:
            logging.info('exec: %s' ,cmd)
            print 'exec: %s' % ( cmd)
            cmd = cmd.replace('$USER',user_name)
            clt.sendline(cmd)
            if cmd[:2] == 'if':
                cmdcontinue = 1
            if cmd[0:2] == 'fi':
                cmdcontinue = 0
            if cmdcontinue == 1:
                continue
            clt.prompt()
            logging.info('exec: %s' ,clt.before)
        clt.logout()
        # cltcmd = '/usr/bin/ksh -c "nohup /jfdata01/kt/operation/test/python/scandir/bin/scandirclient.py %s &"' % serv_ip
        # # clt.sendline('/usr/bin/ksh -c "nohup /nms/scandir/bin/scandirclient.py &"')
        # clt.sendline(cltcmd)
        # clt.prompt()
        # self.loger.writeLog('exec: %s' % (clt.before))

    def getLocalIp(self):
        self.hostname = socket.gethostname()
        logging.info('local host: %s' ,self.hostname)
        self.localIp = socket.gethostbyname(self.hostname)
        return self.localIp



class DirsManager(BaseManager):
    pass




def main():
    callName = sys.argv[0]
    cmdfile = sys.argv[1]
    dest = sys.argv[2]
    cfg = Conf(callName)
    logging.basicConfig(filename=cfg.logFile, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y%m%d%I%M%S')
    # loger = LogWriter(cfg)
    # logging.info('connect to oracle')
    # cfg.getDb()
    # baseName = os.path.basename(callName)
    # sysName = os.path.splitext(baseName)[0]
    # logFile = '%s/%s%s' % ('../log', sysName, '.log')
    # cfgFile = '%s.cfg' % 'scandir'
    # cfgFile = '%s.cfg' % 'scandir'
    # cfg = Conf(cfgFile)
    remoteShell = RemoteSh(cfg,cmdfile,dest)
    # remoteShell.loger = loger
    remoteShell.start()

    remoteShell.join()

    # dirManager = startManager()

if __name__ == '__main__':
    main()
