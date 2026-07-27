# ai-cost-audit

**Find out how much your LLM bill could drop — in one command.**

A zero-dependency CLI that audits your API traffic and shows, with real per-token prices, how much you'd save by routing each task to the cheapest model that still does the job (DeepSeek / Kimi / Qwen instead of GPT / Claude). Built for teams who suspect they're overpaying but haven't had time to prove it.

> This is the open-source entry point to a paid routing-setup & tuning service. The CLI is free and always will be. See [Paid help](#need-someone-to-do-it-for-you) at the bottom.

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
[![Zero dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](requirements.txt)

## Why

Most teams route **every** call to one flagship model. That's like using express shipping for a letter. Model routing (RouteLLM, FrugalGPT) shows you can keep ~95% of quality while cutting cost 50–90%. The hard part was never the idea — it was *your number*. `ai-cost-audit` gives you that number in under a minute, from your own token counts.

## Install

No `pip` needed. It's a single file using only the Python standard library.

```bash
git clone https://github.com/acan-ai/ai-cost-audit.git
cd ai-cost-audit
python ai_cost_audit.py --help
```

Requires Python 3.8+. (Tested on 3.13.)

## Quickstart

```bash
# Estimate savings for a typical SMB load
# (20M prompt + 5M completion tokens/mo, currently on GPT-4o)
python ai_cost_audit.py audit --prompt-tokens 20e6 --completion-tokens 5e6 --current gpt-4o

# Emit a ready-to-deploy LiteLLM routing config
# (task routing + quality gate + automatic fallback)
python ai_cost_audit.py gen-config --out litellm_config.yaml
```

## Example output

```text
$ python ai_cost_audit.py audit --prompt-tokens 50e6 --completion-tokens 20e6 --current gpt-4o

  Current (gpt-4o):            $325.00 / mo
  Routed (DeepSeek V4-Flash):  $12.60  / mo    save 96.1%
  Routed (Kimi K2.6):          $127.50 / mo    save 60.8%

  Annual saving: $3,749  ·  zero code change, swap one base_url
```

Numbers use public 2026-07 list prices (see `PRICING` in the source). They're estimates — plug your own logs in for a ground-truth number.

## How it works

- **`audit`** — given your monthly token mix and current model, recomputes the bill against a menu of cheaper models (DeepSeek / Kimi / Qwen) and prints the savings %.
- **`gen-config`** — writes a LiteLLM config that routes by task, keeps a quality gate, and falls back to a flagship model only when needed.
- Prices live in one dictionary. Edit it when list prices move — no dependencies to reinstall.

## Honesty box

- This tool **estimates**. Your real saving depends on your task mix. Run it on your actual token counts; we don't fake the number.
- Routing to DeepSeek / Kimi / Qwen means prompts leave your infrastructure and go to those providers (servers in China). If data residency matters, **self-host their open-weight models on infrastructure you control** — the generated config supports `openai/` base_url overrides for exactly that.
- Not a silver bullet: some tasks genuinely need a flagship model. The point is to stop paying flagship prices for tasks that don't.

## Need someone to do it for you?

If you'd rather not wire this up yourself, there's a paid service (by the same person) that:

1. **Audits** your real traffic and delivers a written report with numbers.
2. **Deploys** a self-hosted LiteLLM gateway — you change one `base_url`, nothing else.
3. **Tunes** it monthly as models and prices shift, with quality gates and budget caps.

**Bring-your-own-keys (BYOK):** your provider bills you directly; you pay only for the setup + tuning. → [ai.acan.ccwu.cc](https://ai.acan.ccwu.cc)

## Trust

- The gateway code is open (LiteLLM, Apache-2.0). You can audit every line.
- **BYOK:** we never see your provider keys. Prompts are not stored after delivery.
- Methodology builds on public research: RouteLLM (UC Berkeley + Canva), FrugalGPT, and LiteLLM's model registry.

## License

MIT — use it freely, just keep the honesty box.

## Contributing

Issues and PRs welcome. If you wire up a new provider price, please send the source link.
