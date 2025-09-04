from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..models.disease import Disease, MedicationRecommendation

# 创建疾病
def create_disease(
    db: Session,
    name: str,
    description: str = None
) -> Disease:
    disease = Disease(
        name=name,
        description=description
    )
    
    db.add(disease)
    db.commit()
    db.refresh(disease)
    
    return disease

# 获取所有疾病
def get_diseases(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Disease]:
    return db.query(Disease).offset(skip).limit(limit).all()

# 获取单个疾病
def get_disease(
    db: Session,
    disease_id: int
) -> Optional[Disease]:
    return db.query(Disease).filter(Disease.id == disease_id).first()

# 根据名称获取疾病
def get_disease_by_name(
    db: Session,
    name: str
) -> Optional[Disease]:
    return db.query(Disease).filter(Disease.name == name).first()

# 更新疾病
def update_disease(
    db: Session,
    disease_id: int,
    **kwargs
) -> Optional[Disease]:
    disease = db.query(Disease).filter(Disease.id == disease_id).first()
    
    if not disease:
        return None
    
    for key, value in kwargs.items():
        if hasattr(disease, key):
            setattr(disease, key, value)
    
    db.commit()
    db.refresh(disease)
    
    return disease

# 删除疾病
def delete_disease(
    db: Session,
    disease_id: int
) -> bool:
    disease = db.query(Disease).filter(Disease.id == disease_id).first()
    
    if not disease:
        return False
    
    db.delete(disease)
    db.commit()
    
    return True

# 添加疾病-药物推荐
def add_medication_recommendation(
    db: Session,
    disease_id: int,
    medication_name: str,
    recommendation_strength: int = 1
) -> Optional[MedicationRecommendation]:
    # 检查疾病是否存在
    disease = db.query(Disease).filter(Disease.id == disease_id).first()
    
    if not disease:
        return None
    
    # 检查推荐是否已存在
    existing_recommendation = db.query(MedicationRecommendation).filter(
        MedicationRecommendation.disease_id == disease_id,
        MedicationRecommendation.medication_name == medication_name
    ).first()
    
    if existing_recommendation:
        # 更新现有推荐的强度
        existing_recommendation.recommendation_strength = recommendation_strength
        db.commit()
        db.refresh(existing_recommendation)
        return existing_recommendation
    
    # 创建新的推荐
    recommendation = MedicationRecommendation(
        disease_id=disease_id,
        medication_name=medication_name,
        recommendation_strength=recommendation_strength
    )
    
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    
    return recommendation

# 删除疾病-药物推荐
def remove_medication_recommendation(
    db: Session,
    disease_id: int,
    medication_name: str
) -> bool:
    recommendation = db.query(MedicationRecommendation).filter(
        MedicationRecommendation.disease_id == disease_id,
        MedicationRecommendation.medication_name == medication_name
    ).first()
    
    if not recommendation:
        return False
    
    db.delete(recommendation)
    db.commit()
    
    return True

# 获取疾病的所有药物推荐
def get_disease_recommendations(
    db: Session,
    disease_id: int
) -> List[MedicationRecommendation]:
    return db.query(MedicationRecommendation).filter(
        MedicationRecommendation.disease_id == disease_id
    ).order_by(MedicationRecommendation.recommendation_strength.desc()).all()

# 获取药物的所有疾病推荐
def get_medication_recommendations(
    db: Session,
    medication_name: str
) -> List[MedicationRecommendation]:
    return db.query(MedicationRecommendation).filter(
        MedicationRecommendation.medication_name == medication_name
    ).all()

# 搜索疾病
def search_diseases(
    db: Session,
    search_term: str
) -> List[Disease]:
    # 简单的名称包含搜索
    return db.query(Disease).filter(
        Disease.name.ilike(f"%{search_term}%")
    ).all()

# 批量创建疾病及推荐
def batch_create_diseases_and_recommendations(
    db: Session,
    diseases_data: List[Dict[str, Any]]
) -> Dict[str, Any]:
    results = {
        "created_diseases": 0,
        "created_recommendations": 0,
        "errors": []
    }
    
    for disease_data in diseases_data:
        try:
            # 创建疾病
            disease = create_disease(
                db=db,
                name=disease_data["name"],
                description=disease_data.get("description")
            )
            results["created_diseases"] += 1
            
            # 创建推荐
            if "recommendations" in disease_data:
                for rec in disease_data["recommendations"]:
                    recommendation = add_medication_recommendation(
                        db=db,
                        disease_id=disease.id,
                        medication_name=rec["medication_name"],
                        recommendation_strength=rec.get("recommendation_strength", 1)
                    )
                    if recommendation:
                        results["created_recommendations"] += 1
        except Exception as e:
            results["errors"].append({
                "disease": disease_data.get("name"),
                "error": str(e)
            })
    
    return results