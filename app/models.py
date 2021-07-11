import datetime
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, JSON
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(32), unique=True, index=True)
    password = Column(String(100))
    # list of item urls


class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    subscribed_id = Column(Integer, ForeignKey("users.id"))
    feed_url = Column(String(200))


class FeedItem(Base):
    __tablename__ = "feed items"
    id = Column(Integer, primary_key=True, index=True)
    feed_url = Column(String(200))
    title = Column(String(100))
    link = Column(String(200))
    publication_date = Column(DateTime)
