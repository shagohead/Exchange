from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager


engine = create_engine("postgresql+psycopg2://user_8:888@localhost/exchange")

Session = sessionmaker(bind=engine)
Base = declarative_base()


@contextmanager
def connect():
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    password = Column(String)
    account_number = Column(String)
    balance = Column(Integer)
    currency = Column(String)

    def __init__(self, email, password, account_number, balance, currency):
        self.email = email
        self.password = password
        self.account_number = account_number
        self.balance = balance
        self.currency = currency

    def __repr__(self):
        return "<User('%s', '%s', '%s', '%s', '%s')>" % (self.email,
                                                         self.password,
                                                         self.account_number,
                                                         self.balance,
                                                         self.currency)


class Transactions(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    date_time = Column(String)
    senders_account = Column(String)
    receivers_account = Column(String)
    amount = Column(String)
    currency = Column(String)

    def __init__(self, date_time, senders_account,
                 receivers_account, amount, currency):
        self.date_time = date_time
        self.senders_account = senders_account
        self.receivers_account = receivers_account
        self.amount = amount
        self.currency = currency

    def __repr__(self):
        return """<Transactions
        ('%s', '%s', '%s', '%s', '%s')>""" % (self.date_time,
                                              self.senders_account,
                                              self.receivers_account,
                                              self.amount,
                                              self.currency)


class Currency(Base):
    __tablename__ = 'currencies'
    name = Column(String, primary_key=True)
    short_name = Column(String)
    multiplicity = Column(Integer)
    course = Column(Integer)

    def __init__(self, name, short_name, multiplicity, course):
        self.name = name
        self.short_name = short_name
        self.multiplicity = multiplicity
        self.course = course

    def __repr__(self):
        return "<Currency('%s', '%s', '%s', '%s')>" % (self.name,
                                                       self.short_name,
                                                       self.multiplicity,
                                                       self.course)


Base.metadata.create_all(engine)