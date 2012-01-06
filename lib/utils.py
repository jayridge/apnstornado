import time
import struct
import binascii
import simplejson as json

def token_to_binary(token):
    return token.replace(' ','').decode('hex')


def create_message(token, alert=None, badge=None, sound=None, identifier=0, expiry=None, extra=None):
    token = token_to_binary(token)
    if len(token) != 32:
        raise ValueError, u"Token must be a 32-byte binary string."
    if (alert is not None) and (not isinstance(alert, (str, unicode, dict))):
        raise ValueError, u"Alert message must be a string or a dictionary."
    if expiry is None:
        expiry = long(time.time() + 365 * 86400)

    aps = { "alert" : alert }
    if badge is not None:
        aps["badge"] = badge
    if sound is not None:
        aps["sound"] = sound

    data = { "aps" : aps }
    if extra is not None:
        data.update(extra)

    encoded = json.dumps(data)
    length = len(encoded)

    return struct.pack("!bIIH32sH%(length)ds" % { "length" : length },
        1, identifier, expiry,
        32, token, length, encoded)


def parse_response(bytes):
    if len(bytes) != 6:
        raise ValueError, u"response must be a 6-byte binary string."

    command, status, identifier = struct.unpack_from('!bbI', bytes, 0)
    if command != 8:
        raise ValueError, u"response command must equal 8."

    return status, identifier, error_status_to_string(status)


def error_status_to_string(status):
    if status is 0:
        return "No errors encountered"
    elif status is 1:
        return "Processing error"
    elif status is 2:
        return "Missing device token"
    elif status is 3:
        return "Missing topic"
    elif status is 4:
        return "Missing payload"
    elif status is 5:
        return "Invalid token size"
    elif status is 6:
        return "Invalid topic size"
    elif status is 7:
        return "Invalid payload size"
    elif status is 8:
        return "Invalid token"
    elif status is 255:
        return "None (unknown)"
    else:
        return ""
