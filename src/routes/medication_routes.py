from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ..database import get_db
from ..models.medication import Medication
from ..services.medication_service import (
    create_medication,
    get_medications,
    get_medication,
    update_medication,
    delete_medication,
    search_medication_info,
    get_medications_by_disease
)
from ..utils.medication_search import search_medication_details

router = APIRouter()

# 创建药物
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_new_medication(
    medication_data: dict,
    db: Session = Depends(get_db),
    user_id: int = 1  # 这里简化处理，实际应该从认证中获取用户ID
):
    # 检查必填字段
    required_fields = ["name", "production_date", "shelf_life_days"]
    for field in required_fields:
        if field not in medication_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    # 解析日期
    try:
        production_date = datetime.strptime(
            medication_data["production_date"], "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid production_date format. Use YYYY-MM-DD."
        )
    
    # 搜索药物信息
    medication_info = search_medication_details(medication_data["name"])
    if medication_info:
        medication_data.update({
            "功效": medication_info.get("功效"),
            "usage": medication_info.get("用法"),
            "image_url": medication_info.get("图片")
        })
    
    # 创建药物
    medication = create_medication(
        db=db,
        name=medication_data["name"],
        production_date=production_date,
        shelf_life_days=medication_data["shelf_life_days"],
        功效=medication_data.get("功效"),
        usage=medication_data.get("用法"),
        image_url=medication_data.get("image_url"),
        quantity=medication_data.get("quantity", 1.0),
        unit=medication_data.get("unit", "片"),
        user_id=user_id
    )
    
    return {
        "id": medication.id,
        "name": medication.name,
        "expiry_date": medication.expiry_date.isoformat() if medication.expiry_date else None,
        "message": "Medication created successfully"
    }

# 获取所有药物
@router.get("/", response_model=List[dict])
def read_medications(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: int = 1  # 简化处理
):
    medications = get_medications(db, skip=skip, limit=limit, user_id=user_id)
    return [
        {
            "id": med.id,
            "name": med.name,
            "production_date": med.production_date.isoformat() if med.production_date else None,
            "shelf_life_days": med.shelf_life_days,
            "expiry_date": med.expiry_date.isoformat() if med.expiry_date else None,
            "功效": med.功效,
            "usage": med.usage,
            "image_url": med.image_url,
            "quantity": med.quantity,
            "unit": med.unit,
            "is_expired": med.is_expired,
            "is_near_expiry": med.is_near_expiry
        } for med in medications
    ]

# 获取单个药物
@router.get("/{medication_id}", response_model=dict)
def read_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # 简化处理
):
    db_medication = get_medication(db, medication_id=medication_id, user_id=user_id)
    if db_medication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    return {
        "id": db_medication.id,
        "name": db_medication.name,
        "production_date": db_medication.production_date.isoformat() if db_medication.production_date else None,
        "shelf_life_days": db_medication.shelf_life_days,
        "expiry_date": db_medication.expiry_date.isoformat() if db_medication.expiry_date else None,
        "功效": db_medication.功效,
        "usage": db_medication.usage,
        "image_url": db_medication.image_url,
        "quantity": db_medication.quantity,
        "unit": db_medication.unit,
        "is_expired": db_medication.is_expired,
        "is_near_expiry": db_medication.is_near_expiry
    }

# 更新药物
@router.put("/{medication_id}", response_model=dict)
def update_existing_medication(
    medication_id: int,
    medication_data: dict,
    db: Session = Depends(get_db),
    user_id: int = 1  # 简化处理
):
    # 解析日期
    if "production_date" in medication_data:
        try:
            medication_data["production_date"] = datetime.strptime(
                medication_data["production_date"], "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid production_date format. Use YYYY-MM-DD."
            )
    
    db_medication = update_medication(db, medication_id=medication_id, 
                                     user_id=user_id, **medication_data)
    if db_medication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    
    return {
        "id": db_medication.id,
        "name": db_medication.name,
        "message": "Medication updated successfully"
    }

# 删除药物
@router.delete("/{medication_id}", response_model=dict)
def delete_existing_medication(
    medication_id: int,
    db: Session = Depends(get_db),
    user_id: int = 1  # 简化处理
):
    success = delete_medication(db, medication_id=medication_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found"
        )
    return {"message": "Medication deleted successfully"}

# 搜索药物信息
@router.get("/search/{medication_name}", response_model=dict)
def search_medication(medication_name: str):
    result = search_medication_details(medication_name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No information found for medication: {medication_name}"
        )
    return result

# 根据疾病获取药物推荐
@router.get("/disease/{disease_name}", response_model=dict)
def get_medications_for_disease(
    disease_name: str,
    db: Session = Depends(get_db),
    user_id: int = 1  # 简化处理
):
    result = get_medications_by_disease(db, disease_name, user_id)
    return result