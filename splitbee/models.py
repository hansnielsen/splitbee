import string
import random
from decimal import Decimal

from sqlalchemy import (
    create_engine,
    Column,
    ForeignKey,
    Integer,
    Sequence,
    String,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import types

from .config import DEBUG

Base = declarative_base()
Session = sessionmaker()


# The default alphabet is all letters and digits, but with some confusing
# duplicate-looking letters removed (see below for the whole list).
ID_TRANSLATION = ''.join([chr(x) for x in range(256)])
DEFAULT_ALPHABET = (string.ascii_letters + string.digits).translate(
    ID_TRANSLATION,
    'oO0Il1'
)
def gen_random(length, alphabet=DEFAULT_ALPHABET):
    return ''.join(random.choice(alphabet) for x in range(length))


class StringCurrency(types.TypeDecorator):
    precision = Decimal('0.01')
    impl = types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))

    def process_bind_param(self, value, dialect):
        if isinstance(value, float):
            value = Decimal(value)

        return str(value.quantize(self.precision))

    def process_result_value(self, value, dialect):
        return Decimal(value)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String)
    # auth

    # Optional name
    name = Column(String, nullable=True)

    def __init__(self, email, password, name=None):
        self.email = email
        #self.password = password
        self.name = name

    @property
    def total_owing(self):
        """
        Total amount this user owes - i.e. the amount they would have paid
        if all bills were split perfectly and they paid for their entire share.
        """
        # TODO: this should use sql, not sum here
        return sum(x.amount_paid for x in self.paid_components)

    @property
    def total_paid(self):
        """
        Total amount this user has actually paid for.
        """
        # TODO: this should use sql, not sum here
        return 0

    def __repr__(self):
        return "<User(%d, '%s')>" % (self.id, self.name)


class Bill(Base):
    """
    A single bill, representing some amount of money that was paid and needs
    to be split among multiple people.
    """
    __tablename__ = 'bills'

    # NOTE: This ID can't be an integer, since it will be displayed to end-
    # users and used to look up bills.  We make it a random string do
    # dissuade brute-forcing.
    id = Column(String(8), primary_key=True)
    description = Column(String(140), nullable=False)

    # ID of the payer.  NULL means "not yet paid"
    payer_id = Column(Integer, ForeignKey('users.id'))

    def __init__(self, description=""):
        self.id = gen_random(8)
        self.description = description

    @property
    def is_paid(self):
        return self.payer_id is not None

    @property
    def total_amount(self):
        # TODO: this should use sql, not sum here
        return sum(x.amount_paid for x in self.bill_components)

    def __repr__(self):
        return "<Bill(id=%d, total_amount='%s')>" % (self.id,
                                                     self.total_amount)


class BillComponent(Base):
    """
    A component of a bill that is owned by a certain user.
    """
    __tablename__ = 'bill_components'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    bill_id = Column(Integer, ForeignKey('bills.id'), primary_key=True)

    amount_paid = Column(StringCurrency, nullable=False)

    # Bidirectional relationship to User
    payer = relationship(User,
                backref=backref("paid_components",
                                cascade="all, delete-orphan")
                )

    # Reference to bill
    bill = relationship(Bill, backref=backref("bill_components",
                                              cascade="all, delete-orphan"))

    def __init__(self, bill, payer, amount):
        self.bill = bill
        self.payer = payer
        self.amount_paid = amount


def bind_db(conn_str, create=False):
    engine = create_engine(conn_str)
    Session.configure(bind=engine)
    if create:
        Base.metadata.create_all(engine)

    return engine
