---
name: telegram-bot-deployment
description: "Deploy Python Telegram bots to Railway.app 24/7."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Telegram, Bot, Railway, Deployment, Python]
---

# Telegram Bot Deployment

Deploy Python-based Telegram bots to Railway.app for 24/7 operation. Covers token management, timeout configuration, API geo-restrictions, and environment variable setup.

## When to Use

- User wants to run a Telegram bot 24/7
- User asks to deploy a bot to Railway, Render, or similar PaaS
- User has a python-telegram-bot project that needs hosting
- User reports timeout or connection errors on PaaS platforms

## Prerequisites

- Telegram bot token from @BotFather
- GitHub account (for Railway deployment)
- Railway.app account (free tier available)

## Project Structure

```
bot-project/
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
└── Procfile            # "worker: python3 bot.py"
```

## Procedure

### 1. Create Bot on Telegram

1. Open Telegram → go to **@BotFather**
2. Send `/newbot`
3. Choose a name and username
4. Copy the token (format: `123456789:ABCdefGHI...`)

### 2. Prepare Code

**bot.py** — use environment variable for token (never hardcode):
```python
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
```

**requirements.txt**:
```
python-telegram-bot>=20.0
requests>=2.28.0
```

**Procfile** (for Railway):
```
worker: python3 bot.py
```

### 3. Push to GitHub

```bash
git init && git add -A
git commit -m "feat: telegram bot"
git remote add origin https://github.com/user/repo.git
git push -u origin main
```

### 4. Deploy to Railway

1. Go to **railway.app** → Sign in with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Select the bot repo
4. Go to **"Variables"** tab
5. Add: `BOT_TOKEN` = `<your token>`
6. Railway auto-deploys

## Key Patterns

### Timeout Configuration

Railway and other PaaS platforms often have slow DNS/network. Always set generous timeouts:

```python
app = (
    Application.builder()
    .token(BOT_TOKEN)
    .read_timeout(30)
    .write_timeout(30)
    .connect_timeout(30)
    .build()
)
```

### Environment Variables

Always use `os.environ.get("BOT_TOKEN")` — never hardcode tokens. Railway injects env vars from the Variables tab.

### Drop Pending Updates

On restart, the bot should not process old queued updates:
```python
app.run_polling(drop_pending_updates=True)
```

## Pitfalls

1. **Timeout errors on PaaS.** `TimedOut` errors are the #1 issue on Railway/Render. Fix: set `read_timeout`, `write_timeout`, `connect_timeout` to 30+ seconds. The error looks like `httpx.ReadTimeout` or `telegram.error.TimedOut`.

2. **Geo-restricted APIs.** Iranian APIs (tala.ir, sarafario.ir, bitpin.ir) may be blocked from PaaS servers outside Iran. Solution: add international fallback APIs (exchangerate-api.com, fawaz CDN). Test APIs from the deployment server before relying on them.

3. **Bot token security.** Never commit tokens to git. Use environment variables. If a token is exposed, revoke it via @BotFather `/revoke`.

4. **Worker vs Web service.** Telegram bots use long-polling, so they need a `worker` process type, not a `web` server. The Procfile should say `worker: python3 bot.py`, not `web: ...`.

5. **Railway free tier.** Railway gives $5/month free credit. A simple Telegram bot uses ~$0. If it exceeds, the service stops. Monitor usage in Railway dashboard.

6. **Bot stops after inactivity.** If using free tier on some platforms, the service may sleep after inactivity. Telegram bots need to be always-on for polling. Consider using webhook mode for platforms that sleep workers.

## Verification

After deployment:
1. Check Railway logs for `✅ ربات در حال اجراست...`
2. Send `/start` to the bot in Telegram
3. Bot should respond without errors
4. Check Railway logs for `200 OK` responses to `getUpdates`
