# -*- coding:utf-8 -*-
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen

import urllib
import json
import datetime
import time
# import sys
# import os
# sys.path.append(os.path.expanduser('/data/dev/pyspider'))
# from util import ItemIDExtractor

# from lib.log import LOG
from lib.rec_driver import *
# from pyredis import RedisKv

from lib.pymysql import PyMysql

from lib.common import base_path

class Index(tornado.web.RequestHandler):
    mysql_con=''
    def get(self):
        # pass

        # print base_path()

        # LOG.instance().send_task('wlog.write_log', args=["abc"])
        # LOG.ilog("aaaaaa")

        self.mysql_con = PyMysql("rr-2zeq53lf7562ks1ko.mysql.rds.aliyuncs.com", 3306, "siterec", "siterec123456",
                                 "siterec_datacenter")
        # sql = " select * from item_info where item_infoid=%s limit 1"

        itemids_str= "'207080','52','44','78'"
        sql1 = "and itemid in (%s)" % itemids_str
        sql0 = " select * from item_info where appid=%s "+sql1
        # print sql
        ret = self.mysql_con.select(sql0,'many',(237389))
        print ret

        return







