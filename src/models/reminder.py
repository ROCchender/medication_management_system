from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime

class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    medication_id = Column(Integer, ForeignKey("medications.id"))
    reminder_type = Column(String(20))  # "expiry", "usage"等
    reminder_time = Column(DateTime)
    sent = Column(Boolean, default=False)
    message = Column(String(500))
    
    user = relationship("User", back_populates="reminders")