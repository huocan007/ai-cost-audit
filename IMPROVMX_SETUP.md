# ImprovMX 域名邮箱转发配置：hello@acan.ccwu.cc → 私人邮箱

## 为什么用 ImprovMX 而不是 Zoho
Zoho 国际版个人注册在美国 IP 下强制 `+1` 国家码、中国手机号收不到验证短信，
且要填公司名——对 solo 用户摩擦大。ImprovMX 专门做域名邮箱转发：
- 免费版：1 个域名、无限别名、**无需手机号、无需公司名**
- 只加 2 条 MX + 1 条 SPF 即可，30 秒注册
- 2016 年起运营，转发通常 5 秒内完成，可靠性好
- 客户看到 `hello@acan.ccwu.cc`（专业），实际收信进私人邮箱（不暴露私人地址）

> 与落地页主通道 Web3Forms 表单并行：表单让客户不看到任何邮箱；本域名邮箱作书面/备选联系。

## 操作步骤

### Step 1 — 注册 ImprovMX
1. 打开 https://improvmx.com/
2. 用**你的私人邮箱**登录/注册（这邮箱就是最终收件箱，例如 Gmail/QQ 邮箱）

### Step 2 — 添加域名
1. 后台点 **Add a domain**
2. 填 `acan.ccwu.cc`
3. 页面会显示要加的 MX 与 SPF 记录（以页面显示为准，通用值见下）

### Step 3 — 在 DNSHE 添加 DNS 记录
删除该域名下**所有旧的 MX 记录**，然后加：
| 类型 | 主机 | 记录值 | 优先级 |
|---|---|---|---|
| MX | `@` | `mx1.improvmx.com` | 10 |
| MX | `@` | `mx2.improvmx.com` | 20 |
| TXT | `@` | `v=spf1 include:spf.improvmx.com ~all` | — |

> 若 DNSHE 把 `acan.ccwu.cc` 当作 `ccwu.cc` 域下的**子域**管理，则「主机」填 `acan` 而非 `@`。
> 若已有 SPF TXT 记录，不要新建第二条，改为把 `include:spf.improvmx.com` 合并进现有值。

### Step 4 — 添加转发别名
回到 ImprovMX 后台 → **Aliases** → 添加：
- 自定义地址：`hello@acan.ccwu.cc`
- 转发到：你的私人邮箱

### Step 5 — 验证
1. 用另一个邮箱（Gmail）发测试信到 `hello@acan.ccwu.cc`
2. 约 5 秒–几分钟内，信应出现在你的私人收件箱
3. ImprovMX 后台域名状态显示 "Email forwarding active" 即成功

## 限制（先知晓）
- **免费版只能收信转发，不能从 `hello@` 发信**。回复客户时若用私人邮箱回，对方看到私人地址（与 Zoho 转发模式一致）。
- 要「以 `hello@` 身份发信」需升级付费（ImprovMX SMTP 中继，约 $9/月）。冷启动阶段不必，先收询盘为主。
- 不影响网站：MX 只管邮件，A/CNAME（落地页）记录不动。
- DNS 生效通常几分钟到 24 小时。

## 与 Zoho 方案的关系
`ZOHO_MAIL_SETUP.md` 仍可作为「需要完整收发+网页邮箱」时的备选（Zoho 免费版含 5GB 网页邮箱、可发信），
但因注册需手机验证、对当前美国 IP + 中国手机号组合不友好，本文件（ImprovMX）作为**首选零摩擦路径**。
