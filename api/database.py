from os import environ

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configuration
SQLALCHEMY_DATABASE_URL = environ.get('SQLALCHEMY_DATABASE_URI')
SQLALCHEMY_POOL_SIZE = environ.get('SQLALCHEMY_POOL_SIZE')

engine = create_engine(SQLALCHEMY_DATABASE_URL,
                       pool_size=int(SQLALCHEMY_POOL_SIZE))

session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
