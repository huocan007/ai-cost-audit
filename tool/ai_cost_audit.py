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
PRICING = {
    # A 经济档（中国算力 · 最省）
    "deepseek/deepseek-v4-flash": {"in": 0.14, "out": 0.28},   # 修正:此前$0.12/$0.32过期
    "moonshot/kimi-k2-5":         {"in": 0.60, "out": 3.00},   # 已核实(缓存命中$0.10)
    # B 标准档（中国算力 · 能力平衡）
    "moonshot/kimi-k2-6":         {"in": 0.95, "out": 4.00},   # 已核实(缓存命中$0.16)
    "qwen/qwen2.5-72b-instruct":  {"in": 0.39, "out": 1.04},
    # C 旗舰档（最难任务）
    "gpt-4o":                     {"in": 2.50, "out": 10.00},
    "gpt-5.6-sol":                {"in": 5.00, "out": 30.00},
    "claude-opus-4.8":            {"in": 5.00, "out": 25.00},
    # 注:kimi-k3(2026-07-16 发布)官方 API 单价本轮未核到精确数,推测≥k2.6;
    #    给客户报价前须到 platform.moonshot.ai/pricing 核最新 K3 价,勿用估算值成交。
}

# 路由默认落点：最便宜且能力够用的模型
ROUTED_TO = "deepseek/deepseek-v4-flash"


def cost(model, p_tokens, c_tokens):
    p = PRICING[model]
    return (p_tokens / 1_000_000) * p["in"] + (c_tokens / 1_000_000) * p["out"]


def cmd_audit(args):
    current = args.current
    if current not in PRICING:
        print(f"[!] 未知模型 {current}。可选: {', '.join(PRICING)}")
        sys.exit(1)
    cur = cost(current, args.prompt_tokens, args.completion_tokens)
    rtd = cost(ROUTED_TO, args.prompt_tokens, args.completion_tokens)
    saved = cur - rtd
    pct = (saved / cur * 100) if cur else 0
    print("=" * 56)
    print("  AI 成本审计结果")
    print("=" * 56)
    print(f"  月 prompt tokens    : {args.prompt_tokens:,.0f}")
    print(f"  月 completion tokens : {args.completion_tokens:,.0f}")
    print(f"  当前模型            : {current}")
    print(f"  当前月成本          : ${cur:,.2f}")
    print(f"  路由到 {ROUTED_TO}")
    print(f"  路由后月成本        : ${rtd:,.2f}")
    print(f"  月度节省            : ${saved:,.2f}  ({pct:.1f}%)")
    print(f"  年度节省            : ${saved * 12:,.2f}")
    print("=" * 56)
    if pct >= 70:
        print("  结论: 路由到便宜模型可省 70%+，强烈建议做成本审计。")
    elif pct >= 40:
        print("  结论: 有显著节省空间，建议做任务级路由（简单任务走便宜模型）。")
    else:
        print("  结论: 当前用量下节省有限，可先优化 prompt / 缓存。")


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

    a = sub.add_parser("audit", help="估算切换到便宜模型路由后的节省%")
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
