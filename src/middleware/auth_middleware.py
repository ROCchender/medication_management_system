from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional, Callable
import time
import logging

from ..database import get_db
from ..models.user import User
from ..services.user_service import get_user

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建HTTP Bearer安全方案
bearer_scheme = HTTPBearer()

# 模拟的令牌存储（实际应用中应该使用数据库或Redis存储令牌）
# 格式: {token: {user_id: int, expiry: float}}
TOKENS = {}

# 生成认证令牌
def generate_token(user_id: int, expiry_hours: int = 24) -> str:
    """生成认证令牌"""
    import uuid
    import hashlib
    
    # 生成唯一令牌
    token = str(uuid.uuid4())
    # 为了安全，可以进一步处理令牌
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    # 计算令牌过期时间
    expiry = time.time() + (expiry_hours * 3600)
    
    # 存储令牌信息
    TOKENS[token_hash] = {"user_id": user_id, "expiry": expiry}
    
    logger.info(f"为用户 {user_id} 生成令牌")
    return token_hash

# 验证令牌
def validate_token(token: str) -> Optional[int]:
    """验证令牌并返回用户ID"""
    # 检查令牌是否存在
    if token not in TOKENS:
        logger.warning("无效的令牌")
        return None
    
    token_info = TOKENS[token]
    current_time = time.time()
    
    # 检查令牌是否过期
    if token_info["expiry"] < current_time:
        # 删除过期令牌
        del TOKENS[token]
        logger.warning("令牌已过期")
        return None
    
    logger.info(f"令牌验证成功，用户ID: {token_info['user_id']}")
    return token_info["user_id"]

# 注销令牌
def revoke_token(token: str) -> bool:
    """注销令牌"""
    if token in TOKENS:
        del TOKENS[token]
        logger.info("令牌已注销")
        return True
    
    logger.warning("尝试注销不存在的令牌")
    return False

# 获取当前用户
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """\获取当前认证的用户"""
    token = credentials.credentials
    user_id = validate_token(token)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="无效或过期的令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user = get_user(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="用户不存在"
        )
    
    return user

