import datetime
from typing import List, Optional
from pydantic import BaseModel, json
from sqlalchemy.sql.sqltypes import JSON


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
    feed_url: str


class SubscriptionCreate(SubscriptionBase):
    subscribed_id: int


class Subscription(BaseModel):
    id: int

    class Config:
        orm_mode = True


# ------feed item
class FeedItem(BaseModel):
    id: int
    subscription_id: int
    feed_obj: JSON
    created_date: str
    read: bool

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

# ------ jwt token


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
