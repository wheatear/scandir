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
import logging
import re

from config import *


class RefreshScanItem(object):
    'refresh scan item every day'
    def __init__(self, cfg):
        self.cfg = cfg
        self.filterKey = ("bak","stat","err","redo","log","JFLOG")
        self.aClus = []
        self.aHosts = []
        self.cmdUser = 'nms'
        self.cmdPwd = 'ailk,123'

    def refreshItem(self):
        dScanItem = {}
        dScanItemOld = {}
        self.cfg.getDb()
        sql = 'select distinct c.cluster_code,a.buss_type,a.input_path,a.output_path1,a.output_path2  from APP_MANAGE_CONFIG a,SCANDIR_HOST h,SCANDIR_CLUSTER c where a.vm_ip=h.vm_ip and h.cluster_code=c.cluster_code and  a.input_path is not null order by c.cluster_code,a.buss_type,a.input_path'
        sqlOld = 'select cluster_code,buss_type,path from SCANDIR_DIR where type=1'
        self.loger.writeLog('sql: %s' % sql)
        curQry = self.cfg.db.cursor()
        curQry.execute(sql)
        rows = curQry.fetchall()
        for item in rows:
            clucode = item[0]
            busstype = item[1]
            if item[2]:
                paths = item[2].split(';')
            if item[3]:
                paths.extend(item[3].split(';'))
            if item[4]:
                paths.extend(item[4].split(';'))

            for pa in paths:
                filted = 0
                for fk in self.filterKey:
                    if pa.find(fk) > -1:
                        filted = 1
                        break
                if filted > 0:
                    continue
                pa = pa.replace('(','')
                pa = pa.replace(')', '')
                itemkey = '%s:%s' % (clucode,pa)
                dScanItem[itemkey] = busstype
        self.loger.writeLog('sql: %s' % sqlOld)
        curQry.execute(sqlOld)
        rowsold = curQry.fetchall()
        for item in rowsold:
            itemkey = '%s:%s' % (item[0],item[2])
            dScanItemOld[itemkey] = (item[1])

        self.loger.writeLog('scan items: %s' % dScanItem)
        scanNum = len(dScanItem)
        scanNumOld = len(dScanItemOld)
        self.loger.writeLog('old number: %d , new number: %d' % (scanNumOld,scanNum))
        numDiff = scanNumOld - scanNum
        if numDiff > 100:
            return -1
        self.loger.writeLog('check diffence')
        for key,value in dScanItemOld.items():
            if key in dScanItem:
                dScanItem[key] = value
                del dScanItemOld[key]
        if numDiff == 0 and len(dScanItemOld) == 0:
            return 0

        delsql = 'delete from SCANDIR_DIR where type=1'
        self.loger.writeLog('delete old items: %s' % delsql)
        curQry.execute(delsql)
        curQry.connection.commit()
        insertsql = 'insert into SCANDIR_DIR(cluster_code,buss_type,path,type) values(:1,:2,:3,:4)'
        self.loger.writeLog('insert new host dirs: %s' % insertsql)
        i = 0
        for k,v in dScanItem.items():
            i += 1
            clucode,path = k.split(':')
            curQry.execute(insertsql,(clucode,v,path,1))
            curQry.connection.commit()
        curQry.close()
        return i

    def makeHostDirs(self):
        cur = self.cfg.db.cursor()
        fDir = open(self.cfg.hostDirs,'w')
        sql = 'select cluster_code,buss_type,path from SCANDIR_DIR where type<=2'
        cur.execute(sql)
        self.loger.writeLog( 'make host dir file')
        for row in cur:
            # print row
            fDir.write('%s %s %s\n' % row)
        fDir.close()
        cur.close()

    def makeHostClu(self):
        cur = self.cfg.db.cursor()
        fDir = open(self.cfg.hostClu,'w')
        sql = 'select vm_ip,cluster_code,user_name,user_pw from SCANDIR_HOST'
        cur.execute(sql)
        self.loger.writeLog( 'make host cluster file')
        for row in cur:
            # print row
            self.aHosts.append(row)
            fDir.write('%s %s %s %s\n' % row)
        fDir.close()
        cur.close()

    def makeCluster(self):
        cur = self.cfg.db.cursor()
        fDir = open(self.cfg.cluster,'w')
        sql = 'select cluster_code,float_ip,user_name,user_pw from SCANDIR_CLUSTER'
        cur.execute(sql)
        # self.loger.writeLog( 'make %s file\n' % self.cfg.cluster)
        for row in cur:
            # print row
            self.aClus.append(row)
            fDir.write('%s %s %s %s\n' % row)
        fDir.close()
        cur.close()

    def spreadCluFile(self,remotepath,*files):
        # cur = self.cfg.db.cursor()
        # sql = 'select cluster_code,float_ip,user_name,user_pw from SCANDIR_CLUSTER'
        # cur.execute(sql)
        # aHosts = cur.fetchall()
        aHosts = self.aHosts
        for h in aHosts:
            for fi in files:
                if self.scpFile(fi, self.cmdUser, self.cmdPwd, h[0], remotepath):
                    self.loger.writeLog( 'put file:%s to cluster:%s(%s) ok.' % (fi,h[0], h[1]))
                else:
                    self.loger.writeLog('put file:%s to cluster:%s(%s) failed.' % (fi,h[0], h[1]))

    def scpFile(self,lfile,ruser,rpasswd,rhost,rpath):
        cmd = 'scp %s %s@%s:%s' % (lfile,self.cmdUser,rhost,rpath)
        self.loger.writeLog( cmd)
        try:
            pscp = pexpect.spawn(cmd)
            pscp.logfile = sys.stdout
            index = pscp.expect(['assword:', pexpect.EOF])
            if index == 0:
                # pscp.sendline(base64.decodestring(rpasswd))
                pscp.sendline(self.cmdPwd)
            elif index == 1:
                return self.parseResp(pscp)
            index = pscp.expect(['assword:', pexpect.EOF])
            if index == 0:
                logging.warn('passward error for hotst: %s', rhost)
                return False
            elif index == 1:
                return self.parseResp(pscp)
            # if index == 1:
            #     return False
        except (pexpect.TIMEOUT,pexpect.EOF),e:
            self.loger.writeLog('scp file %s:%s failed. %s' % (rhost,lfile,e))
            return False
        return True

    def parseResp(self,pscp):
        i = 0
        resp = pscp.before
        reg = re.compile(' \r\n\w(.+)')
        errres = re.findall(reg, resp)
        errnum = len(errres)
        if errnum > 0:
            for erf in errres:
                logging.info(erf)
            logging.info('%d files error', errnum)
            resp = re.sub(reg, '', resp)
        fileret = pscp.before.split('\r\n\r')
        for frt in fileret:
            frt = frt.strip()
            if frt == '':
                continue
            i += 1
            ret = frt.split('\r')
            if len(ret) > 1:
                logging.info(ret[1])
            else:
                logging.info(ret[0])
        logging.info('%d files ok', i)
        # logging.info(pscp.match.group())
        return True


