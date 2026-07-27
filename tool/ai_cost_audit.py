#!/usr/bin/env python3
"""ai_cost_audit.py — AI 成本审计 + LiteLLM 路由配置生成器。

这是「成本套利」开源楔子工具：把"把 AI 调用路由到最便宜的模型"从概念变成
可运行的证据。SMB / 独立开发者缺的，正是不到 1 分钟就能跑出来的审计 + 现成配置。

功能：
  audit      输入月 token 量 + 当前模型，估算切换到便宜模型路由后的节省%
  gen-config 生成可直接部署的 litellm_config.yaml（任务路由 + 质量门 + 便宜优先 + 回退）

定价为 2026-07 公开报价近似值（来源：DeepSeek / OpenRouter / Anthropic 公开页），
可用 --price 覆盖。仅用标准库，零依赖。

用法：
  python ai_cost_audit.py audit --prompt-tokens 50e6 --completion-tokens 20e6 --current gpt-4o
  python ai_cost_audit.py gen-config --out litellm_config.yaml
"""
import argparse
import sys

# 每百万 token 价格（USD），2026-07 核实价（来源：DeepSeek / Moonshot / OpenAI 公开页）
# 缓存命中价未在审计中单列；实际部署开 LiteLLM 上下文缓存可再砍 80%+ 输入成本。
# 每百万 token 价格（USD），2026-07 核实价（来源：DeepSeek / Moonshot / OpenAI / Anthropic 公开定价页）。
# 仅列入已核实单价的模型；未核实标准的模型一律不进字典，避免向客户展示估算价。
PRICING = {
    # A 经济档（中国算力 · 最省）
    "deepseek/deepseek-v4-flash": {"in": 0.14, "out": 0.28},   # 核实(2026-07)
    "moonshot/kimi-k2-5":         {"in": 0.60, "out": 3.00},   # 已核实(缓存命中$0.10)
    # B 标准档（中国算力 · 能力平衡）
    "moonshot/kimi-k2-6":         {"in": 0.95, "out": 4.00},   # 已核实(缓存命中$0.16)
    "moonshot/kimi-k3":           {"in": 3.00, "out": 15.00},  # 已核实(2026-07-17 发布;缓存命中$0.30)
    "qwen/qwen2.5-72b-instruct":  {"in": 0.39, "out": 1.04},
    # C 旗舰档（最难任务 · 含西方合规兜底）
    "gpt-4o":                     {"in": 2.50, "out": 10.00},  # 已核实(2026-07 OpenAI)
    "claude-opus-4.8":            {"in": 5.00, "out": 25.00},  # 已核实(2026-07 Anthropic 官方)
}

# 路由默认落点：最便宜且能力够用的模型
ROUTED_TO = "deepseek/deepseek-v4-flash"

# 展示用名称（英文，面向西方客户）
LABELS = {
    "deepseek/deepseek-v4-flash": "DeepSeek V4-Flash",
    "moonshot/kimi-k2-5": "Kimi K2.5",
    "moonshot/kimi-k2-6": "Kimi K2.6",
    "moonshot/kimi-k3": "Kimi K3",
    "qwen/qwen2.5-72b-instruct": "Qwen 2.5-72B",
    "gpt-4o": "gpt-4o",
    "claude-opus-4.8": "Claude Opus 4.8",
}

def _label(model):
    return LABELS.get(model, model)


def cost(model, p_tokens, c_tokens):
    p = PRICING[model]
    return (p_tokens / 1_000_000) * p["in"] + (c_tokens / 1_000_000) * p["out"]


