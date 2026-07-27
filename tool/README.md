# ai_cost_audit.py

The open-source wedge for the cost-arbitrage funnel. Turns "route AI calls to the
cheapest model that works" from a concept into runnable proof. SMBs and indie
devs lack the time to produce this in under a minute — that's the gap this fills.

## Commands

```bash
# Audit: estimate savings for a monthly token mix on your current model
python ai_cost_audit.py audit --prompt-tokens 50e6 --completion-tokens 20e6 --current gpt-4o

# Generate a deployable LiteLLM routing config (task routing + quality gate + fallback)
python ai_cost_audit.py gen-config --out litellm_config.yaml
```

## Notes

- Zero dependencies — standard library only.
- `PRICING` holds 2026-07 public list prices (DeepSeek / Kimi / Qwen / OpenAI /
  Anthropic). Edit the dict when prices move; no reinstall needed.
- Output is an **estimate** from your token counts, not a live proxy measurement.
  Plug in real logs for a ground-truth number.

## Funnel position

GitHub (open source) → README links to landing page → Show HN / Product Hunt /
r/LocalLLaMA → consulting leads. See the repo root `README.md`.
