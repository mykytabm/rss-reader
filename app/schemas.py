import datetime
from typing import List, Optional
from pydantic import BaseModel


# ------user
class UserBase(BaseModel):
    name: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True


# ------subscription
class SubscriptionBase(BaseModel):
    title: str


class SubscriptionCreate(SubscriptionBase):
    pass


class Subscription(SubscriptionBase):
    id: str
    subscribed_id: int
    feed_url: str

    class Config:
        orm_mode = True


# feeditem
class FeedItem(BaseModel):
    subscription_id: int
    created_date: str
    read: bool

    class Config:
        orm_mode = True
