from __future__ import absolute_import

import re
import json
import falcon

from . import config

if config.DEBUG:
    def dumps(d):
        s = json.dumps(d, indent=2, sort_keys=True) + '\n'
        return json_escape(s)
else:
    def dumps(d):
        return json_escape(json.dumps(d))

def loads(s):
    try:
        return json.loads(s)
    except ValueError:
        raise falcon.HTTPBadRequest('Invalid JSON',
                                    'Invalid JSON provided')


ESCAPE_RE = re.compile(r'[<>/]')
def _escape_func(matchobj):
    ch = ord(matchobj.group(0))
    return '\\u%04x' % (ch,)

def json_escape(s):
    return ESCAPE_RE.sub(_escape_func, s)
