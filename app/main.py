
import os
import logging

from fastapi import Depends, FastAPI, Form, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from starlette.status import HTTP_200_OK
from jose import JWTError, jwt
from models import Base, User
from schemas import TokenData

from database import SessionLocal, engine

from utils.exceptions import credentials_exception
from utils.secret_key import secret_key

from services.user_service import register_user, login_user
from services.feed_service import subscribe_feed, unsubscribe_feed, get_user_feeds, get_feed_items, update_feed, get_filtered_items, mark_item

from worker.celery_app import celery_app

log = logging.getLogger(__name__)

# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ALGORITHM = "HS256"


def celery_on_message(body):
    log.warn(body)

def background_on_message(task):
    log.warn(task.get(on_message=celery_on_message, propagate=False))


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

# @app.get("/update-feeds")
# async def update_feeds(background_task: BackgroundTasks):
#     # task_name=None
#     #  # set correct task name based on the way you run the example
#     # if not bool(os.getenv('DOCKER')):
#     #     task_name = "app.worker.celery_worker.update_feeds_items"
#     # else:
#     #     task_name = "app.app.worker.celery_worker.update_feeds_items"

#     # task = celery_app.send_task(task_name)
#     # print(task)
#     # background_task.add_task(background_on_message, task)
#     # return {"message": "running update feeds items"}


@app.get("/{word}")
async def root(word: str, background_task: BackgroundTasks):
    task_name = None

    # set correct task name based on the way you run the example
    if not bool(os.getenv('DOCKER')):
        task_name = "app.worker.celery_worker.test_celery"
    else:
        task_name = "app.worker.celery_worker.test_celery"

    task = celery_app.send_task(task_name, args=[word])
    print(task)
    background_task.add_task(background_on_message, task)

    return {"message": "Word received"}


@app.post("/register", status_code=HTTP_200_OK)
def register(username: str = Form(...), password: str = Form(...)):
    register_user(username, password)

@app.post("/follow-rss", status_code=HTTP_200_OK)
def follow_rss(feed_url: str,  token: str = Depends(oauth2_scheme)):
    
    # # set correct task name based on the way you run the example
    # if not bool(os.getenv('DOCKER')):
    #     task_name = "app.worker.celery_worker.test_celery"
    # else:
    #     task_name = "app.app.worker.celery_worker.test_celery"

    # task = celery.send_task(task_name, args=['test celery'])
    # print(task)
    # background_task.add_task(background_on_message, task)
    
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return subscribe_feed(feed_url, user.id)


@app.delete("/unfollow-rss", status_code=HTTP_200_OK)
def unfollow_rss(feed_url: str, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return unsubscribe_feed(feed_url, user.id)


@app.get("/list-feeds",status_code=HTTP_200_OK)
def list_feeds(start: int, end: int, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return get_user_feeds(user.id, start, end)


@app.get("/get-items",status_code=HTTP_200_OK)
def list_feed_items(feed_url: str, start: int, end: int, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return get_feed_items(feed_url, start, end)
    
    
@app.post("/mark-item",status_code=HTTP_200_OK)
def mark_item_read(item_link: str, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return mark_item(item_link, user.id)



@app.get('/get-filtered-items',status_code=HTTP_200_OK)
def list_filtered_feed_items(feed_url: str, read: bool, start: int, end: int, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return get_filtered_items(feed_url, read, user.id, start, end)


@app.get("/update-feed", status_code=HTTP_200_OK)
def update_feed(feed_url: str, token: str = Depends(oauth2_scheme)):
    user = auth_user(token)
    if not user:
        raise credentials_exception
    else:
        return update_feed(feed_url)
