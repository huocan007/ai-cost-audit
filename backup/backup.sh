#!/usr/bin/env bash
# backup.sh — 免费异地备份（在 DediRock VPS 上每日 cron 运行）
# 策略：① 打包站点 + 网关配置 + 数据库；② 推到 Cloudflare R2（10GB 免费、出站免费）；
#        ③ 同时 scp 回你本机（零成本兜底）。任一层成功即视为备份完成。
#
# 前置：
#   - rclone 已配置名为 'r2' 的 remote（S3 兼容，指向 Cloudflare R2）
#   - 本机已授权 SSH（用于 scp 回传）
# 用法：
#   chmod +x backup.sh && ./backup.sh
#   crontab -e  ->  0 4 * * * /path/backup.sh >> /var/log/backup.log 2>&1

set -euo pipefail

# ===== 配置（按需修改）=====
BACKUP_DIR="/var/backups/costrouter"
SRC_LANDING="/srv/landing"
SRC_IAC="/opt/costrouter/iac"
R2_REMOTE="r2:costrouter-backup"          # rclone remote:bucket
LOCAL_PULL="yican@YOUR-PC:/d/backups/costrouter"  # 可选：scp 回本机
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
ARCHIVE="$BACKUP_DIR/costrouter-$TIMESTAMP.tar.gz"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] 打包中..."
tar -czf "$ARCHIVE" "$SRC_LANDING" "$SRC_IAC" 2>/dev/null || {
  echo "[$(date)] 警告：部分源不存在，仍继续"
  tar -czf "$ARCHIVE" -C / $(echo "$SRC_LANDING $SRC_IAC" | sed 's#/##') 2>/dev/null || true
}

# 层 1：Cloudflare R2（出站免费，恢复不花钱）
if command -v rclone >/dev/null 2>&1; then
  echo "[$(date)] 同步到 R2..."
  rclone copy "$ARCHIVE" "$R2_REMOTE/" && echo "[$(date)] R2 OK"
fi

# 层 2：scp 回本机（零成本兜底，可选）
if [ -n "${LOCAL_PULL:-}" ]; then
  echo "[$(date)] 回传本机..."
  scp "$ARCHIVE" "$LOCAL_PULL/" && echo "[$(date)] 本机 OK" || echo "[$(date)] 本机回传失败（非致命）"
fi

# 保留最近 14 天本地副本
find "$BACKUP_DIR" -name 'costrouter-*.tar.gz' -mtime +14 -delete
echo "[$(date)] 完成"
