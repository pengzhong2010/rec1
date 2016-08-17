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
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        # query = self.get_argument('q')
        client = tornado.httpclient.AsyncHTTPClient()
        response = yield tornado.gen.Task(client.fetch,
                                          "http://127.0.0.1/5.php" )
        # body = json.loads(response.body)
        body=response.body
        self.write("""
    <div style="text-align: center">
        %s
    </div>""" % (body))
        self.finish()