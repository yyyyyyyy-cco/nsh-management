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
| 个人战绩 | 按游戏 ID 查询历史比赛数据（单局指标与排名、个人概览） |
| 系统日志 | 操作审计日志查询/统计/清理（仅开发者，写操作自动落库） |
| 联赛日程 | 日历视图、赛程 CRUD、级联创建/删除、帮众联赛总览 |

## 角色权限

| 角色 | 说明 |
|------|------|
| 开发者 (developer) | 不绑定帮会，可创建帮会、派发账号、删除帮会 |
| 管理员 (admin) | 绑定帮会，拥有帮会内全部功能权限 |
| 帮众 (member) | 绑定帮会，录屏上传、个人战绩、联赛日程（详情只读），提交录屏链接 |

## 技术栈

**前端：** Vue 3 + TypeScript + Vite + Element Plus + ECharts 6 + Pinia

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

> **安装排错（2026-10-02 补充）**：若 `pip install` 报 SSL 证书错误（企业代理/自签证书环境），可改用与镜像构建相同的镜像源：
> `pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com`。
> 另注意：`requirements.txt` 与 `requirements-dev.txt` 首行声明了 `# -*- coding: utf-8 -*-`——文件含中文注释，中文 Windows（cp936）下 pip 缺少编码声明会解码失败（`UnicodeDecodeError`），**新增内容时请勿删除该行**。

### 后端测试与静态检查

```bash
cd backend
python -m pytest     # 新用例（backend/tests/）+ 既有 selfcheck_*.py；全部使用内存库
ruff check .         # 静态检查（配置见 backend/ruff.toml）
```

启动后访问 http://localhost:5173，首次启动会自动初始化默认账号：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 开发者 | developer | dev123456 |
| 管理员 | admin | admin123 |
| 帮众 | member | member123 |

### 数据源模式（`DB_MODE`，仅本地开发）

`start.bat` 顶部通过 `DB_MODE` 切换本地启动所用数据库，**默认 `prod`**：

| 模式 | 数据源 | 说明 |
|------|--------|------|
| `prod`（默认） | `backend\data\nsh-server-20260907.db` | 服务器数据**快照副本**，便于用真实数据调试；副本不存在时自动回退到 `dev`。本地的读写只作用于副本，**不会影响生产服务器** |
| `dev` | `backend\data\nsh.db` | 本地开发库；首次启动自动初始化默认账号（见上表） |

> 快照文件需从服务器导出后放入 `backend\data\`（`.gitignore` 已排除 `*.db`，不入库）。只想用本地库时，把 `start.bat` 中的 `set "DB_MODE=prod"` 改为 `dev`。

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

> 前端镜像构建依赖仓库内的 `frontend/nginx.conf`（占位符版，2026-10-02 起入库）——该文件缺失时 `docker compose up -d --build` 会在 `COPY nginx.conf` 一步失败。生产服务器的实际 nginx 配置与之不同，按 [DEPLOY.md](DEPLOY.md) §三 单独维护（`deploy.sh` 排除清单仍排除该文件，避免本地占位符版覆盖服务器）。
> 一键部署脚本模板为 `deploy.sh.example`（复制为 `deploy.sh` 并填写服务器占位符后使用）。

详细部署文档见 [DEPLOY.md](DEPLOY.md)。

## 项目结构

> 代码目录树的**唯一权威源**是 [`memory-bank/progress.md`](memory-bank/progress.md)（`AGENTS.md` §2.1 约定「不复制，引用」）；
> 文档索引与文档目录树见 [`memory-bank/architecture.md`](memory-bank/architecture.md)。
> 本文件不再重复维护目录树，避免多份副本漂移（历史教训见 `memory-bank/ai-checklist.md`）。

## 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `SECRET_KEY` | JWT 签名密钥（生产必须修改；推荐 `openssl rand -hex 32`） | `dev-secret-key-change-in-production` |
| `APP_ENV` | 运行环境标识（`production`/`prod` 或 `development`/`dev`/`test`；docker-compose.yml 已固定 production） | 未声明时以容器特征兜底 |
| `DEVELOPER_PASSWORD` | 开发者密码（首次建库时生效） | - |
| `ADMIN_PASSWORD` | 管理员密码（可选，不设置则不创建） | - |
| `MEMBER_PASSWORD` | 帮众密码（可选，不设置则不创建） | - |

> 安全门禁：容器/生产环境（`APP_ENV=production`）下，弱密钥（模板占位值、<32 字符、
> 含项目名/单词/年份等可猜片段）将拒绝启动；本地开发仅告警放行。详见 `DEPLOY.md` §六。

## 许可证

MIT
