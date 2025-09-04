from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import get_db
from ..models.disease import Disease, MedicationRecommendation
from ..services.disease_service import (
    create_disease,
    get_diseases,
    get_disease,
    update_disease,
    delete_disease,
    add_medication_recommendation,
    remove_medication_recommendation
)

router = APIRouter()

# 创建疾病
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_new_disease(
    disease_data: dict,
    db: Session = Depends(get_db)
):
    # 检查必填字段
    if "name" not in disease_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: name"
        )
    
    # 创建疾病
    disease = create_disease(
        db=db,
        name=disease_data["name"],
        description=disease_data.get("description")
    )
    
    return {
        "id": disease.id,
        "name": disease.name,
        "message": "Disease created successfully"
    }

# 获取所有疾病
@router.get("/", response_model=List[dict])
def read_diseases(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    diseases = get_diseases(db, skip=skip, limit=limit)
    return [
        {
            "id": disease.id,
            "name": disease.name,
            "description": disease.description
        } for disease in diseases
    ]

# 获取单个疾病
@router.get("/{disease_id}", response_model=dict)
def read_disease(
    disease_id: int,
    db: Session = Depends(get_db)
):
    db_disease = get_disease(db, disease_id=disease_id)
    if db_disease is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease not found"
        )
    
    # 获取推荐药物
    recommendations = [
        {
            "medication_name": rec.medication_name,
            "recommendation_strength": rec.recommendation_strength
        }
        for rec in db_disease.recommended_medications
    ]
    
    return {
        "id": db_disease.id,
        "name": db_disease.name,
        "description": db_disease.description,
        "recommended_medications": recommendations
    }

# 更新疾病
@router.put("/{disease_id}", response_model=dict)
def update_existing_disease(
    disease_id: int,
    disease_data: dict,
    db: Session = Depends(get_db)
):
    db_disease = update_disease(db, disease_id=disease_id, **disease_data)
    if db_disease is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease not found"
        )
    
    return {
        "id": db_disease.id,
        "name": db_disease.name,
        "message": "Disease updated successfully"
    }

# 删除疾病
@router.delete("/{disease_id}", response_model=dict)
def delete_existing_disease(
    disease_id: int,
    db: Session = Depends(get_db)
):
    success = delete_disease(db, disease_id=disease_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease not found"
        )
    return {"message": "Disease deleted successfully"}

# 添加药物推荐
@router.post("/{disease_id}/recommendations", response_model=dict)
def add_disease_medication_recommendation(
    disease_id: int,
    recommendation_data: dict,
    db: Session = Depends(get_db)
):
    # 检查必填字段
    if "medication_name" not in recommendation_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: medication_name"
        )
    
    # 添加推荐
    recommendation = add_medication_recommendation(
        db=db,
        disease_id=disease_id,
        medication_name=recommendation_data["medication_name"],
        recommendation_strength=recommendation_data.get("recommendation_strength", 1)
    )
    
    if recommendation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disease not found"
        )
    
    return {
        "id": recommendation.id,
        "disease_id": recommendation.disease_id,
        "medication_name": recommendation.medication_name,
        "message": "Medication recommendation added successfully"
    }

# 删除药物推荐
@router.delete("/recommendations/{recommendation_id}", response_model=dict)
def remove_disease_medication_recommendation(
    recommendation_id: int,
    db: Session = Depends(get_db)
):
    success = remove_medication_recommendation(db, recommendation_id=recommendation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication recommendation not found"
        )
    return {"message": "Medication recommendation removed successfully"}