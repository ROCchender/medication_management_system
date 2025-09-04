from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from ..models.medication import Medication
from ..models.disease import Disease, MedicationRecommendation
from ..utils.medication_search import search_medication_details, get_recommended_medications_for_disease

# 创建药物
def create_medication(
    db: Session,
    name: str,
    production_date: str,
    shelf_life_days: int,
    功效: str = None,
    usage: str = None,
    image_url: str = None,
    quantity: float = 1.0,
    unit: str = "片",
    user_id: int = 1
) -> Medication:
    # 创建药物实例
    medication = Medication(
        name=name,
        production_date=production_date,
        shelf_life_days=shelf_life_days,
        功效=功效,
        usage=usage,
        image_url=image_url,
        quantity=quantity,
        unit=unit,
        user_id=user_id
    )
    
    # 计算过期日期
    medication.calculate_expiry_date()
    
    # 保存到数据库
    db.add(medication)
    db.commit()
    db.refresh(medication)
    
    return medication

# 获取所有药物
def get_medications(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    user_id: int = 1
) -> List[Medication]:
    return db.query(Medication).filter(
        Medication.user_id == user_id
    ).offset(skip).limit(limit).all()

# 获取单个药物
def get_medication(
    db: Session,
    medication_id: int,
    user_id: int = 1
) -> Optional[Medication]:
    return db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == user_id
    ).first()

# 更新药物
def update_medication(
    db: Session,
    medication_id: int,
    user_id: int = 1,
    **kwargs
) -> Optional[Medication]:
    # 查找药物
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == user_id
    ).first()
    
    if not medication:
        return None
    
    # 更新字段
    for key, value in kwargs.items():
        if hasattr(medication, key):
            setattr(medication, key, value)
    
    # 如果更新了生产日期或保存期限，重新计算过期日期
    if "production_date" in kwargs or "shelf_life_days" in kwargs:
        medication.calculate_expiry_date()
    
    db.commit()
    db.refresh(medication)
    
    return medication

# 删除药物
def delete_medication(
    db: Session,
    medication_id: int,
    user_id: int = 1
) -> bool:
    # 查找药物
    medication = db.query(Medication).filter(
        Medication.id == medication_id,
        Medication.user_id == user_id
    ).first()
    
    if not medication:
        return False
    
    # 删除药物
    db.delete(medication)
    db.commit()
    
    return True

# 搜索药物信息
def search_medication_info(medication_name: str) -> Optional[Dict[str, Any]]:
    # 调用工具函数搜索药物信息
    return search_medication_details(medication_name)

# 根据疾病获取药物推荐
def get_medications_by_disease(
    db: Session,
    disease_name: str,
    user_id: int = 1
) -> Dict[str, Any]:
    result = {
        "disease": disease_name,
        "available_medications": [],
        "recommended_medications": []
    }
    
    # 1. 获取疾病推荐的药物列表
    recommended_med_names = get_recommended_medications_for_disease(disease_name)
    
    # 2. 检查用户药物柜中是否有推荐的药物
    if recommended_med_names:
        # 查找用户药物柜中的药物
        user_medications = db.query(Medication).filter(
            Medication.user_id == user_id,
            Medication.name.in_(recommended_med_names),
            Medication.is_expired == False  # 只考虑未过期的药物
        ).all()
        
        # 添加到可用药物列表
        for med in user_medications:
            result["available_medications"].append({
                "id": med.id,
                "name": med.name,
                "功效": med.功效,
                "usage": med.usage,
                "image_url": med.image_url,
                "quantity": med.quantity,
                "unit": med.unit,
                "expiry_date": med.expiry_date.isoformat() if med.expiry_date else None
            })
        
        # 找出用户没有的推荐药物
        user_med_names = [med.name for med in user_medications]
        missing_med_names = [name for name in recommended_med_names if name not in user_med_names]
        
        # 为缺少的药物添加购买推荐
        for med_name in missing_med_names:
            # 搜索药物详细信息
            med_info = search_medication_details(med_name)
            if med_info:
                result["recommended_medications"].append({
                    "name": med_name,
                    "功效": med_info.get("功效"),
                    "用法": med_info.get("用法"),
                    "image_url": med_info.get("图片")
                })
    
    # 3. 如果没有预定义的推荐，尝试从数据库中查找
    if not recommended_med_names:
        # 查找疾病记录
        disease = db.query(Disease).filter(Disease.name == disease_name).first()
        
        if disease:
            # 获取推荐药物
            for recommendation in disease.recommended_medications:
                # 检查用户是否有该药物
                user_med = db.query(Medication).filter(
                    Medication.user_id == user_id,
                    Medication.name == recommendation.medication_name,
                    Medication.is_expired == False
                ).first()
                
                if user_med:
                    # 添加到可用药物
                    result["available_medications"].append({
                        "id": user_med.id,
                        "name": user_med.name,
                        "功效": user_med.功效,
                        "usage": user_med.usage,
                        "image_url": user_med.image_url,
                        "quantity": user_med.quantity,
                        "unit": user_med.unit,
                        "expiry_date": user_med.expiry_date.isoformat() if user_med.expiry_date else None
                    })
                else:
                    # 添加到购买推荐
                    med_info = search_medication_details(recommendation.medication_name)
                    if med_info:
                        result["recommended_medications"].append({
                            "name": recommendation.medication_name,
                            "功效": med_info.get("功效"),
                            "用法": med_info.get("用法"),
                            "image_url": med_info.get("图片"),
                            "recommendation_strength": recommendation.recommendation_strength
                        })
    
    return result

# 获取即将过期的药物
def get_near_expiry_medications(
    db: Session,
    user_id: int = 1
) -> List[Medication]:
    return db.query(Medication).filter(
        Medication.user_id == user_id,
        Medication.is_near_expiry == True
    ).all()

# 获取过期的药物
def get_expired_medications(
    db: Session,
    user_id: int = 1
) -> List[Medication]:
    return db.query(Medication).filter(
        Medication.user_id == user_id,
        Medication.is_expired == True
    ).all()