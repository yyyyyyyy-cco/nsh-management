#!/bin/sh
set -e

# 以 root 身份修复 data 目录权限（Docker volume 可能是 root 创建的）
chown -R appuser:appuser /app/data

# 切换到 appuser 执行实际命令
exec gosu appuser "$@"
