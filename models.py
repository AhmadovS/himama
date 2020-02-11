from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from flask_login import UserMixin

engine = create_engine('sqlite:///database.db', echo=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


class User(UserMixin, Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    email = Column(String(120), unique=True)
    password = Column(String(30))

    def __init__(self, email=None, name=None, password=None):
        self.name = name
        self.password = password
        self.email = email

class Tracker(Base):
    __tablename__ = 'tracker'
    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    # duration = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id'),
        nullable=False)

    def __init__(self,user_id, start_time=None):
        self.user_id = user_id
        self.start_time = start_time

# Create tables.
Base.metadata.create_all(bind=engine)
