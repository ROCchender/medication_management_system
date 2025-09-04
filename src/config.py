from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    HOST: str = '0.0.0.0'
    PORT: int = 8000
    DEBUG: bool = True
    # CORS配置
    CORS_ORIGINS: List[str] = ["*"]
    
    # 提醒配置
    EXPIRY_REMINDER_DAYS: int = 30  # 过期前30天开始提醒
    
    # 短信配置
    SMS_ENABLED: bool = False
    SMS_API_KEY: str = "your_api_key"
    SMS_API_SECRET: str = "your_api_secret"
    
    # 微信配置
    WECHAT_ENABLED: bool = False
    WECHAT_APP_ID: str = "your_app_id"
    WECHAT_APP_SECRET: str = "your_app_secret"
    
    # 药物信息API
    MEDICATION_API_URL: str = "https://api.medication-info.com/v1"
    MEDICATION_API_KEY: str = "your_medication_api_key"

# 实例化配置
settings = Settings()