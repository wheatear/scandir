#!/usr/bin/env python
"""emergency provisioning ps control model"""

import sys
import os
import time
import multiprocessing
import signal
# import cx_Oracle as orcl
import pexpect
import pexpect.pxssh
import threading


# myssh = pexpect.pxssh.pxssh()
# myssh.login('10.7.5.165','bjjk12','tst,12')
# myssh.sendline('pxsshtest.sh')
# myssh.prompt()
# print myssh.before
# myssh.logout()

# myssh = pexpect.pxssh.pxssh()
# myssh.login('10.7.5.165','bjjk12','tst,12')
# myssh.sendline('nohup pxsshtest.sh &')
# myssh.prompt()
# print myssh.before
# myssh.logout()

def remexe():
    myssh = pexpect.pxssh.pxssh()
    myssh.login('10.7.5.165', 'bjjk12', 'tst,12')
    print 'remexe login ok.'
    myssh.sendline('/usr/bin/ksh -c "nohup pxsshtest.sh &"')
    myssh.prompt()
    print myssh.before
    myssh.logout()
    print 'remexe logout ok.'

def checkexe():
    myssh = pexpect.pxssh.pxssh()
    myssh.login('10.7.5.165', 'bjjk12', 'tst,12')
    print 'checker login.'
    for i in range(7):
        myssh.sendline('ps -exf|grep pxssh')
        myssh.prompt()
        print myssh.before
        time.sleep(10)
    myssh.logout()
    print 'checker logout.'

def scpFile(self,lfile,ruser,rpasswd,rhost,rpath):
    cmd = 'scp %s %s@%s:%s' % (lfile, ruser, rhost, rpath)
    try:
        pscp = pexpect.spawn(cmd)
        pscp.expect('Password:')
        pscp.sendline(rpasswd)
        index = pscp.expect(pexpect.EOF, pexpect.TIMEOUT)
        if index == 1:
            return False
    except (pexpect.TIMEOUT, pexpect.EOF), e:
        print 'scp file %s failed.' % lfile
        return False
    return True


def main():
    rex = threading.Thread(target=remexe,name='remoteexe')
    checker = threading.Thread(target=checkexe)
    rex.start()
    checker.start()




# /usr/local/bin/bash -c 'nohup pxsshtest.sh &'
# /usr/local/bin/bash -c nohup pxsshtest.sh &
# ps -exf|grep pxssh

if __name__ == '__main__':
    main()