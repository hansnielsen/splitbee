import string
import random
from decimal import Decimal
from datetime import datetime

import peewee
from peewee import *
from playhouse.proxy import Proxy

from .config import DEBUG
from .util import gen_random


database_proxy = Proxy()


class SplitbeeModel(Model):
    class Meta:
        database = database_proxy


class User(SplitbeeModel):
    id = PrimaryKeyField()
    email = CharField(null=False)
    password = CharField(null=False)

    # Optional name
    name = CharField(null=True)

    @property
    def total_owing(self):
        """
        Total amount this user owes - i.e. the amount they would have paid
        if all bills were split perfectly and they paid for their entire share.
        """
        # TODO: this should use sql, not sum here
        return sum(x.amount for x in self.paid_components)

    @property
    def total_paid(self):
        """
        Total amount this user has actually paid for.
        """
        # TODO: this should use sql, not sum here
        return 0


class Token(SplitbeeModel):
    """
    This class represents tokens that can be used to authenticate as a user.
    Each token will be valid for a certain period of time after the issuing
    date, which is stored in the token.
    """
    id = CharField(primary_key=True)
    user = ForeignKeyField(User, related_name='tokens')
    timestamp = DateTimeField(null=False)


class Bill(SplitbeeModel):
    """
    A single bill, representing some amount of money that was paid and needs
    to be split among multiple people.
    """
    # NOTE: This ID can't be an integer, since it will be displayed to end-
    # users and used to look up bills.  We make it a random string do
    # dissuade brute-forcing.
    id = CharField(max_length=8, primary_key=True)
    description = CharField(max_length=140, null=False)
    payer = ForeignKeyField(User, null=True, related_name='bills_paid')

    @property
    def is_paid(self):
        return self.payer is not None


class BillComponent(SplitbeeModel):
    """
    A component of a bill that is owned by a certain user.
    """
    user = ForeignKeyField(User)
    bill = ForeignKeyField(Bill)
    amount = DecimalField(decimal_places=2, null=False)

    # TODO: make user/bill primary keys


ALL_MODELS = (User, Token, Bill, BillComponent)


def bind_db(db):
    database_proxy.initialize(db)
    return database_proxy

def create_tables():
    peewee.create_model_tables(ALL_MODELS)

def drop_tables():
    peewee.drop_model_tables(ALL_MODELS)
