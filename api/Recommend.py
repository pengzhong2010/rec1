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
import sys
import os
sys.path.append(os.path.expanduser('/data/dev/pyspider'))
from util import ItemIDExtractor

class Index(tornado.web.RequestHandler):

    rec_url = 'http://recapi.datagrand.com/relate/datagranddoc'

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        pass
        # appname = self.get_argument('appname')
        # appid = self.get_argument('appid')
        # data_url = self.get_argument('url')
        # cnt = self.get_argument('cnt')
        cnt=10

        # #get itemid
        itemid_extractor = ItemIDExtractor()
        retcode, itemid = itemid_extractor.extract("datagrnddoc",
                                                   "http://www.datagrand.com/blog/datagrande-query-2.html")
        # print retcode
        # print itemid
        # self.finish()
        if retcode:
            self.set_status(500)
            self.write("url not exists")
            self.finish()

        rec_get_query_url=self.rec_url+'?itemid='+itemid+'&cnt='+str(cnt)

        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch,
                                          rec_get_query_url )

    #     # body = json.loads(response.body)
    #     body=response.body
        self.write(response.body)
        self.finish()

        rec_str=response.body
        rec_dict = json.loads(rec_str)
        rec_status = rec_dict.get('status')
        if not rec_status:
            self.write("rec faild")
            self.finish()
        if rec_status == 'FAIL':
            self.write("rec status FAIL")
            self.finish()
        rec_recdata = rec_dict.get('recdata')
        if not rec_recdata:
            self.write("rec data not exist")
            self.finish()
        if len(rec_recdata)==0:
            self.write("rec data not exist")
            self.finish()
        rec_items_list=[]
        for i in rec_recdata:
            rec_items_list.append(i['itemid'])

        self.write(rec_items_list)
        self.finish()










