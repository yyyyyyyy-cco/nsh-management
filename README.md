# 轻衫都会用的帮会联赛管理系统

> 专为游戏帮会管理人员设计的一体化管理工具，涵盖成员管理、出勤考核、联赛排表、录屏审核和比赛数据分析等核心功能。

> 📘 开发协作规范（分支/提交/发布/tag）见 [GIT-GUIDE.md](GIT-GUIDE.md)。

## 功能特性

| 模块 | 功能 |
|------|------|
| 常驻库 | 成员 CRUD、Excel 批量导入、职业/状态筛选、出勤率统计 |
| 出勤库 | 一键导入正式成员、批量导入请假、替补/补人管理、职业缺口分析 |
| 联赛排表 | 拖拽编排 10 队 × 6 人、候选池按职业分组、导入历史排表、自动保存、导出 PNG |
| 录屏审核 | 多局链接提交、审核/批量审核、进度统计、链接脱敏 |
| 数据分析 | CSV 导入、ECharts 8 Tab 可视化（总览/列表/排行榜/阵营对比/小队分析/职业分析/职业深度/综合评分）、16 项衍生指标 |
| 分析调整 | 小队分析内手动分配未排表成员到目标队伍（仅作用于分析视图） |
| 系统配置 | 职业配置、账号管理、帮会管理（开发者专属） |
| 联赛日程 | 日历视图、赛程 CRUD、级联创建/删除、帮众联赛总览 |

## 角色权限

| 角色 | 说明 |
|------|------|
| 开发者 (developer) | 不绑定帮会，可创建帮会、派发账号、删除帮会 |
| 管理员 (admin) | 绑定帮会，拥有帮会内全部功能权限 |
| 帮众 (member) | 绑定帮会，查看出勤/排表/录屏/数据，提交录屏链接 |

## 技术栈

**前端：** Vue 3 + TypeScript + Vite + Element Plus + ECharts + Pinia

**后端：** Python 3.13 + FastAPI + SQLAlchemy + SQLite + Alembic

**部署：** Docker Compose + Nginx

## 快速开始

### 本地开发（Windows）

```bash
# 1. 克隆项目
git clone <repo-url>
cd nsh-management

# 2. 后端
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\alembic upgrade head

# 3. 前端
cd ../frontend
npm install

# 4. 一键启动（回到项目根目录）
cd ..
start.bat
```

启动后访问 http://localhost:5173，首次启动会自动初始化默认账号：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 开发者 | developer | dev123456 |
| 管理员 | admin | admin123 |
| 帮众 | member | member123 |

### Docker 部署

```bash
# 1. 复制环境变量模板并填写
cp .env.example .env
# 编辑 .env，修改 SECRET_KEY 和账号密码

# 2. 构建并启动
docker compose up -d --build

# 3. 访问
# http://your-server-ip
```

详细部署文档见 [DEPLOY.md](DEPLOY.md)。

## 项目结构

```
nsh-management/
├── backend/                    # 后端（FastAPI）
│   ├── app/
│   │   ├── api/v1/             # API 路由
│   │   ├── core/               # 配置、数据库、安全
│   │   ├── models/             # SQLAlchemy 模型（9 表）
│   │   ├── schemas/            # Pydantic Schema
│   │   ├── services/           # 业务逻辑
│   │   └── utils/              # 工具函数
│   ├── alembic/                # 数据库迁移
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/                   # 前端（Vue 3）
│   ├── src/
│   │   ├── api/                # API 封装
│   │   ├── components/         # 业务组件
│   │   ├── views/              # 页面
│   │   ├── composables/        # 组合式函数
│   │   ├── layouts/            # 布局
│   │   ├── stores/             # Pinia 状态
│   │   ├── styles/             # 主题样式
│   │   ├── types/              # TypeScript 类型
│   │   ├── utils/              # 工具函数
│   │   └── router/             # 路由
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
├── DEPLOY.md
└── start.bat                   # Windows 一键启动
```

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | JWT 签名密钥（生产必须修改） | `dev-secret-key-change-in-production` |
| `DEVELOPER_PASSWORD` | 开发者密码（首次建库时生效） | - |
| `ADMIN_PASSWORD` | 管理员密码（可选，不设置则不创建） | - |
| `MEMBER_PASSWORD` | 帮众密码（可选，不设置则不创建） | - |

## 许可证

MIT
