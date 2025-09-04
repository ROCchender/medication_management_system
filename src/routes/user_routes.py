from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from ..database import get_db
from ..models.user import User
from ..services.user_service import (
    create_user,
    get_users,
    get_user,
    update_user,
    delete_user,
    bind_phone_number,
    verify_phone_number,
    bind_wechat_account
)

router = APIRouter()

# 创建用户
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_new_user(
    user_data: dict,
    db: Session = Depends(get_db)
):
    # 检查必填字段
    if "username" not in user_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: username"
        )
    
    # 创建用户
    user = create_user(
        db=db,
        username=user_data["username"]
    )
    
    return {
        "id": user.id,
        "username": user.username,
        "message": "User created successfully"
    }

# 获取所有用户
@router.get("/", response_model=List[dict])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    users = get_users(db, skip=skip, limit=limit)
    return [
        {
            "id": user.id,
            "username": user.username,
            "phone_number": user.phone_number,
            "wechat_openid": user.wechat_openid,
            "phone_verified": user.phone_verified,
            "wechat_verified": user.wechat_verified
        } for user in users
    ]

# 获取单个用户
@router.get("/{user_id}", response_model=dict)
def read_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    db_user = get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "phone_number": db_user.phone_number,
        "wechat_openid": db_user.wechat_openid,
        "phone_verified": db_user.phone_verified,
        "wechat_verified": db_user.wechat_verified
    }

# 更新用户
@router.put("/{user_id}", response_model=dict)
def update_existing_user(
    user_id: int,
    user_data: dict,
    db: Session = Depends(get_db)
):
    db_user = update_user(db, user_id=user_id, **user_data)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": db_user.id,
        "username": db_user.username,
        "message": "User updated successfully"
    }

# 删除用户
@router.delete("/{user_id}", response_model=dict)
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    success = delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return {"message": "User deleted successfully"}

# 绑定手机号码
@router.post("/{user_id}/bind-phone", response_model=dict)
def bind_user_phone_number(
    user_id: int,
    phone_data: dict,
    db: Session = Depends(get_db)
):
    # 检查必填字段
    if "phone_number" not in phone_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: phone_number"
        )
    
    # 绑定手机号
    user = bind_phone_number(
        db=db,
        user_id=user_id,
        phone_number=phone_data["phone_number"]
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "phone_number": user.phone_number,
        "message": "Phone number bound successfully. Please verify."
    }

# 验证手机号码
@router.post("/{user_id}/verify-phone", response_model=dict)
def verify_user_phone_number(
    user_id: int,
    verification_data: dict,
    db: Session = Depends(get_db)
):
    # 这里简化处理，实际应用中应该有验证码验证逻辑
    # 检查必填字段
    if "verification_code" not in verification_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: verification_code"
        )
    
    # 验证手机号
    # 注意：实际应用中应该有验证码生成和验证的完整流程
    user = verify_phone_number(
        db=db,
        user_id=user_id,
        verification_code=verification_data["verification_code"]
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or verification failed"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "phone_verified": user.phone_verified,
        "message": "Phone number verified successfully"
    }

# 绑定微信账号
@router.post("/{user_id}/bind-wechat", response_model=dict)
def bind_user_wechat_account(
    user_id: int,
    wechat_data: dict,
    db: Session = Depends(get_db)
):
    # 检查必填字段
    if "wechat_openid" not in wechat_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required field: wechat_openid"
        )
    
    # 绑定微信
    user = bind_wechat_account(
        db=db,
        user_id=user_id,
        wechat_openid=wechat_data["wechat_openid"]
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "wechat_openid": user.wechat_openid,
        "message": "WeChat account bound successfully. Please verify."
    }

# 验证微信账号
@router.post("/{user_id}/verify-wechat", response_model=dict)
def verify_user_wechat_account(
    user_id: int,
    verification_data: dict,
    db: Session = Depends(get_db)
):
    # 这里简化处理，实际应用中应该有微信验证逻辑
    # 验证微信
    user = verify_wechat_account(
        db=db,
        user_id=user_id,
        verification_data=verification_data
    )
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or verification failed"
        )
    
    return {
        "id": user.id,
        "username": user.username,
        "wechat_verified": user.wechat_verified,
        "message": "WeChat account verified successfully"
    }