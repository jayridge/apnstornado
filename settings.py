import tornado.options

tornado.options.define("environment", default="dev", help="environment")

options = {
    'dev' : {
        'certfile' : 'apns_development.pem',
        'apns_host' : ( 'gateway.sandbox.push.apple.com', 2195 ),
        'feedback_host' : ( 'feedback.sandbox.push.apple.com', 2196 ),
        'memcached' : ['127.0.0.1:11211'],
        'apns_reconnect_lag' : 5,
        'feedback_enabled' : False,
        'feedback_reconnect_lag' : 60
    }, 
    'prod' : {
        'certfile' : 'apns_production.pem',
        'apns_host' : ( 'gateway.push.apple.com', 2195 ),
        'feedback_host' : ( 'feedback.push.apple.com', 2196 ),
        'memcached' : ['127.0.0.1:11211'],
        'apns_reconnect_lag' : 1,
        'feedback_enabled' : False,
        'feedback_reconnect_lag' : 60
    }
}

default_options = {
}

def env():
    return tornado.options.options.environment

def get(key):
    env = tornado.options.options.environment 
    if env not in options: 
        raise Exception("Invalid Environment (%s)" % env) 
    v = options.get(env).get(key) or default_options.get(key)
    if callable(v):
        return v()
    return v

