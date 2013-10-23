#!/usr/bin/env python2

from __future__ import print_function
import sys

from splitbee.models import *

conn_str = 'sqlite:///:memory:'
engine = bind_db(conn_str, create=True)
db = Session()

# Add test users
print("Adding users...")
u1 = User("foo@bar.com", "hello")
u2 = User("baz@bar.com", "goodbye")
db.add_all([u1, u2]); db.commit()

# Add test bills
print("Adding bills...")
b1 = Bill("breakfast at Foo")
b2 = Bill("lunch at Bar")
b3 = Bill("dinner at Baz")
db.add_all([b1, b2, b3]); db.commit()

# Add components of a bill
print("Adding bill components...")
c1 = BillComponent(b1, u1, 10.0)
c2 = BillComponent(b1, u2, 15.0)
c3 = BillComponent(b2, u1,  1.0)
c4 = BillComponent(b2, u2, 11.0)
c5 = BillComponent(b3, u1, 25.0)
c6 = BillComponent(b3, u2, 18.0)
db.add_all([c1, c2, c3, c4, c5]); db.commit()


#print("Total amount for bill 1: ", end=''); sys.stdout.flush()
#print(b1.total_amount)

#print("User 1 is owing: ", end=''); sys.stdout.flush()
#print(u1.total_owing)
