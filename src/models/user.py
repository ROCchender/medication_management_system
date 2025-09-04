from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    phone_number = Column(String(20), nullable=True)
    wechat_openid = Column(String(100), nullable=True)
    phone_verified = Column(Boolean, default=False)
    wechat_verified = Column(Boolean, default=False)
    
    # 与药物的关系
    medications = relationship("Medication", back_populates="user")
    # 与提醒的关系
    reminders = relationship("Reminder", back_populates="user")