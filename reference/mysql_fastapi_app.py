# Reference only (Interns/mysql). The same SQLAlchemy code we use with SQLite on Day 2, pointed at MySQL.
from urllib.parse import quote_plus

import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
import os


class config:   # was a config.py with real credentials — read them from the environment instead
    username = os.environ.get("DB_USER", "root")
    password = os.environ.get("DB_PASSWORD", "")
    dbhost = os.environ.get("DB_HOST", "localhost")
    dbname = os.environ.get("DB_NAME", "energy")

# =========================
# DB CONFIG
# =========================
username = config.username
password = config.password
encoded_password = quote_plus(password)
dbhost = config.dbhost
dbname = config.dbname

DATABASE_URL = f"mysql+pymysql://{username}:{encoded_password}@{dbhost}/{dbname}"

engine = create_engine(DATABASE_URL)

# =========================
# BASE MODEL
# =========================
Base = declarative_base()

# =========================
# USERS TABLE
# =========================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    firstname = Column(String(100))
    lastname = Column(String(100))
    age = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create table
Base.metadata.create_all(bind=engine)

# =========================
# DB SESSION
# =========================
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# PYDANTIC SCHEMAS
# =========================
class UserCreate(BaseModel):
    username: str
    firstname: Optional[str]
    lastname: Optional[str]
    age: Optional[int]


class UserUpdate(BaseModel):
    firstname: Optional[str]
    lastname: Optional[str]
    age: Optional[int]


class UserResponse(BaseModel):
    id: int
    username: str
    firstname: Optional[str]
    lastname: Optional[str]
    age: Optional[int]

    class Config:
        orm_mode = True

# =========================
# FASTAPI INIT
# =========================
app = FastAPI(title="User CRUD API")

# =========================
# CRUD APIs
# =========================

# 1. CREATE USER
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    db_user = User(**user.dict())

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# 2. GET ALL USERS
@app.get("/users/", response_model=List[UserResponse])
def get_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()


# 3. GET USER BY ID
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# 4. UPDATE USER
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


# 5. DELETE USER
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}

# ----------------------
if __name__ == "__main__":
    uvicorn.run("dbsers:app", host="127.0.0.1", port=8000, reload=True)