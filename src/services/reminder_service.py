from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from ..models.reminder import Reminder
from ..models.medication import Medication
from ..models.user import User
from ..adapters.notification_adapters import SMSAdapter, WeChatAdapter
from ..config import settings

# 创建提醒
def create_reminder(
    db: Session,
    user_id: int,
    medication_id: int,
    reminder_type: str,
    reminder_time: datetime,
    message: str = None
) -> Reminder:
    reminder = Reminder(
        user_id=user_id,
        medication_id=medication_id,
        reminder_type=reminder_type,
        reminder_time=reminder_time,
        message=message,
        is_sent=False
    )
    
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    
    return reminder

# 获取所有提醒
def get_reminders(
    db: Session,
    skip: int = 0,
    limit: int = 100
) -> List[Reminder]:
    return db.query(Reminder).offset(skip).limit(limit).all()

# 获取用户的提醒
def get_user_reminders(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Reminder]:
    return db.query(Reminder).filter(
        Reminder.user_id == user_id
    ).offset(skip).limit(limit).all()

# 获取单个提醒
def get_reminder(
    db: Session,
    reminder_id: int
) -> Optional[Reminder]:
    return db.query(Reminder).filter(Reminder.id == reminder_id).first()

# 更新提醒
def update_reminder(
    db: Session,
    reminder_id: int,
    **kwargs
) -> Optional[Reminder]:
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    
    if not reminder:
        return None
    
    for key, value in kwargs.items():
        if hasattr(reminder, key):
            setattr(reminder, key, value)
    
    db.commit()
    db.refresh(reminder)
    
    return reminder

# 删除提醒
def delete_reminder(
    db: Session,
    reminder_id: int
) -> bool:
    reminder = db.query(Reminder).filter(Reminder.id == reminder_id).first()
    
    if not reminder:
        return False
    
    db.delete(reminder)
    db.commit()
    
    return True

# 检查并发送到期提醒
def check_and_send_reminders(
    db: Session
) -> Dict[str, int]:
    now = datetime.now()
    # 查找5分钟内需要发送的提醒
    reminders_to_send = db.query(Reminder).filter(
        Reminder.reminder_time <= now + timedelta(minutes=5),
        Reminder.reminder_time >= now - timedelta(minutes=5),  # 允许有一定的时间窗口
        Reminder.is_sent == False
    ).all()
    
    results = {
        "total_reminders_to_send": len(reminders_to_send),
        "sms_reminders_sent": 0,
        "wechat_reminders_sent": 0,
        "failed_reminders": 0
    }
    
    # 初始化通知适配器
    sms_adapter = SMSAdapter(settings.SMS_API_KEY)
    wechat_adapter = WeChatAdapter(settings.WECHAT_APP_ID, settings.WECHAT_APP_SECRET)
    
    for reminder in reminders_to_send:
        try:
            # 获取用户信息
            user = db.query(User).filter(User.id == reminder.user_id).first()
            if not user:
                results["failed_reminders"] += 1
                continue
            
            # 获取药物信息
            medication = db.query(Medication).filter(Medication.id == reminder.medication_id).first()
            if not medication:
                results["failed_reminders"] += 1
                continue
            
            # 构建提醒消息
            if not reminder.message:
                if reminder.reminder_type == "expiry":
                    reminder.message = f"您的药物 '{medication.name}' 将在{settings.EXPIRY_REMINDER_DAYS}天后过期，请及时处理！"
                elif reminder.reminder_type == "usage":
                    reminder.message = f"请按时服用药物 '{medication.name}'！"
            
            # 根据用户设置发送通知
            sent = False
            
            # 发送短信通知（如果用户开启了短信通知且绑定了手机号）
            if user.sms_notification and user.phone_number and user.is_phone_verified:
                sms_result = sms_adapter.send_message(
                    user.phone_number,
                    reminder.message
                )
                if sms_result:
                    results["sms_reminders_sent"] += 1
                    sent = True
            
            # 发送微信通知（如果用户开启了微信通知且绑定了微信）
            if user.wechat_notification and user.wechat_openid and user.is_wechat_verified:
                wechat_result = wechat_adapter.send_message(
                    user.wechat_openid,
                    reminder.message
                )
                if wechat_result:
                    results["wechat_reminders_sent"] += 1
                    sent = True
            
            # 更新提醒状态
            if sent:
                reminder.is_sent = True
                reminder.sent_time = datetime.now()
                db.commit()
            else:
                results["failed_reminders"] += 1
        except Exception as e:
            # 记录错误，但继续处理其他提醒
            results["failed_reminders"] += 1
    
    return results

