@echo off
chcp 65001 >nul
title 帮会联赛管理系统 - 一键启动
cd /d "%~dp0"

set "BACKEND=%~dp0backend"
set "FRONTEND=%~dp0frontend"

REM ===== 数据源切换：prod=生产数据副本（nsh-server-*.db，只读参考）；dev=本地开发库 =====
REM 切换时改下一行即可；副本文件由服务器快照拉取，勿在本地业务操作中依赖它回写生产
set "DB_MODE=prod"

set "DATABASE_URL="
if /i "%DB_MODE%"=="prod" (
    if exist "%BACKEND%\data\nsh-server-20260907.db" (
        set "DATABASE_URL=sqlite+aiosqlite:///%BACKEND:\=/%/data/nsh-server-20260907.db"
    ) else (
        echo [警告] 未找到生产数据副本 backend\data\nsh-server-20260907.db，回退本地开发库
    )
)

if defined DATABASE_URL (
    echo 数据源: 生产数据副本 ^(nsh-server-20260907.db^)
) else (
    echo 数据源: 本地开发库 ^(nsh.db^)
)

REM ===== 步骤1: 数据库迁移（每次启动都执行，确保 Schema 最新）=====
echo [1/4] 正在执行数据库迁移...
pushd "%BACKEND%"
.venv\Scripts\alembic.exe upgrade head
if errorlevel 1 (
    popd
    echo [错误] 数据库迁移失败，请确认已按 README 安装后端依赖
    pause
    exit /b 1
)
popd
echo      数据库迁移完成

REM ===== 首次启动自动初始化账号数据（仅本地开发库；生产副本自带账号，跳过）=====
if not defined DATABASE_URL if not exist "%BACKEND%\data\nsh.db" (
    echo [1/4] 首次启动，正在初始化账号数据...
    pushd "%BACKEND%"
    if not defined DEVELOPER_PASSWORD set "DEVELOPER_PASSWORD=dev123456"
    if not defined ADMIN_PASSWORD set "ADMIN_PASSWORD=admin123"
    if not defined MEMBER_PASSWORD set "MEMBER_PASSWORD=member123"
    .venv\Scripts\python.exe -m app.init_db
    if errorlevel 1 (
        popd
        echo [错误] 初始化账号数据失败
        pause
        exit /b 1
    )
    popd
    echo      账号数据初始化完成
)

REM ===== 步骤2: 启动后端(127.0.0.1:8000,热重载) =====
echo [2/4] 启动后端服务...
cd /d "%BACKEND%"
start "后端-FastAPI :8000" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

REM ===== 步骤3: 等待后端就绪 =====
echo [3/4] 等待后端服务就绪，请稍候...
ping -n 4 127.0.0.1 >nul

REM ===== 步骤4: 启动前端(127.0.0.1:5173) =====
echo [4/4] 启动前端...
cd /d "%FRONTEND%"
start "前端-Vite :5173" cmd /k "npm run dev"

echo.
echo 启动完成!
echo   前端页面:  http://localhost:5173
echo   接口文档:  http://127.0.0.1:8000/docs
echo.
if defined DATABASE_URL (
    echo   当前数据源: 生产数据副本 ^(2026-09-07 快照^)
    echo   登录账号:   使用生产环境的真实账号密码
    echo   注意:       此库为快照副本，本地操作不会影响生产服务器
) else (
    echo   测试账号:
    echo     开发者:  developer / dev123456  ^(创建帮会、派发账号^)
    echo     管理员:  admin / admin123       ^(管理帮会功能^)
    echo     帮众:    member / member123     ^(查看数据、提交录屏^)
)
echo.
echo 关闭方式: 直接关闭弹出的「后端」和「前端」两个窗口即可。
echo.
echo 若登录仍提示"网络错误"，请检查后端窗口是否有报错信息，
echo 或访问 http://127.0.0.1:8000/docs 确认后端是否正常运行。
pause
