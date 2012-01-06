import tornado.options
import tornado.web
from tornado.escape import utf8
import settings
import logging
import simplejson as json
from lib.connection import APNSConn, FeedbackConn


class BaseHandler(tornado.web.RequestHandler):
    def get_int_argument(self, name, default=None):
        value = self.get_argument(name, default=default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def error(self, status_code, status_txt, data=None):
        """write an api error in the appropriate response format"""
        self.api_response(status_code=status_code, status_txt=status_txt, data=data)

    def api_response(self, data, status_code=200, status_txt="OK"):
        """write an api response in json"""
        self.set_header("Content-Type", "application/json; charset=utf-8")
        self.finish(json.dumps(dict(data=data, status_code=status_code, status_txt=status_txt)))

class PushHandler(BaseHandler):
    def get(self):
        token = utf8(self.get_argument("token"))
        alert = self.get_argument("alert", None)
        badge = self.get_argument("badge", None)
        sound = self.get_argument("sound", None)
        expiry = self.get_argument("expiry", None)
        extra = self.get_argument("extra", None)
        resp = apns.push(token, alert, badge, sound, expiry, extra)
        self.api_response(resp)

class StatsHandler(BaseHandler):
    def get(self):
        self.api_response(apns.get_stats())

if __name__ == "__main__":
    tornado.options.define("port", default=8888, help="Listen on port", type=int)
    tornado.options.parse_command_line()

    # the global apns
    apns = APNSConn()
    feedback = FeedbackConn()

    application = tornado.web.Application([
        (r"/push", PushHandler),
        (r"/stats", StatsHandler),
    ])
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
