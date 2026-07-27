# REDEPLOY.md — 30 分钟重建手册

目标：DediRock（或任意一家 VPS）意外宕机 / 被墙 / 跑路时，能在 **30 分钟内** 在另一家供应商重建整套服务。

> 核心思路：代码 / 配置 / 部署脚本全在 Git + 本仓库；数据在免费异地备份（R2 / 本机）。
> 换供应商 = 改 DNS 指向，零锁定。

## 前置（一次性准备）
1. 本仓库已推到 GitHub 私有库（代码 = 第二地点）。
2. Cloudflare R2（10GB 免费）已建 bucket，rclone 已配 `r2` remote。
3. 域名 `acan.ccwu.cc` 的子域（如 `ai.acan.ccwu.cc`）已可在新 VPS 上重新解析。

## 重建步骤（在新 VPS 上）
```bash
# 1. 装依赖（Debian/Ubuntu）
sudo apt update && sudo apt install -y docker.io docker-compose-plugin rclone

# 2. 取代码
git clone git@github.com:YOURNAME/cost-arbitrage-stack.git
cd cost-arbitrage-stack/iac

# 3. 填密钥
cp .env.example .env && nano .env   # 填入 DEEPSEEK/QWEN/OPENAI key + DOMAIN

# 4. 起网关 + 反向代理
docker compose up -d

# 5. 恢复数据（从 R2 或本机备份）
rclone copy r2:costrouter-backup/latest.tar.gz /tmp/
tar -xzf /tmp/latest.tar.gz -C /

# 6. 解析域名
#   在新 VPS 控制台把 ai.acan.ccwu.cc A 记录指向新 IP；
#   Caddy 会自动申请 SSL（约 1 分钟）。

# 7. 验证
curl -X POST https://ai.acan.ccwu.cc/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"hi"}]}'
```

## 第二家冷备（营收后启用）
- 拿到首笔客户款后，花 $5–10/月开一台 RackNerd 或试试 Oracle Cloud Always-Free（4 ARM 核 / 24G / 10TB）。
- 平时只同步备份；出事直接改 DNS，无需长期双跑。

## 自检清单
- [ ] 代码在 GitHub 私有库
- [ ] 每晚备份到 R2 + 本机（backup/backup.sh 已 cron）
- [ ] 新 VPS 能 30 分钟内跑通上面 7 步
- [ ] 域名解析权在自己手里（acan.ccwu.cc）
