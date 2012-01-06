import pylibmc
import logging
import settings

"""
This is a transparent library that wraps a memcache client, lazily initiating connections and swallowing all errors

from MemcachePool import mc
mc.get(key)
mc.set(key,value)
"""

class mc(object):
    _conn = None
    
    @classmethod
    def setup(self):
        if not self._conn:
            self._conn = pylibmc.Client(settings.get("memcached"))
            self._conn.set_behaviors({
                    # socket connection timeout (seconds)
                    'connect_timeout': 2, 
                    # packet receive timeout (milliseconds)
                    'receive_timeout': 500, 
                    # packet send timeout (milliseconds)
                    'send_timeout': 500, 
                    # num of failures before server marked as failed
                    'failure_limit': 5, 
                    # number of seconds before retrying connection to failed server
                    '_retry_timeout': 60, 
                    # don't delete a host from pool (avoid remapping of keys on server failure)
                    '_auto_eject_hosts': False
                })
        return self._conn
    
    @classmethod
    def get_multi(self, keys, *args, **kwargs):
        assert isinstance(keys, (list, tuple))
        for key in keys:
            assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.get_multi(keys, *args, **kwargs)
        except:
            logging.exception('failed querying memcached %r %r %r' % (keys, args, kwargs))

    @classmethod
    def delete_multi(self, keys, *args, **kwargs):
        assert isinstance(keys, (list, tuple))
        for key in keys:
            assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.delete_multi(keys, *args, **kwargs)
        except:
            logging.exception('failed querying memcached %r %r %r' % (keys, args, kwargs))

    @classmethod
    def set_multi(self, data, *args, **kwargs):
        assert isinstance(data, dict)
        for key in data:
            assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.set_multi(data, *args, **kwargs)
        except:
            logging.exception('failed querying memcached %r %r %r' % (data, args, kwargs))

    @classmethod
    def incr_multi(self, keys, *args, **kwargs):
        assert isinstance(keys, (list, tuple))
        for key in keys:
            assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.incr_multi(keys, *args, **kwargs)
        except:
            logging.exception('failed querying memcached %r %r %r' % (keys, args, kwargs))

    @classmethod
    def get_stats(self):
        try:
            mc.setup()
            return mc._conn.get_stats()
        except:
            logging.exception('failed querying memcached get_stats')

    @classmethod
    def flush_all(self):
        try:
            mc.setup()
            return mc._conn.flush_all()
        except:
            logging.exception('failed querying memcached flush_all')

    @classmethod
    def disconnect_all(self):
        try:
            mc.setup()
            return mc._conn.disconnect_all()
        except:
            logging.exception('failed running disconnect_all')

    @classmethod
    def add(self, key, *args, **kwargs):
        assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.add(key, *args, **kwargs)
        except:
            logging.exception('failed memcached call %r %r %r' % (key, args, kwargs))

    @classmethod
    def set(self, key, *args, **kwargs):
        assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.set(key, *args, **kwargs)
        except:
            logging.exception('failed memcached call %r %r %r' % (key, args, kwargs))

    @classmethod
    def delete(self, key, *args, **kwargs):
        assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.delete(key, *args, **kwargs)
        except:
            logging.exception('failed memcached call %r %r %r' % (key, args, kwargs))

    @classmethod
    def get(self, key, *args, **kwargs):
        assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.get(key, *args, **kwargs)
        except:
            logging.exception('failed memcached call %r %r %r' % (key, args, kwargs))

    @classmethod
    def incr(self, key, *args, **kwargs):
        assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.incr(key, *args, **kwargs)
        except pylibmc.NotFound:
            pass
        except:
            logging.exception('failed memcached call %r %r %r' % (key, args, kwargs))
    
    @classmethod
    def decr(self, key, *args, **kwargs):
        assert isinstance(key, str), "key %r must be _utf8" % key
        try:
            mc.setup()
            return mc._conn.decr(key, *args, **kwargs)
        except pylibmc.NotFound:
            pass
        except:
            logging.exception('failed memcached call %r %r %r' % (key, args, kwargs))

