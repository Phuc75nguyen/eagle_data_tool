import os
import datetime
import uuid
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Boolean, JSON, DateTime, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship 

load_dotenv() #dont write 4profuct

# Use SQLite for simplicity, DB file will be created in the current directory
SQLALCHEMY_DATABASE_URL = "sqlite:///eagle_data.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define Users table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    password_hash = Column(String)
    credits = Column(Float, default=100.0)

#create table instruction
Base.metadata.create_all(bind=engine)