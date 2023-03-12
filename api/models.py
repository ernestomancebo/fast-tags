from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from api.database import Base


class User(Base):
    __tablename__ = "users"

    _id = Column(Integer, primary_key=True, index=True, name="id")
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    links = relationship('TaggedLink', back_populates="owner")


class TaggedLink(Base):
    __tablename__ = 'tagged_links'

    _id = Column(Integer, primary_key=True, index=True, name='id')
    url = Column(String, unique=True, index=True, nullable=False)
    tags = Column(ARRAY(String, dimensions=1), nullable=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship('User', back_populates='links')