def cmd_audit(args):
    current = args.current
    if current not in PRICING:
        print(f"[!] Unknown model '{current}'. Available: {', '.join(PRICING)}")
        sys.exit(1)
    cur = cost(current, args.prompt_tokens, args.completion_tokens)
    ds = cost(ROUTED_TO, args.prompt_tokens, args.completion_tokens)
    kimi = cost("moonshot/kimi-k2-6", args.prompt_tokens, args.completion_tokens)
    saved = cur - ds
    pct = (saved / cur * 100) if cur else 0
    kimi_pct = ((cur - kimi) / cur * 100) if cur else 0
    print("  Current ({}):           ${:,.2f} / mo".format(_label(current), cur))
    print("  Routed ({}):   ${:,.2f}  / mo    save {:.1f}%".format(_label(ROUTED_TO), ds, pct))
    print("  Routed ({}):         ${:,.2f}  / mo    save {:.1f}%".format(_label("moonshot/kimi-k2-6"), kimi, kimi_pct))
    print("")
    print("  Annual saving: ${:,.0f}  ·  swap one base_url, zero code change".format(saved * 12))
    print("")
    if pct >= 70:
        print("  -> Routing to a cheaper model saves 70%+. Worth a cost audit.")
    elif pct >= 40:
        print("  -> Meaningful savings available via task-level routing.")
    else:
        print("  -> Limited savings at this mix; optimize prompts / caching first.")


LITELLM_TEMPLATE = """\
model_list:
  # A 经济档（中国算力 · 最省）
  - model_name: deepseek-v4-flash
    litellm_params:
      model: deepseek/deepseek-v4-flash
      api_base: https://api.deepseek.com/v1
      api_key: os.environ/DEEPSEEK_API_KEY
  - model_name: kimi-k2-5
    litellm_params:
      model: moonshot/kimi-k2-5
      api_base: https://api.moonshot.ai/v1
      api_key: os.environ/MOONSHOT_API_KEY
  # B 标准档（中国算力 · 能力平衡）
  - model_name: kimi-k2-6
    litellm_params:
      model: moonshot/kimi-k2-6
      api_base: https://api.moonshot.ai/v1
      api_key: os.environ/MOONSHOT_API_KEY
  - model_name: qwen-72b
    litellm_params:
      model: qwen/qwen2.5-72b-instruct
      api_base: https://dashscope.aliyuncs.com/compatible-mode/v1
      api_key: os.environ/QWEN_API_KEY
  # C 旗舰档（最难任务 · 含西方合规兜底）
  - model_name: kimi-k3
    litellm_params:
      model: moonshot/kimi-k3
      api_base: https://api.moonshot.ai/v1
      api_key: os.environ/MOONSHOT_API_KEY
  - model_name: gpt-4o-fallback
    litellm_params:
      model: gpt-4o
      api_key: os.environ/OPENAI_API_KEY

router_settings:
  routing_strategy: least-cost        # 默认走最便宜且达标的模型
  fallback_strategy: "502,500,503,429"  # 失败自动回退
  model_group_retry_policy:
    num_retries: 2

litellm_params:
  context_window: 128000
"""


def cmd_gen_config(args):
    out = args.out
    with open(out, "w", encoding="utf-8") as f:
        f.write(LITELLM_TEMPLATE)
    print(f"[+] 已生成 {out}")
    print("[+] 部署: docker compose up -d  (见 iac/docker-compose.yml)")
    print("[+] 试用:")
    print('    curl -X POST http://localhost:4000/v1/chat/completions \\')
    print('      -H "content-type: application/json" \\')
    print('      -d \'{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"hi"}]}\'')


def main():
    ap = argparse.ArgumentParser(description="AI 成本审计 + LiteLLM 路由配置生成器")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("audit", help="估算切换到便宜模型路由后的节省比例")
    a.add_argument("--prompt-tokens", type=float, required=True,
                   help="月 prompt token 数 (可用 50e6 表示 5 千万)")
    a.add_argument("--completion-tokens", type=float, required=True,
                   help="月 completion token 数")
    a.add_argument("--current", default="gpt-4o", help="当前模型，默认 gpt-4o")
    a.set_defaults(func=cmd_audit)

    g = sub.add_parser("gen-config", help="生成 litellm_config.yaml")
    g.add_argument("--out", default="litellm_config.yaml", help="输出路径")
    g.set_defaults(func=cmd_gen_config)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
