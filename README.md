# 药物管理系统

一个基于FastAPI+SQLite的简易药物管理系统，用于帮助用户管理家中的药物信息、获取疾病用药推荐以及接收过期提醒。

## 功能特点

- **药物柜管理**：手动添加药物信息，自动计算过期日期，输入药名自动补全功效/用法/图片
- **疾病到药物推荐**：优先推荐用户药物柜中的药物，不足时提供购买推荐
- **通知功能**：支持短信/微信过期提醒，可自定义提醒设置
- **用户管理**：支持用户注册、登录、个人信息管理等功能
- **用药提醒**：可设置定时用药提醒，确保按时服药

## 技术栈

- **后端框架**：FastAPI
- **数据库**：SQLite
- **ORM**：SQLAlchemy
- **API文档**：Swagger UI (自动生成)
- **部署工具**：Uvicorn

## 项目结构

```
medication_management_system/
├── src/
│   ├── main.py               # FastAPI应用入口
│   ├── database.py           # 数据库配置
│   ├── config.py             # 系统配置
│   ├── models/               # 数据模型
│   │   ├── __init__.py
│   │   ├── medication.py     # 药物模型
│   │   ├── disease.py        # 疾病模型
│   │   ├── user.py           # 用户模型
│   │   └── reminder.py       # 提醒模型
│   ├── routes/               # API路由
│   │   ├── __init__.py
│   │   ├── medication_routes.py  # 药物相关路由
│   │   ├── disease_routes.py     # 疾病相关路由
│   │   ├── user_routes.py        # 用户相关路由
│   │   ├── reminder_routes.py    # 提醒相关路由
│   │   └── main_router.py        # 主路由集成
│   ├── services/             # 业务逻辑
│   │   ├── __init__.py
│   │   ├── medication_service.py  # 药物服务
│   │   ├── disease_service.py     # 疾病服务
│   │   ├── user_service.py        # 用户服务
│   │   └── reminder_service.py    # 提醒服务
│   ├── adapters/             # 适配器
│   │   ├── __init__.py
│   │   └── notification_adapters.py  # 通知适配器
│   ├── middleware/           # 中间件
│   │   ├── __init__.py
│   │   └── auth_middleware.py       # 认证中间件
│   └── utils/                # 工具函数
│       ├── __init__.py
│       └── medication_search.py     # 药物搜索工具
├── requirements.txt          # 项目依赖
├── run.py                    # 启动脚本
└── README.md                 # 项目说明
```

## 安装和运行

### 1. 克隆项目

```bash
git clone https://github.com/yourusername/medication_management_system.git
cd medication_management_system
```

### 2. 创建虚拟环境（可选但推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行项目

```bash
python run.py
```

系统默认在 http://127.0.0.1:8000 启动。

## API文档

项目启动后，可以访问以下地址查看自动生成的API文档：

- Swagger UI：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc

## 主要API端点

### 认证接口
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/register` - 用户注册

### 药物管理接口
- `GET /api/medications` - 获取所有药物
- `GET /api/medications/{medication_id}` - 获取单个药物
- `POST /api/medications` - 创建药物
- `PUT /api/medications/{medication_id}` - 更新药物
- `DELETE /api/medications/{medication_id}` - 删除药物
- `GET /api/medications/search` - 搜索药物信息
- `GET /api/medications/by_disease` - 根据疾病获取药物推荐

### 疾病管理接口
- `GET /api/diseases` - 获取所有疾病
- `GET /api/diseases/{disease_id}` - 获取单个疾病
- `POST /api/diseases` - 创建疾病
- `PUT /api/diseases/{disease_id}` - 更新疾病
- `DELETE /api/diseases/{disease_id}` - 删除疾病

### 用户管理接口
- `GET /api/users` - 获取所有用户（管理员）
- `GET /api/users/{user_id}` - 获取用户信息
- `PUT /api/users/{user_id}` - 更新用户信息
- `DELETE /api/users/{user_id}` - 删除用户
- `POST /api/users/{user_id}/bind_phone` - 绑定手机号
- `POST /api/users/{user_id}/verify_phone` - 验证手机号
- `POST /api/users/{user_id}/bind_wechat` - 绑定微信账号

### 提醒管理接口
- `GET /api/reminders` - 获取所有提醒
- `GET /api/reminders/{reminder_id}` - 获取单个提醒
- `POST /api/reminders` - 创建提醒
- `PUT /api/reminders/{reminder_id}` - 更新提醒
- `DELETE /api/reminders/{reminder_id}` - 删除提醒
- `POST /api/reminders/check_and_send` - 检查并发送提醒
- `POST /api/reminders/schedule_expiry` - 安排过期提醒

## 配置说明

项目配置位于 `src/config.py` 文件中，主要配置项包括：

- CORS_ORIGINS - 允许的跨域请求源
- DATABASE_URL - 数据库连接URL
- EXPIRY_REMINDER_DAYS - 过期提醒提前天数
- SMS_API_KEY - 短信API密钥
- WECHAT_APP_ID/WECHAT_APP_SECRET - 微信公众号配置
- HOST/PORT - 服务器主机和端口
- DEBUG - 调试模式开关

## 注意事项

1. 本项目使用SQLite数据库，数据存储在项目根目录的 `medication.db` 文件中
2. 短信和微信通知功能目前使用模拟实现，实际部署时需要配置真实的API密钥
3. 开发环境下推荐开启DEBUG模式，生产环境请关闭
4. 默认管理员账号：admin / admin123（首次运行时自动创建）

## 开发指南

1. 遵循FastAPI和Python的最佳实践
2. 所有数据库操作通过services层进行，保持路由层的简洁
3. 使用Pydantic模型进行数据验证和序列化
4. 新增功能时，先创建数据模型，然后实现服务层，最后添加API路由
5. 提交代码前确保通过所有测试

