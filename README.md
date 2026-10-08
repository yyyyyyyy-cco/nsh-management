# 轻衫都会用的帮会联赛管理系统

> 专为游戏帮会管理人员设计的一体化管理工具，涵盖成员管理、出勤考核、联赛排表、录屏审核和比赛数据分析等核心功能。

> 📘 开发协作规范（分支/提交/发布/tag）见 [GIT-GUIDE.md](GIT-GUIDE.md)。
> 📄 参与贡献与仓库政策：[CONTRIBUTING.md](CONTRIBUTING.md)（协作约定）· [SECURITY.md](SECURITY.md)（漏洞报告）· [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)（行为准则）· [CHANGELOG.md](CHANGELOG.md)（更新日志）。

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

**后端：** Python 3.11（生产镜像基座与 CI；本地 3.11～3.13） + FastAPI + SQLAlchemy + SQLite + Alembic

**部署：** Docker Compose + Nginx

## 快速开始

### 一、本地开发（Windows）

```bash
# 1. 克隆项目
git clone <repo-url>
cd nsh-management

# 2. 后端（Python 3.11 / 3.12 / 3.13，版本不符时下一行会直接报错）
cd backend
python -c "import sys; assert sys.version_info[:2] in [(3,11),(3,12),(3,13)], sys.version"
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\alembic upgrade head

# 3. 前端（Node 20+）
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

> **环境要求**：Python 3.11–3.13（3.14 装不上依赖）、Node 20+；依赖拉取慢/超时或报 SSL 证书错误时**按命令换源**（pip 清华源 / npm npmmirror，不要改全局配置、不要写进仓库）；Python 3.13 需补装 `greenlet`（否则 `alembic upgrade head` 报 `ValueError`）。
> 细节见 [CONTRIBUTING.md](CONTRIBUTING.md) §环境准备。

### 二、服务器部署（Docker Compose）

```bash
# 1. 准备环境变量（必改 SECRET_KEY 与账号密码）
cp .env.example .env

# 2. 构建并启动
docker compose up -d --build

# 3. 检查状态（backend 应为 healthy）
docker compose ps
```

HTTPS/域名、一键更新、备份恢复、日志与故障排查见 [DEPLOY.md](DEPLOY.md)；一键更新脚本模板为 `deploy.sh.example`。

### 本地开发补充

**数据源模式（`DB_MODE`）**：`start.bat` 顶部通过 `DB_MODE` 切换本地启动所用数据库，**默认 `prod`**：

| 模式 | 数据源 | 说明 |
|------|--------|------|
| `prod`（默认） | `backend\data\nsh-server-20260907.db` | 服务器数据**快照副本**，便于用真实数据调试；副本不存在时自动回退到 `dev`。本地的读写只作用于副本，**不会影响生产服务器** |
| `dev` | `backend\data\nsh.db` | 本地开发库；首次启动自动初始化默认账号（见上表） |

> 快照文件需从服务器导出后放入 `backend\data\`（`.gitignore` 已排除 `*.db`，不入库）。只想用本地库时，把 `start.bat` 中的 `set "DB_MODE=prod"` 改为 `dev`。

**测试与静态检查**：

```bash
cd backend
python -m pytest     # 新用例（backend/tests/）+ 既有 selfcheck_*.py；全部使用内存库
ruff check .         # 静态检查（配置见 backend/ruff.toml）
```

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
