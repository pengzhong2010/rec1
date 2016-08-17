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

    def get(self):
        itemid_extractor = ItemIDExtractor()
        retcode, itemid = itemid_extractor.extract("datagrnddoc",
                                                   "http://www.datagrand.com/blog/smg-the-next-unicorn.html")
        print retcode
        print itemid
        body='ddd'
        self.write("""
    <div style="text-align: center">
        %s
    </div>""" % (body))
