from datetime import timedelta, datetime
from typing import Optional
from database import SessionLocal
from models import User
from jose import JWTError, jwt
from fastapi import status
from fastapi.exceptions import HTTPException
from passlib.context import CryptContext


SECRET_KEY = "765e6d6a8fa43f75a5fdd20e31b136b1c6dc2641e2f6646a504353745285f905"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
# if "SECRET_KEY" in os.environ:
#     return os.environ["SECRET_KEY"]

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(username: str, password: str):
    with SessionLocal() as session:
        user = session.query(User).filter(
            User.name == username).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def register_user(username, password):
    user = User(name=username, password=password)
    user.password = get_password_hash(password)
    with SessionLocal() as session:
        if session.query(User).filter(User.name == username).first():
            raise HTTPException(
                status_code=400, detail="This username is already in use")
        else:
            session.add(user)
            session.commit()


def login_user(form_data):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user:
        access_token_expires = timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.name}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
