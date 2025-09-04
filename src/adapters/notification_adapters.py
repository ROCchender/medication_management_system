from abc import ABC, abstractmethod
from typing import Dict, Any
import requests
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 通知适配器接口
class NotificationAdapter(ABC):
    @abstractmethod
    def send_message(self, recipient: str, message: str) -> bool:
        """发送通知消息"""
        pass

    @abstractmethod
    def send_verification_code(self, recipient: str, code: str) -> bool:
        """发送验证码"""
        pass

# SMS通知适配器
class SMSAdapter(NotificationAdapter):
    def __init__(self, api_key: str):
        self.api_key = api_key
        # 实际应用中应该使用真实的SMS API地址
        self.api_url = "https://api.sms-service.com/send"
    
    def send_message(self, recipient: str, message: str) -> bool:
        """发送短信通知"""
        try:
            # 在实际应用中，这里应该调用真实的SMS API
            # 目前只是模拟发送
            logger.info(f"[SMS] 向 {recipient} 发送消息: {message}")
            
            # 模拟API调用
            # response = requests.post(
            #     self.api_url,
            #     headers={"Authorization": f"Bearer {self.api_key}"},
            #     json={"phone": recipient, "content": message}
            # )
            # return response.status_code == 200
            
            return True
        except Exception as e:
            logger.error(f"发送短信失败: {str(e)}")
            return False
    
    def send_verification_code(self, recipient: str, code: str) -> bool:
        """发送验证码"""
        message = f"您的验证码是：{code}，有效期5分钟，请不要泄露给他人。"
        return self.send_message(recipient, message)

# 微信通知适配器
class WeChatAdapter(NotificationAdapter):
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expiry = 0
        self.api_url = "https://api.weixin.qq.com/cgi-bin"
    
    def _get_access_token(self) -> str:
        """获取微信访问令牌"""
        import time
        
        # 检查令牌是否有效
        if self.access_token and self.token_expiry > time.time():
            return self.access_token
        
        try:
            # 在实际应用中，这里应该调用微信API获取access_token
            # 目前只是模拟
            logger.info("获取微信access_token")
            
            # 模拟API调用
            # response = requests.get(
            #     f"{self.api_url}/token",
            #     params={
            #         "grant_type": "client_credential",
            #         "appid": self.app_id,
            #         "secret": self.app_secret
            #     }
            # )
            # data = response.json()
            # self.access_token = data.get("access_token")
            # self.token_expiry = time.time() + data.get("expires_in", 7200) - 300  # 提前5分钟刷新
            
            self.access_token = "mock_access_token"
            self.token_expiry = time.time() + 7200 - 300  # 有效期2小时，提前5分钟刷新
            
            return self.access_token
        except Exception as e:
            logger.error(f"获取微信access_token失败: {str(e)}")
            return None
    
    def send_message(self, recipient: str, message: str) -> bool:
        """发送微信消息"""
        try:
            access_token = self._get_access_token()
            if not access_token:
                return False
            
            # 在实际应用中，这里应该调用微信API发送消息
            # 目前只是模拟发送
            logger.info(f"[WeChat] 向 {recipient} 发送消息: {message}")
            
            # 模拟API调用
            # response = requests.post(
            #     f"{self.api_url}/message/custom/send",
            #     params={"access_token": access_token},
            #     json={
            #         "touser": recipient,
            #         "msgtype": "text",
            #         "text": {"content": message}
            #     }
            # )
            # return response.status_code == 200 and response.json().get("errcode") == 0
            
            return True
        except Exception as e:
            logger.error(f"发送微信消息失败: {str(e)}")
            return False
    
    def send_verification_code(self, recipient: str, code: str) -> bool:
        """发送验证码"""
        message = f"您的验证码是：{code}，有效期5分钟，请不要泄露给他人。"
        return self.send_message(recipient, message)

# 邮件通知适配器（扩展功能）
class EmailAdapter(NotificationAdapter):
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
    
    def send_message(self, recipient: str, message: str) -> bool:
        """发送邮件通知"""
        try:
            # 在实际应用中，这里应该使用SMTP发送邮件
            # 目前只是模拟发送
            logger.info(f"[Email] 向 {recipient} 发送消息: {message}")
            
            # 模拟SMTP发送
            # import smtplib
            # from email.mime.text import MIMEText
            # from email.header import Header
            # 
            # msg = MIMEText(message, 'plain', 'utf-8')
            # msg['From'] = Header(self.username)
            # msg['To'] = Header(recipient)
            # msg['Subject'] = Header('药物管理系统通知')
            # 
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()
            # server.login(self.username, self.password)
            # server.sendmail(self.username, [recipient], msg.as_string())
            # server.quit()
            
            return True
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False
    
    def send_verification_code(self, recipient: str, code: str) -> bool:
        """发送验证码"""
        message = f"您的验证码是：{code}，有效期5分钟，请不要泄露给他人。"
        return self.send_message(recipient, message)

# 通知管理器 - 用于管理多个通知适配器
class NotificationManager:
    def __init__(self):
        self.adapters = {}
    
    def register_adapter(self, name: str, adapter: NotificationAdapter):
        """注册通知适配器"""
        self.adapters[name] = adapter
    
    def send_message(self, adapter_name: str, recipient: str, message: str) -> bool:
        """通过指定的适配器发送消息"""
        adapter = self.adapters.get(adapter_name)
        if not adapter:
            logger.error(f"未找到名为 {adapter_name} 的通知适配器")
            return False
        
        return adapter.send_message(recipient, message)
    
    def send_verification_code(self, adapter_name: str, recipient: str, code: str) -> bool:
        """通过指定的适配器发送验证码"""
        adapter = self.adapters.get(adapter_name)
        if not adapter:
            logger.error(f"未找到名为 {adapter_name} 的通知适配器")
            return False
        
        return adapter.send_verification_code(recipient, code)
    
    def broadcast_message(self, recipients: Dict[str, str], message: str) -> Dict[str, bool]:
        """通过多个适配器广播消息"""
        results = {}
        
        for adapter_name, recipient in recipients.items():
            results[adapter_name] = self.send_message(adapter_name, recipient, message)
        
        return results

# 创建默认的通知管理器实例
def create_default_notification_manager(sms_api_key: str = None, wechat_app_id: str = None, wechat_app_secret: str = None) -> NotificationManager:
    manager = NotificationManager()
    
    # 注册SMS适配器
    if sms_api_key:
        manager.register_adapter("sms", SMSAdapter(sms_api_key))
    
    # 注册微信适配器
    if wechat_app_id and wechat_app_secret:
        manager.register_adapter("wechat", WeChatAdapter(wechat_app_id, wechat_app_secret))
    
    return manager

# 简化的通知发送函数
def send_notification(recipient_type: str, recipient: str, message: str, **adapter_config) -> bool:
    """简化的通知发送函数"""
    
    if recipient_type == "sms":
        adapter = SMSAdapter(adapter_config.get("api_key", ""))
    elif recipient_type == "wechat":
        adapter = WeChatAdapter(
            adapter_config.get("app_id", ""),
            adapter_config.get("app_secret", "")
        )
    elif recipient_type == "email":
        adapter = EmailAdapter(
            adapter_config.get("smtp_server", ""),
            adapter_config.get("smtp_port", 587),
            adapter_config.get("username", ""),
            adapter_config.get("password", "")
        )
    else:
        logger.error(f"不支持的通知类型: {recipient_type}")
        return False
    
    return adapter.send_message(recipient, message)