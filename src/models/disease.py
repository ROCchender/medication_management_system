from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base

class Disease(Base):
    __tablename__ = "diseases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, unique=True)
    description = Column(Text)
    
    # 与推荐药物的关系
    recommended_medications = relationship(
        "MedicationRecommendation", back_populates="disease"
    )

class MedicationRecommendation(Base):
    __tablename__ = "medication_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"))
    medication_name = Column(String(100))  # 药物名称
    recommendation_strength = Column(Integer, default=1)  # 推荐强度（1-5）
    
    disease = relationship("Disease", back_populates="recommended_medications")