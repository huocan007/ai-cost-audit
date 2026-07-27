# Deploy the landing page to DediRock (short commands)

Goal: serve `landing/index.html` at `https://ai.acan.ccwu.cc` via Caddy on your
existing DediRock VPS (Debian 13). No long pastes — run these one at a time.

## 0 · DNS (do this in DNSHE first, once)
Add an **A record**: `ai` → `192.3.90.244` (your DediRock IP).
Wait a few minutes for propagation before testing.

## 1 · On DediRock — make the web root
```bash
mkdir -p /var/www/ai
```

## 2 · From your Windows machine — upload the page
(SSH port is 10022; adjust the path to where you keep the repo.)
```bash
scp -P 10022 "D:/WorkBuddy/日常/cost-arbitrage-stack/landing/index.html" root@192.3.90.244:/var/www/ai/index.html
```

## 3 · On DediRock — tell Caddy about the new host
Append this block to your Caddyfile (or create `/etc/caddy/Caddyfile` if none):
```caddy
ai.acan.ccwu.cc {
    root * /var/www/ai
    file_server
    encode gzip
}
```
Then reload Caddy:
```bash
caddy reload --config /etc/caddy/Caddyfile
```
(If Caddy isn't installed yet: `apt update && apt install -y caddy`.)

## 4 · Verify
From your Windows machine (or any browser):
```bash
curl -sI https://ai.acan.ccwu.cc | head -n 1
```
Expect `HTTP/2 200`. Open `https://ai.acan.ccwu.cc` to see the page.

## Notes
- The page is fully static + client-side JS — no backend, no secrets on the server.
- To update later: re-run step 2, then `caddy reload` (step 3) is not needed for
  a pure file change.
- The "Book a free audit" button is a `mailto:` to `hello@acan.ccwu.cc` — works
  with zero backend. Swap to a form later if you want submissions in one place.
