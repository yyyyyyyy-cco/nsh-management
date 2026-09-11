# 逆水寒帮会联赛系统 - 技术栈确认

## 技术选型原则
- **简单**：学习曲线平缓，社区活跃，文档完善
- **健壮**：成熟稳定，类型安全，易于维护
- **高效**：开发效率高，工具链完善

---

## 前端技术栈

| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|---------|
| Vue | 3.x | UI框架 | 渐进式框架，学习曲线平缓，中文文档完善 |
| TypeScript | 5.x | 类型系统 | 类型安全，减少运行时错误 |
| Vite | 5.x | 构建工具 | 快速冷启动，热更新快，Vue官方推荐 |
| Element Plus | 2.x | UI组件库 | Vue3组件库，中文友好，企业级组件 |
| Vue Router | 4.x | 路由管理 | Vue官方路由，支持嵌套路由 |
| Pinia | 2.x | 状态管理 | Vue官方推荐，轻量级，TypeScript友好 |
| Axios | 1.x | HTTP客户端 | 拦截器支持，请求/响应处理方便 |
| vue.draggable.next | 4.x | 拖拽功能 | Vue3拖拽库，支持排序、移动 |
| html2canvas | 1.x | 导出PNG | 将DOM转为Canvas导出图片 |
| xlsx | 0.18.x | Excel解析 | 前端解析Excel文件 |
| dayjs | 1.x | 日期处理 | 轻量级，API兼容moment |
| echarts | 6.x | 图表库 | 数据分析可视化（总览/列表/排行/阵营对比/小队分析/职业深度/评分） |

