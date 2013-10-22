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
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import types

from .config import DEBUG

Base = declarative_base()
engine = create_engine('sqlite:///test.db')
create_session = sessionmaker(bind=engine)


class StringCurrency(types.TypeDecorator):
    precision = Decimal('0.01')
    impl = types.String

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.VARCHAR(100))

    def process_bind_param(self, value, dialect):
        return str(value.quantize(self.precision))

    def process_result_value(self, value, dialect):
        return Decimal(value)


class BillPayer(Base):
    __tablename__ = 'bill_payers'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    bill_id = Column(Integer, ForeignKey('bills.id'), primary_key=True)

    amount_paid = 


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    # TODO: persona auth

    bills_paid = relationship('Bill', backref='payer')
    bills_split = relationship('Bill',
                               secondary=bill_user_assoc_table,
                               backref='members')

    def __repr__(self):
        return "<User(%d, '%s')>" % (self.id, self.name)


class Bill(Base):
    """
    A single bill, representing some amount of money that was paid and needs
    to be split among multiple people.
    """
    __tablename__ = 'bills'

    id = Column(Integer, primary_key=True)
    description = Column(String(140))

    # Total amount of the bill
    total_amount = Column(StringCurrency, nullable=False)

    # ID of the payer
    payer_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    def __repr__(self):
        return "<Bill(id=%d, total_amount='%s')>" % (self.id,
                                                     self.total_amount)