# 认证中间件类
class AuthMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # 记录请求开始时间
        start_time = time.time()
        
        # 获取请求路径
        path = request.url.path
        
        # 列出不需要认证的路径
        excluded_paths = [
            "/", "/docs", "/redoc", "/openapi.json",
            "/api/auth/login", "/api/auth/register",
            # 其他公开API路径...
        ]
        
        # 检查是否需要认证
        requires_auth = True
        for excluded_path in excluded_paths:
            if path.startswith(excluded_path):
                requires_auth = False
                break
        
        # 如果需要认证，验证令牌
        if requires_auth:
            try:
                # 从请求头中获取Authorization
                auth_header = request.headers.get("Authorization")
                
                if not auth_header or not auth_header.startswith("Bearer "):
                    raise HTTPException(
                        status_code=401,
                        detail="未提供认证令牌",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                # 提取令牌
                token = auth_header[len("Bearer "):]
                user_id = validate_token(token)
                
                if not user_id:
                    raise HTTPException(
                        status_code=401,
                        detail="无效或过期的令牌",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
                
                # 将用户ID添加到请求状态中
                request.state.user_id = user_id
                
            except HTTPException as e:
                # 处理认证异常
                logger.warning(f"认证失败: {str(e.detail)}")
                response = Response(
                    content=json.dumps({"detail": e.detail}),
                    status_code=e.status_code,
                    headers={"WWW-Authenticate": "Bearer"}
                )
                response.headers["Content-Type"] = "application/json"
                return response
            except Exception as e:
                # 处理其他异常
                logger.error(f"认证过程中发生错误: {str(e)}")
                response = Response(
                    content=json.dumps({"detail": "认证过程中发生错误"}),
                    status_code=500
                )
                response.headers["Content-Type"] = "application/json"
                return response
        
        # 处理请求
        response = await call_next(request)
        
        # 记录请求处理时间
        process_time = time.time() - start_time
        logger.info(f"请求路径: {path}, 处理时间: {process_time:.4f}秒")
        
        return response

# 错误处理中间件
class ErrorHandlingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        try:
            # 处理请求
            response = await call_next(request)
            return response
        except HTTPException as e:
            # 处理HTTP异常
            logger.warning(f"HTTP异常: {e.status_code} - {e.detail}")
            # 在实际应用中，应该返回统一的错误响应格式
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            # 处理其他异常
            logger.error(f"服务器错误: {str(e)}")
            # 在实际应用中，应该返回统一的错误响应格式，并记录详细错误信息
            return JSONResponse(
                status_code=500,
                content={"detail": "服务器内部错误"}
            )

# 日志中间件
class LoggingMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # 记录请求信息
        logger.info(f"请求方法: {request.method}, 请求路径: {request.url.path}")
        
        # 如果是POST或PUT请求，记录请求体
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    # 尝试解析JSON
                    try:
                        import json
                        body_json = json.loads(body)
                        # 过滤敏感信息
                        if isinstance(body_json, dict):
                            if "password" in body_json:
                                body_json["password"] = "[REDACTED]"
                            if "credit_card" in body_json:
                                body_json["credit_card"] = "[REDACTED]"
                        logger.info(f"请求体: {json.dumps(body_json)}")
                    except:
                        # 如果不是有效的JSON，记录原始内容的前100个字符
                        logger.info(f"请求体: {body[:100]}...")
            except Exception as e:
                logger.warning(f"无法读取请求体: {str(e)}")
        
        # 处理请求
        response = await call_next(request)
        
        # 记录响应信息
        logger.info(f"响应状态码: {response.status_code}")
        
        return response

# CORS中间件配置函数
def setup_cors_middleware(app):
    """设置CORS中间件"""
    from fastapi.middleware.cors import CORSMiddleware
    
    # 允许的源
    origins = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        # 其他允许的源...
    ]
    
    # 添加CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# 速率限制中间件
class RateLimiterMiddleware:
    def __init__(self, app, max_requests: int = 100, time_window: int = 60):
        self.app = app
        self.max_requests = max_requests  # 时间窗口内的最大请求数
        self.time_window = time_window  # 时间窗口（秒）
        self.requests = {}
    
    async def __call__(self, request: Request, call_next):
        # 获取客户端IP地址
        client_ip = request.client.host
        
        # 获取当前时间戳
        current_time = time.time()
        
        # 清理过期的请求记录
        if client_ip in self.requests:
            self.requests[client_ip] = [
                timestamp for timestamp in self.requests[client_ip]
                if current_time - timestamp < self.time_window
            ]
        else:
            self.requests[client_ip] = []
        
        # 检查请求数是否超过限制
        if len(self.requests[client_ip]) >= self.max_requests:
            logger.warning(f"IP地址 {client_ip} 请求过于频繁")
            # 在实际应用中，应该返回统一的错误响应格式
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"}
            )
        
        # 记录请求时间
        self.requests[client_ip].append(current_time)
        
        # 处理请求
        response = await call_next(request)
        
        return response

# 初始化所有中间件
def setup_middlewares(app):
    """设置所有中间件"""
    # 设置CORS中间件
    setup_cors_middleware(app)
    
    # 添加错误处理中间件
    # app.add_middleware(ErrorHandlingMiddleware)
    
    # 添加日志中间件
    # app.add_middleware(LoggingMiddleware)
    
    # 添加速率限制中间件
    # app.add_middleware(RateLimiterMiddleware, max_requests=100, time_window=60)
    
    # 注意：认证中间件通常不通过app.add_middleware添加，而是通过依赖项或路由守卫实现
    
    logger.info("所有中间件已设置完成")

# 导入需要的模块
from fastapi.responses import Response, JSONResponse
import json