# 为即将过期的药物安排提醒
def schedule_expiry_reminders(
    db: Session,
    days_ahead: int = settings.EXPIRY_REMINDER_DAYS
) -> Dict[str, int]:
    now = datetime.now()
    reminder_date = now + timedelta(days=days_ahead)
    
    # 查找即将过期但还没有提醒的药物
    medications = db.query(Medication).filter(
        Medication.expiry_date <= reminder_date + timedelta(days=1),
        Medication.expiry_date >= reminder_date - timedelta(days=1),
        Medication.is_expired == False,
        Medication.is_near_expiry == True
    ).all()
    
    results = {
        "total_medications": len(medications),
        "reminders_scheduled": 0
    }
    
    for medication in medications:
        # 检查是否已经为该药物安排了过期提醒
        existing_reminder = db.query(Reminder).filter(
            Reminder.user_id == medication.user_id,
            Reminder.medication_id == medication.id,
            Reminder.reminder_type == "expiry",
            Reminder.is_sent == False
        ).first()
        
        if not existing_reminder:
            # 创建新的提醒
            reminder_time = medication.expiry_date - timedelta(days=days_ahead)
            # 确保提醒时间在未来
            if reminder_time > now:
                create_reminder(
                    db=db,
                    user_id=medication.user_id,
                    medication_id=medication.id,
                    reminder_type="expiry",
                    reminder_time=reminder_time
                )
                results["reminders_scheduled"] += 1
    
    return results

# 批量创建用药提醒
def create_usage_reminders(
    db: Session,
    user_id: int,
    medication_id: int,
    frequency: str,  # 例如："daily", "weekly", "monthly"
    times_per_day: int = 1,
    start_date: datetime = None,
    end_date: datetime = None,
    message: str = None
) -> List[Reminder]:
    created_reminders = []
    
    # 默认开始日期为今天
    if not start_date:
        start_date = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    
    # 根据频率生成提醒时间
    if frequency == "daily":
        # 计算每次提醒的时间间隔
        interval_hours = 24 / times_per_day
        
        # 生成未来30天的提醒
        for i in range(30):
            for j in range(times_per_day):
                reminder_time = start_date + timedelta(
                    days=i,
                    hours=j * interval_hours
                )
                
                # 检查是否超过结束日期
                if end_date and reminder_time > end_date:
                    break
                
                # 创建提醒
                reminder = create_reminder(
                    db=db,
                    user_id=user_id,
                    medication_id=medication_id,
                    reminder_type="usage",
                    reminder_time=reminder_time,
                    message=message
                )
                created_reminders.append(reminder)
    
    elif frequency == "weekly":
        # 生成未来4周的提醒（每周一次）
        for i in range(4):
            reminder_time = start_date + timedelta(weeks=i)
            
            # 检查是否超过结束日期
            if end_date and reminder_time > end_date:
                break
            
            # 创建提醒
            reminder = create_reminder(
                db=db,
                user_id=user_id,
                medication_id=medication_id,
                reminder_type="usage",
                reminder_time=reminder_time,
                message=message
            )
            created_reminders.append(reminder)
    
    elif frequency == "monthly":
        # 生成未来3个月的提醒（每月一次）
        for i in range(3):
            # 简单的月份计算（不考虑月底的特殊情况）
            reminder_month = start_date.month + i
            reminder_year = start_date.year
            
            if reminder_month > 12:
                reminder_month -= 12
                reminder_year += 1
            
            # 尝试创建日期，如果日期不存在（例如2月30日），则使用月末
            try:
                reminder_time = start_date.replace(year=reminder_year, month=reminder_month)
            except ValueError:
                # 处理月末日期
                if reminder_month == 2:
                    days_in_month = 28
                    if (reminder_year % 4 == 0 and reminder_year % 100 != 0) or (reminder_year % 400 == 0):
                        days_in_month = 29
                elif reminder_month in [4, 6, 9, 11]:
                    days_in_month = 30
                else:
                    days_in_month = 31
                
                reminder_time = start_date.replace(
                    year=reminder_year,
                    month=reminder_month,
                    day=days_in_month
                )
            
            # 检查是否超过结束日期
            if end_date and reminder_time > end_date:
                break
            
            # 创建提醒
            reminder = create_reminder(
                db=db,
                user_id=user_id,
                medication_id=medication_id,
                reminder_type="usage",
                reminder_time=reminder_time,
                message=message
            )
            created_reminders.append(reminder)
    
    return created_reminders

# 获取即将到期的提醒
def get_upcoming_reminders(
    db: Session,
    user_id: int,
    hours_ahead: int = 24
) -> List[Reminder]:
    now = datetime.now()
    upcoming_time = now + timedelta(hours=hours_ahead)
    
    return db.query(Reminder).filter(
        Reminder.user_id == user_id,
        Reminder.reminder_time >= now,
        Reminder.reminder_time <= upcoming_time,
        Reminder.is_sent == False
    ).order_by(Reminder.reminder_time.asc()).all()