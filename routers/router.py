import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen

from api import Recommend
from api import Test

class Router(tornado.web.Application):
    handlers=[
            (r"/related", Recommend.Index),
            (r"/personal", Recommend.Personalized),
            (r"/test", Test.Index),
        ]
    settings = {
        # 'template_path': 'templates',
        # 'static_path': 'static'
    }
    def __init__(self):
        tornado.web.Application.__init__(self, self.handlers, **self.settings)