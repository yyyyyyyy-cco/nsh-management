@echo off
chcp 65001 >nul
title 帮会联赛管理系统 - 一键启动
cd /d "%~dp0"

set "BACKEND=%~dp0backend"
set "FRONTEND=%~dp0frontend"

REM ===== 首次启动自动建库(检测 data\nsh.db 是否存在) =====
if not exist "%BACKEND%\data\nsh.db" (
    echo [1/3] 首次启动,正在初始化数据库...
    pushd "%BACKEND%"
    .venv\Scripts\alembic.exe upgrade head
    if errorlevel 1 (
        popd
        echo [错误] 数据库迁移失败,请确认已按 README 安装后端依赖
        pause
        exit /b 1
    )
    .venv\Scripts\python.exe -m app.init_db
    popd
    echo      数据库初始化完成
)

REM ===== 启动后端(127.0.0.1:8000,热重载) =====
echo [2/3] 启动后端服务...
cd /d "%BACKEND%"
start "后端-FastAPI :8000" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

REM ===== 启动前端(127.0.0.1:5173) =====
echo [3/3] 启动前端...
cd /d "%FRONTEND%"
start "前端-Vite :5173" cmd /k "npm run dev"

echo.
echo 启动完成!
echo   前端页面:  http://localhost:5173
echo   接口文档:  http://127.0.0.1:8000/docs
echo   测试账号:  admin / admin123(管理员)  member / member123(帮众)
echo.
echo 关闭方式:直接关闭弹出的「后端」和「前端」两个窗口即可。
pause
