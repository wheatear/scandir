#!/usr/bin/env python
"""class for dirs of host"""


class HostDirs(object):
    def __init__(self):
        self.ip = None
        self.cluster = None
        self.dirs = {}
        self.dBusi = {}

    def __str__(self):
        str = ''
        if self.dirs is None:
            str = '[None]'
        else:
            str = "['%s','%s',%s]" % (self.cluster,self.ip,self.dirs)
        return str

    def getBusiDic(self):
        # self.dBusi = {}
        for (dirName,(busi,optime,filenum)) in self.dirs.items():
            if busi in self.dBusi:
                self.dBusi[busi] += 1
            else:
                self.dBusi[busi] = 1
        return self.dBusi

