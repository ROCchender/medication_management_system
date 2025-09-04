from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

from ..database import get_db
from ..models.reminder import Reminder
from ..services.reminder_service import create_reminder, get_reminders, get_reminder, update_reminder, delete_reminder

router = APIRouter()

# 创建提醒
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_new_reminder(
    reminder_data: dict,
    db: Session = Depends(get_db)
):
    # 检查必填字段
    required_fields = ["user_id", "medication_id", "reminder_type", "reminder_time"]
    for field in required_fields:
        if field not in reminder_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required field: {field}"
            )
    
    # 解析日期时间
    try:
        reminder_time = datetime.fromisoformat(reminder_data["reminder_time"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reminder_time format. Use ISO format."
        )
    
    # 创建提醒
    # 这里调用服务层的方法，但为了简化，我们直接在路由层实现基本逻辑
    # 实际应用中应该调用reminder_service的方法
    from models.medication import Medication
    
    # 检查药物是否存在
    medication = db.query(Medication).filter(
        Medication.id == reminder_data["medication_id"],
        Medication.user_id == reminder_data["user_id"]
    ).first()
    
    if not medication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Medication not found for this user"
        )
    
    # 创建提醒消息
    if reminder_data["reminder_type"] == "expiry":
        days_until_expiry = (medication.expiry_date - datetime.now().date()).days
        message = f"您的药物 '{medication.name}' 将在 {days_until_expiry} 天后过期，请及时处理。"
    else:
        message = reminder_data.get("message", "您有一个药物提醒")
    
    # 创建提醒记录
    reminder = Reminder(
        user_id=reminder_data["user_id"],
        medication_id=reminder_data["medication_id"],
        reminder_type=reminder_data["reminder_type"],
        reminder_time=reminder_time,
        message=message,
        sent=reminder_data.get("sent", False)
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    return {
        "id": reminder.id,
        "user_id": reminder.user_id,
        "medication_id": reminder.medication_id,
        "message": "Reminder created successfully"
    }

# 获取用户的所有提醒
@router.get("/user/{user_id}", response_model=List[dict])
def read_user_reminders(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    reminders = db.query(Reminder).filter(
        Reminder.user_id == user_id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": reminder.id,
            "user_id": reminder.user_id,
            "medication_id": reminder.medication_id,
            "reminder_type": reminder.reminder_type,
            "reminder_time": reminder.reminder_time.isoformat() if reminder.reminder_time else None,
            "sent": reminder.sent,
            "message": reminder.message
        } for reminder in reminders
    ]

# 获取单个提醒
@router.get("/{reminder_id}", response_model=dict)
def read_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if db_reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    return {
        "id": db_reminder.id,
        "user_id": db_reminder.user_id,
        "medication_id": db_reminder.medication_id,
        "reminder_type": db_reminder.reminder_type,
        "reminder_time": db_reminder.reminder_time.isoformat() if db_reminder.reminder_time else None,
        "sent": db_reminder.sent,
        "message": db_reminder.message
    }

# 更新提醒
@router.put("/{reminder_id}", response_model=dict)
def update_existing_reminder(
    reminder_id: int,
    reminder_data: dict,
    db: Session = Depends(get_db)
):
    # 检查提醒是否存在
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if db_reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    # 更新字段
    if "reminder_type" in reminder_data:
        db_reminder.reminder_type = reminder_data["reminder_type"]
    if "reminder_time" in reminder_data:
        try:
            db_reminder.reminder_time = datetime.fromisoformat(reminder_data["reminder_time"])
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reminder_time format. Use ISO format."
            )
    if "sent" in reminder_data:
        db_reminder.sent = reminder_data["sent"]
    if "message" in reminder_data:
        db_reminder.message = reminder_data["message"]
    
    db.commit()
    db.refresh(db_reminder)
    
    return {
        "id": db_reminder.id,
        "message": "Reminder updated successfully"
    }

# 删除提醒
@router.delete("/{reminder_id}", response_model=dict)
def delete_existing_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
):
    db_reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    if db_reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    
    db.delete(db_reminder)
    db.commit()
    
    return {"message": "Reminder deleted successfully"}