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
| dayjs | 1.x | 日期处理 | 轻量级，API兼容moment |
| echarts | 6.x | 图表库 | 数据分析可视化（总览/列表/排行/阵营对比/小队分析/职业深度/评分） |

### 前端项目结构

> **权威源**：`progress.md`（完整代码目录树）。`src/` 分层：api / components / layouts / views / stores / composables / utils / types / styles / router。

---

## 后端技术栈

| 技术 | 版本 | 用途 | 选择理由 |
|------|------|------|---------|
| Python | 3.11 | 运行环境 | 生产镜像基座（`python:3.11-slim`）与 CI 均为 3.11；本地 3.11–3.13 可用（3.14 暂无 `pydantic-core` wheel） |
| FastAPI | 0.142.2（锁定） | Web框架 | 现代高性能，自动API文档，类型提示支持 |
| SQLAlchemy | 2.x | ORM | 最流行Python ORM，功能强大，文档完善 |
| SQLite | 3.x | 数据库 | 轻量级，无需额外服务，单文件存储 |
| Pydantic | 2.x | 数据验证 | 类型安全，自动验证，与FastAPI深度集成 |
| python-jose | 3.x | JWT认证 | Token生成和验证 |
| passlib | 1.x | 密码加密 | 支持bcrypt等多种加密算法 |
| python-multipart | 0.x | 文件上传 | 处理multipart/form-data |
| uvicorn | 0.x | ASGI服务器 | 高性能异步服务器 |
| aiosqlite | 0.x | 异步SQLite | 异步数据库驱动 |
| openpyxl | 3.1.5 | Excel 导入导出 | 成员模板解析与成员导出 |
| Pillow | 11.x | 图片导出 | 常驻库导出图片 |

### 后端项目结构

> **权威源**：`progress.md`（完整代码目录树）。`app/` 分层：api（v1 路由）/ core / models / schemas / services / utils / init_db.py / main.py。

### 依赖清单

> **权威源**：`backend/requirements.txt`（运行时依赖，实际锁定版本，含 bcrypt 固定 4.0.1 等说明）；开发/CI 依赖见 `backend/requirements-dev.txt`（ruff、pytest、httpx）。
>
> **编码声明（2026-10-02）**：两个依赖清单首行均为 `# -*- coding: utf-8 -*-`——文件含中文注释，中文 Windows 的 pip 按 cp936 解码会失败（`UnicodeDecodeError`），新增中文内容时**勿删除该行**。
> **锁定状态（2026-10-02，W1-4）**：`fastapi` 由 `>=0.115.0` 改为 **`==0.142.2`**、`python-multipart` 由 `>=0.0.18` 改为 **`==0.0.32`**，并显式锁定传递引入的 **`starlette==1.7.0`**——三者均为**本仓已实测通过**的组合（pytest 93 用例 + selfcheck 全绿；PyPI 元数据 `requires_python >=3.10`，与 3.11 基座兼容）。范围约束的漂移风险与实测证据见合规化计划 F-15；门禁 `scripts/check_requirements_pins.py` 已接入 CI，阻止再次引入范围约束。
> **仍待完成**：带**哈希**的全量锁文件（`pip-compile` / `uv pip compile`）必须在**部署所用 Python（3.11）**环境生成，否则会锁到 cp312 等错误 wheel；本机无 3.11，故未生成——列入 W1-4 收尾。

> 版本说明（2026-10-02 复核，按代码事实）：**运行时以 Python 3.11 为准**（生产镜像基座与 CI 一致；本地开发 3.11–3.13 可用）。pydantic / SQLAlchemy 固定版本均有对应 wheel；bcrypt 固定 4.0.1 以兼容 passlib 1.7.4（≥4.1 会报错）；fastapi 锁定 0.142.2；openpyxl 用于 Excel 导入导出；python-multipart 锁定 0.0.32（修复 CVE-2024-53981）。

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
- 数据库文件存储在 `backend/data/nsh.db`

---

## 部署方案

| 技术 | 用途 | 选择理由 |
|------|------|---------|
| Docker | 容器化 | 环境一致性，便于部署和迁移 |
| Docker Compose | 容器编排 | 简单的多容器管理 |
| Nginx | 反向代理 | 高性能，静态资源服务，负载均衡 |

### 部署架构

> **权威源**：[`DEPLOY.md`](../DEPLOY.md)（生产架构、日常更新流程、日志、备份与恢复、常见问题）。本节仅保留摘要，不复制其内容。

