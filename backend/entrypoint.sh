#!/bin/sh
set -e

# 以 root 身份修复数据与日志目录权限（Docker volume 可能是 root 创建的）
mkdir -p /app/data /app/logs
chown -R appuser:appuser /app/data /app/logs

# 切换到 appuser 执行实际命令
exec gosu appuser "$@"
