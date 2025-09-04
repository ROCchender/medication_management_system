from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 数据库路径
SQLALCHEMY_DATABASE_URL = "sqlite:///./medication.db"

# 创建引擎
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建会话本地类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()