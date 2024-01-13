import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

POSTGRES_USER: str = os.environ.get("POSTGRES_USER")  
POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD")  
POSTGRES_HOST: str = os.environ.get("POSTGRES_HOST")
POSTGRES_DB: str = os.environ.get("POSTGRES_DB")  
DEBUG: bool = True if os.environ.get("DEBUG") == "True" else False


SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()