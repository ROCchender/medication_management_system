from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .database import SessionLocal, engine
from .models.medication import Medication
from .models.disease import Disease
from .models.user import User
from .models.reminder import Reminder
from .routes.main_router import main_router
from .config import settings

# 创建数据库表
Medication.metadata.create_all(bind=engine)
Disease.metadata.create_all(bind=engine)
User.metadata.create_all(bind=engine)
Reminder.metadata.create_all(bind=engine)

# 初始化FastAPI应用
app = FastAPI(title="Medication Management System", description="药物管理系统", version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 挂载主路由
app.include_router(main_router, prefix="/api")

# 根路径
@app.get("/")
async def root():
    return {"message": "Welcome to Medication Management System"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)