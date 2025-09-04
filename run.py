import uvicorn
from src.config import settings

if __name__ == "__main__":
    # 从配置中获取运行参数
    host = settings.HOST
    port = settings.PORT
    reload = settings.DEBUG
    
    print(f"\n药物管理系统启动信息:")
    print(f"- 运行模式: {'调试' if reload else '生产'}")
    print(f"- 访问地址: http://{host}:{port}")
    print(f"- API文档: http://{host}:{port}/docs")
    print(f"- 替代文档: http://{host}:{port}/redoc")
    print(f"\n按 Ctrl+C 停止服务...\n")
    
    # 启动服务器
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info" if reload else "warning"
    )