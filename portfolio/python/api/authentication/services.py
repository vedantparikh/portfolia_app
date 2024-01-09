import logging
from click import UUID
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from passlib import hash

from authentication.database import Base, engine, SessionLocal
from authentication.models import User
from authentication.schemas import UserCreate, User as UserSchema

JWT_SECRET = 'myjwtsecret'

oauth2chema = OAuth2PasswordBearer(tokenUrl='/api/auth/token')


def create_database():
    return Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_user_by_email(email: str, db: Session):
    return db.query(User).filter(User.email == email).first()


async def create_user(user: UserCreate, db: Session):
    user_obj = User(email=user.email, password=hash.bcrypt.hash(user.password))
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj

async def authenticate_user(email:str, password:str, db:Session):
    user = await get_user_by_email(email=email, db=db)
    if not user or not user.verify_password(password=password):
        return False
    return user

async def create_token(user: User):
    user_obj = UserSchema.model_validate(user)
    token = jwt.encode(dict(id=f'{user_obj.id}', email=user_obj.email, password=user_obj.password), JWT_SECRET)
    return dict(token=token)


async def get_current_user(token: str, db: Session):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = db.query(User).get(UUID(payload['id']))
    except:
        raise HTTPException(status_code=401, detail='Invalid email or password.')
    return UserSchema.model_validate(user)