### 前端项目结构
```
frontend/
├── src/
│   ├── api/              # API请求封装
│   ├── components/       # 通用组件
│   ├── layouts/          # 布局组件
│   ├── views/            # 页面组件
│   ├── stores/           # Pinia状态管理
│   ├── composables/      # 组合式函数
│   ├── utils/            # 工具函数
│   ├── types/            # TypeScript类型定义
│   ├── styles/           # 全局样式
│   ├── router/           # 路由配置
│   └── App.vue
├── index.html
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 后端技术栈

| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|---------|
| Python | 3.13 | 运行环境 | 简单易学，生态丰富 |
| FastAPI | 0.115+ | Web框架 | 现代高性能，自动API文档，类型提示支持 |
| SQLAlchemy | 2.x | ORM | 最流行Python ORM，功能强大，文档完善 |
| SQLite | 3.x | 数据库 | 轻量级，无需额外服务，单文件存储 |
| Pydantic | 2.x | 数据验证 | 类型安全，自动验证，与FastAPI深度集成 |
| python-jose | 3.x | JWT认证 | Token生成和验证 |
| passlib | 1.x | 密码加密 | 支持bcrypt等多种加密算法 |
| python-multipart | 0.x | 文件上传 | 处理multipart/form-data |
| uvicorn | 0.x | ASGI服务器 | 高性能异步服务器 |
| aiosqlite | 0.x | 异步SQLite | 异步数据库驱动 |

### 后端项目结构
```
backend/
├── app/
│   ├── api/              # API路由
│   │   ├── deps.py       # 依赖注入
│   │   └── v1/           # API版本1
│   │       ├── auth.py   # 认证接口
│   │       ├── members.py
│   │       ├── schedules.py
│   │       ├── attendance.py
│   │       ├── lineups.py
│   │       ├── recordings.py
│   │       ├── match_data.py
│   │       ├── squad_adjustments.py  # 分析调整
│   │       ├── developer.py          # 开发者专属路由
│   │       ├── config.py
│   │       └── router.py             # 路由注册
│   ├── core/             # 核心配置
│   │   ├── config.py     # 应用配置
│   │   ├── security.py   # 安全相关
│   │   └── database.py   # 数据库连接
│   ├── models/           # SQLAlchemy模型（10张表）
│   ├── schemas/          # Pydantic数据模式
│   ├── services/         # 业务逻辑层
│   ├── utils/            # 工具函数（attendance_import/excel_import/constants）
│   └── main.py           # 应用入口
├── data/                 # SQLite数据库文件目录
├── scripts/              # 工具脚本（generate_import_template/selfcheck_indicators）
├── templates/            # Excel模板
├── alembic/              # 数据库迁移（13个版本）
├── alembic.ini
├── requirements.txt
└── pyproject.toml
```

### requirements.txt
```
fastapi>=0.115.0
uvicorn[standard]==0.27.1
sqlalchemy==2.0.36
aiosqlite==0.20.0
pydantic==2.11.4
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.0.1
python-multipart>=0.0.18
openpyxl==3.1.5
alembic==1.13.1
```
> 版本说明（2026-08 实际验证）：适配 Python 3.13。pydantic≥2.10、SQLAlchemy≥2.0.36 才有 Python 3.13 预编译包；bcrypt 固定 4.0.1 以兼容 passlib 1.7.4（≥4.1 会报错）；fastapi 升级到 0.115+；openpyxl 用于 Excel 导入导出；python-multipart 升级修复 CVE-2024-53981。

---

## 数据库

| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|---------|
| SQLite | 3.x | 主数据库 | 轻量级，无需额外服务，单文件存储，适合中小型应用 |
| SQLAlchemy | 2.x | ORM | 功能强大，支持异步，迁移方便 |
| Alembic | 1.x | 数据库迁移 | SQLAlchemy官方迁移工具 |

### SQLite优势
- **零配置**：无需安装和配置数据库服务
- **单文件存储**：整个数据库就是一个文件，便于备份和迁移
- **性能足够**：对于帮会管理系统（预计几十到几百用户）完全够用
- **可靠性高**：经过20多年验证，非常稳定

### 数据库设计
- 使用SQLAlchemy定义数据模型
- 使用Pydantic进行数据验证
- 使用Alembic管理数据库迁移
- 数据库文件存储在 `data/nsh.db`

---

## 部署方案

| 技术 | 用途 | 选择理由 |
|------|------|---------|
| Docker | 容器化 | 环境一致性，便于部署和迁移 |
| Docker Compose | 容器编排 | 简单的多容器管理 |
| Nginx | 反向代理 | 高性能，静态资源服务，负载均衡 |

### 部署架构
```
┌─────────────────────────────────────────────────────────┐
│                      云服务器                            │
│  ┌─────────────────────────────────────────────────┐    │
│  │               Nginx（前端容器内）                 │    │
│  │  - 静态资源服务（前端打包文件）                    │    │
│  │  - 反向代理（/api → 后端服务:8000）               │    │
│  │  - HTTPS 终止（SSL 证书）                        │    │
│  │  - SPA 回退（try_files $uri /index.html）        │    │
│  │  - 上传限制 20MB（client_max_body_size）         │    │
│  └─────────────────────────────────────────────────┘    │
│                          │                               │
│          ┌───────────────┴───────────────┐               │
│          │                               │               │
│  ┌───────▼───────┐               ┌──────▼──────┐        │
│  │   前端容器     │               │  后端容器    │        │
│  │  (Nginx:80)   │               │  (FastAPI    │        │
│  │               │               │   :8000)     │        │
│  └───────────────┘               └─────────────┘        │
│                                     │                    │
│                               ┌─────▼─────┐             │
│                               │ data/     │             │
│                               │ nsh.db    │             │
│                               └───────────┘             │
└─────────────────────────────────────────────────────────┘
```

### Docker Compose 配置
实际配置见项目根目录 `docker-compose.yml`，关键特性：
- **前端容器**：多阶段构建（npm build → Nginx 静态托管），端口 80，依赖后端健康检查
- **后端容器**：多阶段构建（pip install → uvicorn），端口 8000，SQLite 数据卷持久化
- **数据卷**：`./data:/app/data`（SQLite 数据库持久化）
- **健康检查**：后端 `/api/v1/auth/me` 健康探针，前端 depends_on 等待后端就绪
- **环境变量**：通过 `.env` 文件注入（SECRET_KEY、DEVELOPER_PASSWORD、ADMIN_PASSWORD、MEMBER_PASSWORD）
- **启动脚本**：`deploy.sh`（Linux 一键部署）、`start.bat`（Windows 本地开发）

---

## 开发工具

| 工具 | 用途 |
|------|------|
| ESLint | 前端代码规范检查 |
| Prettier | 前端代码格式化 |
| Ruff | Python代码规范检查和格式化 |
| Git | 版本控制 |
| VS Code | 推荐IDE |

### VS Code推荐插件
- ESLint
- Prettier
- Volar (Vue官方插件)
- Python
- Pylance
- SQLite Viewer

---

## 包管理

| 工具 | 用途 | 选择理由 |
|------|------|---------|
| pnpm | 前端包管理 | 速度快，磁盘占用小 |
| pip / uv | Python包管理 | Python标准包管理，uv更快 |

---

## 技术栈总结

```
前端：Vue 3 + TypeScript + Vite + Element Plus + ECharts 6 + Pinia
后端：Python 3.13 + FastAPI + SQLAlchemy + SQLite
部署：Docker + Docker Compose + Nginx
```

### 选择这套技术栈的优势

1. **简单易学**：Vue3和Python学习曲线平缓，中文文档完善
2. **开发效率高**：Vite热更新快，FastAPI自动API文档
3. **部署简单**：SQLite无需额外服务，Docker容器化
4. **维护成本低**：SQLite单文件备份，无需数据库管理员
5. **性能足够**：对于帮会管理系统完全够用
6. **成本低**：全部开源，无授权费用，无需额外数据库服务

### 适用场景
- 中小型应用（用户数 < 1000）
- 单服务器部署
- 数据量适中（百万级记录以内）
- 对数据库并发要求不高

---

## 可选替代方案

如果未来需要扩展，以下是可选替代方案：

| 组件 | 当前选择 | 替代方案 | 替代理由 |
|------|---------|---------|---------|
| 前端框架 | Vue 3 | React 18 | 如果团队更熟悉React |
| UI组件库 | Element Plus | Ant Design / Naive UI | 根据设计需求选择 |
| 状态管理 | Pinia | Vuex 4 | 如果需要更严格的状态管理 |
| 数据库 | SQLite | PostgreSQL | 如果需要更高并发或更大数据量 |
| ORM | SQLAlchemy | Tortoise ORM | 如果需要纯异步ORM |
| Web框架 | FastAPI | Flask | 如果不需要异步支持 |

---

## 迁移路径

如果未来业务增长，需要从SQLite迁移到PostgreSQL：

1. **数据库迁移**：使用Alembic生成迁移脚本
2. **修改配置**：更改DATABASE_URL连接字符串
3. **安装驱动**：从aiosqlite切换到asyncpg
4. **代码修改**：SQLAlchemy代码基本无需修改

SQLAlchemy的抽象层使得数据库切换成本很低。
