
from typing import final
from fastapi import Depends, FastAPI, Form, status
import fastapi
import os
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import with_expression
from starlette.status import HTTP_204_NO_CONTENT
from jose import JWTError, jwt
from models import Base, User, Subscription
from schemas import TokenData

from database import SessionLocal, engine
from utils.exceptions import credentials_exception
from utils.secret_key import secret_key
from services.user_service import register_user, login_user
from services.feed_service import subscribe_feed, unsubscribe_feed, list_feeds, get_feed_items, update_feed, get_filtered_items

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


ALGORITHM = "HS256"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auth_user(token: str):
    try:
        payload = jwt.decode(token, secret_key(), algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return False
        token_data = TokenData(username=username)
    except JWTError:
        return False
    with SessionLocal() as session:
        user = session.query(User).filter(
            User.name == token_data.username).first()
    if not user:
        return False
    return user


@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)


@app.get("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return login_user(form_data)


@app.post("/register", status_code=HTTP_204_NO_CONTENT)
async def register(username: str = Form(...), password: str = Form(...)):
    register_user(username, password)


@app.post("/follow-rss", status_code=HTTP_204_NO_CONTENT)
async def follow_rss(feed_url: str, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return subscribe_feed(feed_url, user.id)


@app.delete("/unfollow-rss", status_code=HTTP_204_NO_CONTENT)
async def unfollow_rss(feed_url: str, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return unsubscribe_feed(feed_url, user.id)


@app.get("/list-feeds")
async def list_feeds(token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return list_feeds(user.id)


@app.get("/get-items")
async def list_feed_items(feed_url: str, start: int, end: int, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return get_feed_items(feed_url, start, end)


@app.get('/get-filtered-items')
async def list_filtered_feed_items(feed_url: str, read: bool, start: int, end: int, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return get_filtered_items(feed_url, read, user.id, start, end)


@app.get("/update-feed", status_code=HTTP_204_NO_CONTENT)
async def update_feed(feed_url: str, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return update_feed(feed_url)
