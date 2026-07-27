# Launch copy — ai-cost-audit

Three posts for the funnel. Every claim is backed by the open-source CLI (reproducible) or a cited case. Geo-neutral, English-first, honest about limits — that's what earns trust on HN/Reddit.

---

## 1 · Show HN

**Title (keep lowercase, no hype, no "!"):**
```
Show HN: ai-cost-audit – a CLI that estimates your LLM savings across DeepSeek/Kimi/OpenAI
```

**Body:**
```
I kept watching my API bill climb and suspected I was overpaying by routing every
call to one flagship model. So I built a zero-dependency CLI that gives you *your*
number in under a minute.

Point it at your token counts, it recomputes the bill against cheaper models and
prints the saving %:

  $ python ai_cost_audit.py audit --prompt-tokens 50e6 --completion-tokens 20e6 --current gpt-4o

  Current (gpt-4o):            $325.00 / mo
  Routed (DeepSeek V4-Flash):  $12.40  / mo    save 96.2%
  Routed (Kimi K2.6):          $52.40  / mo    save 83.9%

It also emits a ready LiteLLM config (task routing + quality gate + fallback), so
the "what if" becomes "deployed".

Honest limits:
- It estimates from your counts, not a live proxy. Run it on your real logs for
  a ground-truth number — we don't fake it.
- Routing to DeepSeek/Kimi/Qwen means prompts leave your infra and hit those
  providers (servers in China). There's a self-host mode for their open weights
  if data residency matters.
- Not a silver bullet: some tasks genuinely need a flagship. The point is to
  stop paying flagship prices for tasks that don't.

GitHub: https://github.com/huocan007/ai-cost-audit
Happy to answer questions / take routing-heuristic feedback.
```

---

## 2 · Product Hunt

**Tagline (short, verb, benefit):**
```
Find out how much your LLM bill could drop — in one command.
```

**First comment / description:**
```
Most teams route every LLM call to one flagship model and overpay 5–100×.

ai-cost-audit is a free, zero-dependency CLI that audits your API traffic and
shows — with real per-token prices — how much you'd save by routing each task to
the cheapest model that still does the job (DeepSeek / Kimi / Qwen instead of
GPT / Claude).

Example: 50M prompt + 20M completion tokens/mo on GPT-4o → $325/mo. Routed to
DeepSeek V4-Flash → $12.4/mo (save 96.2%). It also generates a deployable LiteLLM
config.

Honest: it estimates from your counts; routing to China-hosted models means
prompts leave your infra (self-host mode available). Not a silver bullet — some
tasks need a flagship.

Open source (MIT). GitHub link in the first comment.
```

---

## 3 · Reddit — r/LocalLLaMA

**Title:**
```
I built a CLI that audits your LLM spend and shows the savings on DeepSeek/Kimi – here's the methodology
```

**Body:**
```
Full disclosure: I built this. Sharing the method because the "you're overpaying"
claim is worthless without a reproducible number.

The idea is model routing (RouteLLM / FrugalGPT): keep ~95% of quality, cut cost
50–90% by sending simple tasks to cheap models and only hard tasks to a flagship.
The hard part was never the idea — it was *my* number.

So I wrote a stdlib-only CLI. You give it your monthly token mix + current model:

  python ai_cost_audit.py audit --prompt-tokens 20e6 --completion-tokens 5e6 --current gpt-4o

and it recomputes the bill against DeepSeek V4-Flash / Kimi K2.6 / Qwen and prints
the saving %. It also emits a LiteLLM config (task routing + quality gate +
fallback) so the audit becomes a deploy.

Two honesty notes I'd want if I were reading this:
1. It estimates from your counts, not a live proxy. Plug in real logs.
2. Routing to DeepSeek/Kimi/Qwen = prompts go to those providers (China). If that
   matters, self-host their open weights — the config supports openai/ base_url
   overrides.

Methodology sources: RouteLLM (UC Berkeley + Canva), FrugalGPT, LiteLLM registry.
GitHub: https://github.com/huocan007/ai-cost-audit
Feedback on the routing heuristics welcome — especially where this breaks.
```

---

## Distribution playbook (read before posting)

**Geo-neutral, English-first.** HN/Reddit reward English docs and penalize
China-first launches (a known case: a Chinese-first open-source launch was
dismissed for language). Don't lead with nationality; lead with the engineering.

**Disclose "I built this."** Required on Reddit; builds trust on HN. Never ask for
upvotes. Never multi-account — both ban.

**"Save 90%" must carry proof.** Always pair the number with token counts + a
reproducible command. Bare "save 90%!" gets downvoted as spam.

**Honest limits = credibility.** The three posts all state the estimate/China-data/
not-a-silver-bullet caveats on purpose. That's what separates you from spam.

**First-hour engagement is everything.** Reply to every comment within ~60 minutes
of posting. Lurkers convert when the author is present and answers plainly.

**Warm up first (Reddit especially).** r/LocalLLaMA has a karma/age automod. Spend
2–4 weeks commenting helpfully before posting. Keep self-promo under ~10% of your
activity.

**Sequence (don't dump all at once):**
1. Push the repo + land the page first.
2. **Show HN** — Tue–Thu, ~8–11am PT (best traction window).
3. Next day: **Product Hunt**.
4. 3–5 days later: **r/LocalLLaMA** (only after the account is warmed).

**What "success" looks like for P0 (our gate):** ≥3 qualified inbound leads within
3 months. A lead = Western SMB/indie dev who ran the CLI (or shared their token
mix) and asked about setup. Track them; that's the only unproven assumption left.
