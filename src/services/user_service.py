from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import hashlib
import random
import string

from ..models.user import User
from ..models.reminder import Reminder
from ..models.medication import Medication
from ..adapters.notification_adapters import SMSAdapter, WeChatAdapter
from ..config import settings

# 创建用户
def create_user(
    db: Session,
    username: str,
    password: str,
    phone_number: str = None,
    wechat_openid: str = None
) -> User:
    # 密码加密
    hashed_password = hash_password(password)
    
    user = User(
        username=username,
        password_hash=hashed_password,
        phone_number=phone_number,
        wechat_openid=wechat_openid
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

# 密码加密
def hash_password(password: str) -> str:
    # 使用SHA256加密密码
    return hashlib.sha256(password.encode()).hexdigest()

# 验证密码
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

# 获取所有用户
def get_users(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()

# 获取单个用户
def get_user(
    db: Session,
    user_id: int
) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

# 根据用户名获取用户
def get_user_by_username(
    db: Session,
    username: str
) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

# 根据手机号获取用户
def get_user_by_phone(
    db: Session,
    phone_number: str
) -> Optional[User]:
    return db.query(User).filter(User.phone_number == phone_number).first()

# 根据微信OpenID获取用户
def get_user_by_wechat(
    db: Session,
    wechat_openid: str
) -> Optional[User]:
    return db.query(User).filter(User.wechat_openid == wechat_openid).first()

# 更新用户
def update_user(
    db: Session,
    user_id: int,
    **kwargs
) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return None
    
    # 处理密码更新
    if "password" in kwargs:
        kwargs["password_hash"] = hash_password(kwargs.pop("password"))
    
    for key, value in kwargs.items():
        if hasattr(user, key):
            setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return user

# 删除用户
def delete_user(
    db: Session,
    user_id: int
) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        return False
    
    db.delete(user)
    db.commit()
    
    return True

# 绑定手机号
def bind_phone_number(
    db: Session,
    user_id: int,
    phone_number: str
) -> Optional[User]:
    # 检查手机号是否已被绑定
    existing_user = get_user_by_phone(db, phone_number)
    if existing_user and existing_user.id != user_id:
        raise ValueError("该手机号已被其他用户绑定")
    
    # 更新用户信息
    user = update_user(db, user_id, phone_number=phone_number)
    
    # 生成并发送验证码（模拟）
    verification_code = generate_verification_code()
    
    # 在实际应用中，这里应该调用SMSAdapter发送验证码
    # sms_adapter = SMSAdapter(settings.SMS_API_KEY)
    # sms_adapter.send_verification_code(phone_number, verification_code)
    
    # 存储验证码（实际应用中应该使用缓存或临时存储）
    # 这里只是示例，实际应使用更安全的方式
    db.query(User).filter(User.id == user_id).update({
        "verification_code": verification_code
    })
    db.commit()
    
    return user

# 验证手机号
def verify_phone_number(
    db: Session,
    user_id: int,
    verification_code: str
) -> bool:
    user = get_user(db, user_id)
    
    if not user or user.verification_code != verification_code:
        return False
    
    # 验证成功，清除验证码并标记手机号已验证
    db.query(User).filter(User.id == user_id).update({
        "verification_code": None,
        "is_phone_verified": True
    })
    db.commit()
    
    return True

# 绑定微信账号
def bind_wechat_account(
    db: Session,
    user_id: int,
    wechat_openid: str
) -> Optional[User]:
    # 检查微信OpenID是否已被绑定
    existing_user = get_user_by_wechat(db, wechat_openid)
    if existing_user and existing_user.id != user_id:
        raise ValueError("该微信账号已被其他用户绑定")
    
    # 更新用户信息
    user = update_user(db, user_id, wechat_openid=wechat_openid, is_wechat_verified=True)
    
    return user

# 生成验证码
def generate_verification_code(length: int = 6) -> str:
    # 生成指定长度的数字验证码
    return ''.join(random.choices(string.digits, k=length))

# 获取用户的所有药物
def get_user_medications(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Medication]:
    return db.query(Medication).filter(
        Medication.user_id == user_id
    ).offset(skip).limit(limit).all()

# 获取用户的所有提醒
def get_user_reminders(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Reminder]:
    return db.query(Reminder).filter(
        Reminder.user_id == user_id
    ).offset(skip).limit(limit).all()

# 登录验证
def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> Optional[User]:
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password_hash):
        return user
    return None

# 检查用户通知设置
def get_user_notification_preferences(
    db: Session,
    user_id: int
) -> Dict[str, bool]:
    user = get_user(db, user_id)
    
    if not user:
        return {
            "sms_notification": False,
            "wechat_notification": False
        }
    
    return {
        "sms_notification": user.sms_notification if user.sms_notification is not None else True,
        "wechat_notification": user.wechat_notification if user.wechat_notification is not None else True
    }

# 更新用户通知设置
def update_user_notification_preferences(
    db: Session,
    user_id: int,
    sms_notification: bool = None,
    wechat_notification: bool = None
) -> Optional[User]:
    user = get_user(db, user_id)
    
    if not user:
        return None
    
    if sms_notification is not None:
        user.sms_notification = sms_notification
    
    if wechat_notification is not None:
        user.wechat_notification = wechat_notification
    
    db.commit()
    db.refresh(user)
    
    return user