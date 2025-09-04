from fastapi import APIRouter

from .medication_routes import router as medication_router
from .disease_routes import router as disease_router
from .user_routes import router as user_router
from .reminder_routes import router as reminder_router

# 创建主路由器
main_router = APIRouter()

# 包含药物路由
main_router.include_router(
    medication_router,
    prefix="/medications",
    tags=["medications"],
    responses={404: {"description": "Not found"}},
)

# 包含疾病路由
main_router.include_router(
    disease_router,
    prefix="/diseases",
    tags=["diseases"],
    responses={404: {"description": "Not found"}},
)

# 包含用户路由
main_router.include_router(
    user_router,
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# 包含提醒路由
main_router.include_router(
    reminder_router,
    prefix="/reminders",
    tags=["reminders"],
    responses={404: {"description": "Not found"}},
)

# 添加认证相关路由
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict

from ..database import get_db
from ..services.user_service import authenticate_user, get_user_by_username, create_user as create_user_service
from ..middleware.auth_middleware import generate_token

# 认证路由器
auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={404: {"description": "Not found"}},
)

# 登录接口
@auth_router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    用户登录接口
    - **username**: 用户名
    - **password**: 密码
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成令牌
    access_token = generate_token(user.id)
    
    return {"access_token": access_token, "token_type": "bearer"}

# 注册接口
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    username: str,
    password: str,
    phone_number: str = None,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    用户注册接口
    - **username**: 用户名
    - **password**: 密码
    - **phone_number**: 手机号码（可选）
    """
    # 检查用户名是否已存在
    existing_user = get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 创建新用户
    user = create_user_service(
        db=db,
        username=username,
        password=password,
        phone_number=phone_number
    )
    
    return {"message": "用户注册成功"}

# 包含认证路由到主路由
main_router.include_router(auth_router)

# 添加健康检查路由
@main_router.get("/health")
def health_check() -> Dict[str, str]:
    """
    健康检查接口
    """
    return {"status": "healthy"}

# 添加根路由
@main_router.get("/")
def root() -> Dict[str, str]:
    """
    API根接口
    """
    return {"message": "欢迎使用药物管理系统API"}

# 添加API文档路由
@main_router.get("/api-docs")
def api_docs() -> Dict[str, str]:
    """
    API文档指引接口
    """
    return {
        "message": "请访问以下链接查看完整API文档",
        "swagger_ui": "/docs",
        "redoc": "/redoc"
    }

# 添加关于接口
@main_router.get("/about")
def about() -> Dict[str, str]:
    """
    关于系统接口
    """
    return {
        "name": "药物管理系统",
        "version": "1.0.0",
        "description": "一个基于FastAPI的药物管理系统，支持药物柜管理、疾病到药物推荐、过期提醒等功能。"
    }