def main():
    callName = sys.argv[0]
    # baseName = os.path.basename(callName)
    # binDir = os.path.dirname(callName)
    # appHome = os.path.dirname(binDir)
    # sysName = os.path.splitext(baseName)[0]
    # logFile = '%s/log/%s%s' % (appHome, sysName, '.log')
    # cfgFile = '%s.cfg' % 'scandir'
    cfg = Conf(callName)
    loger = LogWriter(cfg)
    loger.writeLog('connect to oracle')
    cfg.getDb()
    refs = RefreshScanItem(cfg)
    refs.loger = loger
    # refNum = refs.refreshItem()
    # if refNum == 0:
    #     print 'no item to refresh.'
    #     exit(0)

    logging.basicConfig(filename='/nms/scandir/log/refreshscanitem.py.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s',datefmt='%Y%m%d%I%M%S')
    logging.info('spread file starting...')

    refs.loger.writeLog('make %s file\n' % refs.cfg.cluster)
    refs.makeCluster()
    refs.loger.writeLog('make %s file\n' % refs.cfg.hostClu)
    refs.makeHostClu()
    refs.loger.writeLog('refresh host and dirs')
    refs.refreshItem()
    refs.loger.writeLog('make %s file\n' % refs.cfg.hostDirs)
    refs.makeHostDirs()
    loger.writeLog( 'put file:%s %s' % (refs.cfg.hostDirs,refs.cfg.hostClu))
    # refs.spreadCluFile(refs.cfg.cfgDir,(refs.cfg.hostDirs,refs.cfg.hostClu))
    refs.spreadCluFile('/nms/scandir/config',refs.cfg.hostDirs,refs.cfg.hostClu,refs.cfg.cluster)



if __name__ == '__main__':
    main()