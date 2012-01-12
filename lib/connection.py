import settings
import logging
import socket
import time
import struct
import ctypes
from tornado import ioloop
from tornado.iostream import IOStream, SSLIOStream
from collections import deque
from MemcachePool import mc
from utils import *

MAX_PAYLOAD_BYTES = 256

class APNSConn():
    def __init__(self, host=None, certfile=None, loop=None):
        self.stats = {
            'disconnects':0,
            'notifications':0,
            'invalid_tokens':0,
        }
        self.started = time.time()
        self.ioloop = loop or ioloop.IOLoop.instance()
        self.host = host or settings.get('apns_host')
        self.certfile = certfile or settings.get('certfile')
        self.write_queue = deque()
        self.recent = deque(maxlen=100)
        # N.B. Python upgrades ints to longs and this is a binary protocol so...
        self.generation = ctypes.c_uint32(0)
        self.connect()

    def get_stats(self):
        stats = self.stats.copy()
        stats['queue_len'] = len(self.write_queue)
        stats['uptime'] = time.time() - self.started
        return stats
        
    def push(self, token, alert=None, badge=None, sound=None, expiry=None, extra=None, timestamp=None):
        '''
        This is really the only api you want to use. Pushes a notification onto the queue
        for non-flagged users. The queue is processed in the tornado event loop.
        '''
        flagged = mc.get(token)
        if flagged:
            if not timestamp or timestamp > flagged:
                self.stats['invalid_tokens'] += 1
                return False

        self.generation.value += 1
        identifier = self.generation.value
        msg = create_message(token, alert=alert, badge=badge, sound=sound,
            identifier=identifier, expiry=expiry, extra=extra)
        if len(msg) > MAX_PAYLOAD_BYTES:
            raise ValueError, u"max payload(%d) exceeded: %d" % (MAX_PAYLOAD_BYTES, len(msg))

        self.write_queue.append(msg)
        self.recent.append(dict(identifier=identifier, token=token))
        self.ioloop.add_callback(self.push_one)
        return True

    def push_one(self):
        if len(self.write_queue) and not self.stream.closed():
            msg = self.write_queue.popleft()
            try:
                self.stream.write(msg)
                self.stats['notifications'] += 1
            except:
                self.write_queue.appendleft(msg)
                return False
            return True
        return False

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = SSLIOStream(self.s, ssl_options=dict(certfile=self.certfile))
        self.stream.connect(self.host, self._on_connect)
        self.stream.read_until_close(self._on_close, streaming_callback=self._on_read)

    def _on_connect(self):
        '''
        Process the backlog, hoss.
        '''
        logging.info('connected to %s:%d' % (self.host[0], self.host[1]))
        while self.push_one(): continue

    def _on_read(self, data):
        '''
        The only message we expect here is an error response... sadly, followed by
        a disconnect. 
        '''
        logging.info('_on_read: %d bytes' % (len(data)))
        try:
            status, identifier, err_string = parse_response(data)
            logging.warning('_on_read err: %d %d %s' % (status, identifier, err_string))
            if status == 8:
                for msg in self.recent:
                    if msg['identifier'] == identifier:
                        token = msg['token']
                        logging.info('flagging token: %s' % (token))
                        self.stats['invalid_tokens'] += 1
                        mc.set(token, int(time.time()))
        except:
            logging.info('parse_response failed')

    def _on_close(self, data):
        '''
        This triggers the reconnect given reconnect_lag from settings. This should
        probably be an exponential backoff.
        '''
        logging.info('_on_close')
        self.stats['disconnects'] += 1
        try:
            self.stream.close()
            self.s.close()
        except:
            pass
        self.ioloop.add_timeout(time.time()+settings.get('apns_reconnect_lag'), self.connect)


class FeedbackConn():
    def __init__(self, host=None, certfile=None, loop=None):
        self.ioloop = loop or ioloop.IOLoop.instance()
        self.host = host or settings.get('feedback_host')
        self.certfile = certfile or settings.get('certfile')
        self.connect()

    def connect(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.stream = SSLIOStream(self.s, read_chunk_size=38, ssl_options=dict(certfile=self.certfile))
        self.stream.connect(self.host, self._on_connect)
        self.stream.read_until_close(self._on_close, streaming_callback=self._on_read)

    def _on_connect(self):
        logging.info("connected to %s:%d" % (self.host[0], self.host[1]))

    def _on_read(self, data):
        #logging.info("read %d bytes" % len(data))
        if len(data) == 38:
            timestamp, toklen, token = struct.unpack_from('!IH32s', data, 0)
            logging.info("flagging user %s at %d" % (token.encode('hex'), timestamp))
            mc.set(token.encode('hex'), timestamp)

    def _on_close(self, data):
        logging.info("disconnected %s:%d" % (self.host[0], self.host[1]))
        try:
            self.stream.close()
            self.s.close()
        except:
            pass
        self.ioloop.add_timeout(time.time()+settings.get('feedback_reconnect_lag'), self.connect)
