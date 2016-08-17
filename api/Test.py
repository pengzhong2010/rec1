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

class Index(tornado.web.RequestHandler):

    def get(self):
        body='bbbcccxxx'
        self.write("""
    <div style="text-align: center">
        %s
    </div>""" % (body))
