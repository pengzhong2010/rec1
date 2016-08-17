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

from routers import router

from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)



if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = router.Router()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
