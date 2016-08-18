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
        print retcode
        print itemid
        self.finish()
        # if retcode:
        #     self.set_status(500)
        #     self.write("itemid not exists")
        #     self.finish()




    #     client = tornado.httpclient.AsyncHTTPClient()
    #     response = yield tornado.gen.Task(client.fetch,
    #                                       "http://127.0.0.1/5.php" )
    #     # body = json.loads(response.body)
    #     body=response.body
    #     self.write("""
    # <div style="text-align: center">
    #     %s
    # </div>""" % (body))
    #     self.finish()