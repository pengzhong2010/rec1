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

        rec_get_query_url=self.rec_url+'?itemid='+itemid

        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch,
                                          rec_get_query_url )

    #     # body = json.loads(response.body)
    #     body=response.body
        self.write(response.body)
        self.finish()