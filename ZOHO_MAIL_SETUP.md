# Zoho Mail 免费版配置：hello@acan.ccwu.cc → 私人邮箱

> ⚠️ **实操结论（2026-07-26）**：Zoho 国际版个人注册在美国 IP 下强制 `+1` 国家码、
> 中国手机号收不到验证短信，且要填公司名——对 solo 用户摩擦大。
> **零摩擦首选请改用 `IMPROVMX_SETUP.md`**（无需手机/公司名，仅 2 条 MX + SPF）。
> 本文件保留为「需要完整网页邮箱 + 能发信」时的备选方案。

## 目标
用 Zoho Mail 免费版给域名 `acan.ccwu.cc` 开通专业邮箱 `hello@acan.ccwu.cc`，
并把来信转发到私人邮箱（或直接在 Zoho 收），让西方客户看到正规域名邮箱、实际收信仍在你手里。

## 选型：国际版 zoho.com（推荐）vs 中国版 zoho.com.cn
- 业务面向西方客户 → 选 **国际版 zoho.com**（数据中心在海外，Gmail/Outlook 送达信任更好）。
- MX 记录值（国际版）：`mx.zoho.com` / `mx2.zoho.com` / `mx3.zoho.com`（不带 .cn）。
- 注册/日常登录需能访问 zoho.com（国内网络可能偏慢，必要时走海外 VPS 浏览器）。
- 中国版 zoho.com.cn 需手机号实名、数据在境内，对国际送达略差，不作首选。
- ⚠️ 不同数据中心 MX 主机名可能微调，最终以 Zoho Admin Console 显示值为准。

## 免费版权益（已核 2026-07）
- 最多 5 个用户、每用户 5GB 存储、单域名托管、25MB 附件
- Web 网页 + 免费移动 App 收发
- **不含 IMAP/POP/ActiveSync**（免费版限制，只能用网页/App，不能绑 Outlook 桌面客户端）
- 无广告、GDPR 合规

## 前置条件
- 能登录 DNSHE 后台管理 `acan.ccwu.cc` 的解析记录（NS 指向 DNSHE 且你是权威 DNS）
- 一个能接收验证邮件/短信的账号（注册用；若在美国 IP 下需美国手机号或换中国 IP 注册）

## 操作步骤

### Step 1 — 注册 Zoho（国际版）
1. 浏览器打开 https://www.zoho.com/mail/ → 点 **Sign Up** / **Sign Up Free**
2. 选 **Forever Free**（永久免费）计划
3. 填：组织名（随意）、登录邮箱（你的私人邮箱）、**域名填 `acan.ccwu.cc`**
4. 国家码：在中国 IP 下为 `+86`；美国 IP 下锁 `+1`（需对应国家手机号收验证码）

### Step 2 — 验证域名所有权（TXT）
1. Zoho Admin Console → **Domains** → **Add domain** → 填 `acan.ccwu.cc`
2. Zoho 给一条验证 TXT，形如 `zoho-verification=xxxxxxxx`
3. DNSHE → `acan.ccwu.cc` 的「解析 / 记录管理」→ 添加 TXT（主机 `@`，值粘贴该串）
4. 回 Zoho 点 **Verify**（DNS 生效通常 5–30 分钟）

### Step 3 — 在 DNSHE 添加 MX 记录（关键）
删除该域名下**所有旧的 MX 记录**，加三条：
| 类型 | 主机 | 记录值 | 优先级 |
|---|---|---|---|
| MX | @ | `mx.zoho.com` | 10 |
| MX | @ | `mx2.zoho.com` | 20 |
| MX | @ | `mx3.zoho.com` | 50 |

> 若 DNSHE 把 `acan.ccwu.cc` 当作 `ccwu.cc` 域下的子域管理，则「主机」填 `acan` 而非 `@`。

### Step 4 — 添加 SPF 与 DKIM
- **SPF**（TXT，主机 `@`，值）：`v=spf1 include:zoho.com ~all`
- **DKIM**：Zoho Admin Console → Domains → Email Configuration → **DKIM** → 生成密钥，
  把 `zoho._domainkey` 主机 + TXT 值填到 DNSHE（同为 TXT 记录）。
- 若已有 SPF TXT，不要新建第二条，改为**合并**到一条。

### Step 5 — 创建邮箱用户
Zoho Admin Console → **Users** → **Add User**：邮箱 `hello@acan.ccwu.cc`、姓名/密码自定。

### Step 6 — 收信方式二选一
- **方案 A（推荐）**：直接登录 Zoho 网页/App 以 `hello@` 收信（发信身份即 `hello@`，零暴露）。
- **方案 B（转发到私人邮箱）**：Zoho Mail → 设置 → **邮件转发 / Email Forwarding** →
  添加私人邮箱并验证 → 启用。⚠️ 部分数据中心免费版**不含外部转发**选项，无则退回方案 A。

### Step 7 — 验证收发
1. 用 Gmail 发测试信到 `hello@acan.ccwu.cc`
2. 等 5–30 分钟，到 Zoho 网页（A）或私人邮箱（B）查收
3. 用 `hello@` 身份回一封，确认对方收到且发件人显示为 `hello@acan.ccwu.cc`

## 重要提醒
- **不影响网站**：MX 只管邮件，A/CNAME（落地页）记录不动。
- **生效时间**：DNS 全球生效 1–24 小时；Zoho 后台每个记录显示 "Configured" 才算就绪。
- **回复别暴露私人地址**：若用方案 B 转发收信，回信请在 Zoho 网页以 `hello@` 发。
- **与 Web3Forms 关系**：落地页主通道仍是 Web3Forms 表单（客户不看到邮箱）；本域名邮箱作书面/备选联系。
- **MX 与 Cloudflare**：若 `acan.ccwu.cc` 走 Cloudflare 橙色代理，邮件 MX 须在**权威 DNS（DNSHE）**设置。

## 排错
- 验证失败 → 等 DNS 传播，TXT 值一字不差
- 收不到信 → 查 MX 三条是否齐全、旧 MX 是否删干净
- 进垃圾箱 → 确认 SPF/DKIM 已加且生效