生产为**单层 TLS**（2026-09-15 改造）：同机全局 `nginx-proxy` 容器是**唯一 TLS 终止点**——证书、限流（API 20r/s、登录 5r/m）、安全响应头、HTTP→HTTPS 跳转、默认 server 兜底全部只在这一层；本项目 frontend 容器退化为「静态资源 + `/api` 反代」，容器内明文 `:80`、**不映射宿主端口**、不挂载证书；backend 容器为内网 FastAPI `:8000`，以非 root（`gosu appuser`）运行，SQLite 数据落在命名卷 `nsh-data`（WAL 模式）。

### Docker Compose 配置

> 实际配置见项目根目录 `docker-compose.yml`。注意：**仓库内该文件是「本地/单机演示拓扑」**（frontend 映射 80/443 并挂载证书），生产服务器版本与之不同（frontend 无宿主端口 + `proxy-net` 外部网络），且服务器配置类文件按 `DEPLOY.md` §三 规则单独维护。

- **前端容器**：多阶段构建（`npm run build:only` → Nginx 静态托管，类型检查在本地/CI 执行）；生产**不映射宿主端口**，由边缘反代回源；依赖后端健康检查
- **后端容器**：**单阶段**构建（`pip install` → uvicorn，见 `backend/Dockerfile`）；`:8000` 仅容器网络可达；SQLite 数据卷持久化
- **数据卷**：命名卷 `nsh-data:/app/data`（SQLite，WAL 模式）与 `nsh-logs:/app/logs`（文件日志，`RotatingFileHandler` 10MB×5）
- **健康检查**：后端根路径 `/` 探活（Python urllib），前端 `depends_on` 等待 `service_healthy`
- **环境变量**：通过 `.env` 注入（`SECRET_KEY`、`DEVELOPER_PASSWORD`、`ADMIN_PASSWORD`、`MEMBER_PASSWORD`；`docker-compose.yml` 已固定 `APP_ENV=production`）
- **本地开发**：`start.bat`（Windows 一键启动，含 `DB_MODE` 数据源切换，见 `README.md`）
- **一键部署**：本地 `deploy.sh` 打包上传后 `docker compose up -d --build`；该脚本**不入库**（含服务器 IP/凭据），模板化与配置漂移治理见 [`.agent/plans/compliance-remediation-plan.md`](../.agent/plans/compliance-remediation-plan.md) 的 W1-2 / W1-3

---

## 开发工具

| 工具 | 用途 |
|------|------|
| Git | 版本控制 |
| VS Code | 推荐 IDE |
| vue-tsc | 前端类型检查（`npm run build` 前置） |
| pytest | 后端测试（`backend/tests/` 新用例 + 既有 `backend/scripts/selfcheck_*.py`；内存库，配置见 `backend/pytest.ini`） |
| Vitest 3 | 前端单元测试（`frontend/src/**/*.spec.ts`，jsdom 环境，配置见 `frontend/vitest.config.ts`；`npm run test`）。**版本须为 3.x**：5.x 的 peer 要求 `vite ≥6.4`，与项目固定的 vite 5.4 冲突 |
| Ruff 0.12 | 后端 Python 静态检查（配置 `backend/ruff.toml`，依赖见 `backend/requirements-dev.txt`，CI 门禁） |
| ESLint 10 + Prettier 3 | 前端静态检查与格式化（配置 `frontend/eslint.config.js`、`frontend/.prettierrc.json`；`npm run lint` / `format`，CI 门禁） |

> **2026-10-02 更新（合规化计划 W2-3）**：**后端 Ruff 与前端 ESLint 10 + Prettier 3 均已配置并接入 CI**——后端 `ruff check .` 通过；前端 `npm run lint` 为 **0 error / 10 warning**（10 处 `vue/no-mutating-props` 降级为 warn，属既有架构债，见计划 W2-8）、`npm run build`（vue-tsc + vite）通过。**待收紧**：`E501` 行长、`ruff format`、`I`/`UP`/`B` 规则、vue `flat/recommended` 排版规则与 Prettier 一次性格式化；后端 mypy 尚未引入。

### VS Code推荐插件
- Volar (Vue官方插件)
- Python
- Pylance
- SQLite Viewer

---

## 包管理

| 工具 | 用途 | 选择理由 |
|------|------|---------|
| npm | 前端包管理 | 随 Node 提供，仓库使用 package-lock.json 锁版本 |
| pip + venv | Python包管理 | 随 Python 提供；uv 为可选加速方案（未启用） |

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
