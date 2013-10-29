#!/usr/bin/env python

from __future__ import print_function

import os
import sys
import baker

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import splitbee


@baker.command
def syncdb():
    from splitbee.models import bind_db
    print("Synchronizing database...", end='')
    #bind_db(
    print(" done!")


@baker.command
def run(port=8000):
    from splitbee.app import app
    from wsgiref import simple_server

    host = '127.0.0.1'
    print("Serving HTTP on %s port %d ..." % (host, port))
    httpd = simple_server.make_server(host, port, app)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('')


if __name__ == "__main__":
    baker.run()
