#!/usr/bin/env python

from __future__ import absolute_import, print_function

import os
import sys
import datetime

import baker
import bcrypt

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import splitbee

from splitbee.models import *
from splitbee.util import gen_random
from splitbee import config


bind_db(config.get_db())



@baker.command
def syncdb():
    print("Synchronizing database...", end='')
    drop_tables()
    create_tables()
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


@baker.command
def add_test_data():
    # Add test users
    print("Adding users..."); sys.stdout.flush()
    u1 = User.create(email='foo@bar.com',
                     password=bcrypt.hashpw("hello", bcrypt.gensalt()))
    u2 = User.create(email='baz@bar.com',
                     password=bcrypt.hashpw("goodbye", bcrypt.gensalt()))

    # Add test bills
    print("Adding bills..."); sys.stdout.flush()
    b1 = Bill.create(id='WSxav972', description="breakfast at Foo")
    b2 = Bill.create(id='Dp84UxFi', description="lunch at Bar")
    b3 = Bill.create(id='nsUyGz42', description="dinner at Baz")

    # Add components of a bill
    print("Adding bill components..."); sys.stdout.flush()
    c1 = BillComponent.create(bill=b1, user=u1, amount=10.0)
    c2 = BillComponent.create(bill=b1, user=u2, amount=15.0)
    c3 = BillComponent.create(bill=b2, user=u1, amount= 1.0)
    c4 = BillComponent.create(bill=b2, user=u2, amount=11.0)
    c5 = BillComponent.create(bill=b3, user=u1, amount=25.0)
    c6 = BillComponent.create(bill=b3, user=u2, amount=18.0)


@baker.command
def get_tokens(email):
    user = User.get(User.email == email)

    print("Tokens for user '%s' (ID = %d):" % (email, user.id))
    for token in Token.select().where(Token.user == user):
        print('\t%s - created at %s (%d seconds ago)' % (
            token.id,
            token.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
            (datetime.utcnow() - token.timestamp).total_seconds(),
        ))


if __name__ == "__main__":
    baker.run()
