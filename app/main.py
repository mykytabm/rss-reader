
from typing import final
from fastapi import Depends, FastAPI, Form, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import with_expression
from jose import JWTError, jwt
from .models import Base, User,Subscription
from .schemas import TokenData

from .database import SessionLocal, engine
from .utils.exceptions import credentials_exception

from .services.user_service import register_user, login_user
from .services.feed_service import subscribe_feed, unsubscribe_feed, list_feeds, add_feed_items

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

SECRET_KEY = "765e6d6a8fa43f75a5fdd20e31b136b1c6dc2641e2f6646a504353745285f905"
ALGORITHM = "HS256"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auth_user(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return login_user(form_data)


@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    register_user(username, password)


@app.post("/follow-rss")
async def follow_rss(feed_url: str, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return subscribe_feed(feed_url, user.id)


@app.delete("/unfollow-rss")
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


@app.post("/list-items")
async def list_feed_items(feed_url: str, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return add_feed_items(feed_url)