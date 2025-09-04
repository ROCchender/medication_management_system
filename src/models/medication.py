from sqlalchemy import Column, Integer, String, Date, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime, timedelta

class Medication(Base):
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True)
    production_date = Column(Date)
    shelf_life_days = Column(Integer)  # 保存期限（天）
    expiry_date = Column(Date)  # 过期日期（系统计算）
    功效 = Column(String(500))
    usage = Column(String(500))
    image_url = Column(String(200))
    quantity = Column(Float, default=1.0)
    unit = Column(String(20), default="片")
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User", back_populates="medications")
    
    # 自动计算过期日期
    def calculate_expiry_date(self):
        if self.production_date and self.shelf_life_days:
            self.expiry_date = self.production_date + timedelta(days=self.shelf_life_days)

    # 检查是否过期
    @property
    def is_expired(self):
        if not self.expiry_date:
            return False
        return datetime.now().date() > self.expiry_date
    
    # 检查是否即将过期
    @property
    def is_near_expiry(self):
        if not self.expiry_date:
            return False
        days_until_expiry = (self.expiry_date - datetime.now().date()).days
        from config import settings
        return 0 <= days_until_expiry <= settings.EXPIRY_REMINDER_DAYS