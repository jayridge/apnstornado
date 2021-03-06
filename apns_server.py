import sys
import tornado.options
import tornado.web
from tornado.escape import utf8
import settings
import logging
import simplejson as json
from lib.MemcachePool import mc
from lib.connection import APNSConn, FeedbackConn


class BaseHandler(tornado.web.RequestHandler):
    def get_int_argument(self, name, default=None):
        value = self.get_argument(name, default=default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def error(self, status_code=500, status_txt=None, data=None):
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
        badge = self.get_int_argument("badge", None)
        sound = self.get_argument("sound", None)
        expiry = self.get_argument("expiry", None)
        extra = self.get_argument("extra", None)
        timestamp = self.get_argument("timestamp", None)

        if extra:
            extra = json.loads(extra)

        status = 'ERROR'
        code = 500
        resp = {'queued':False, 'exception':None}
        try:
            resp['queued'] = apns.push(token, alert, badge, sound, expiry, extra, timestamp)
            if resp['queued']:
                status = 'OK'
                code = 200
            self.api_response(resp, status_code=code, status_txt=status)
        except Exception as e:
            logging.error("push failed", exc_info=e)
            self.error(status_code=500, status_txt=status, data=str(e))
            

class FlushHandler(BaseHandler):
    def get(self):
        token = utf8(self.get_argument("token"))
        try:
            mc.delete(token)
            self.api_response(dict(token=token))
        except Exception as e:
            self.error(status_code=500, status_txt='ERROR', data=str(e))


class StatsHandler(BaseHandler):
    def get(self):
        self.api_response(apns.get_stats())

if __name__ == "__main__":
    tornado.options.define("port", default=8888, help="Listen on port", type=int)
    tornado.options.parse_command_line()
    logging.getLogger().setLevel(settings.get('logging_level'))

    # the global apns
    apns = APNSConn()
    if settings.get('feedback_enabled'):
        feedback = FeedbackConn()

    application = tornado.web.Application([
        (r"/push", PushHandler),
        (r"/stats", StatsHandler),
        (r"/flush", FlushHandler),
    ])
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()
