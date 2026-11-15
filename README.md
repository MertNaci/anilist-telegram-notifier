# AniList Telegram Notifier 📺🤖

A small bot that checks your AniList **Watching** list every day and sends you a Telegram message listing the episodes that aired the previous day.

## 🌟 Features
* **Automated daily checks:** Runs every night on GitHub Actions. No server needed.
* **Tracks what you're watching:** Uses your AniList list status (`Watching` and `Rewatching`), not list names.
* **No duplicates, no gaps:** Each run covers one full calendar day (00:00–00:00, Turkey time), so it doesn't matter when GitHub actually starts the job.
* **Clear notifications:** Shows each episode's number and air time.
* **Secure:** The Telegram token and chat ID live in GitHub Secrets, never in the code.

## 🛠️ Technologies Used
* **Python 3.12**
* **AniList GraphQL API** (user list & airing schedules)
* **Telegram Bot API** (notifications)
* **GitHub Actions** (scheduled runs)

---

## 🚀 Setup (GitHub Actions)

### 1. Create a Telegram bot
1. Open Telegram and find **@BotFather**.
2. Send `/newbot` and follow the instructions.
3. Copy the **HTTP API token** it gives you.
4. Open a chat with your new bot and send `/start`.
5. Get your **chat ID** (e.g. with `@userinfobot`).

### 2. Fork and configure
1. Fork this repository.
2. In `main.py`, set your AniList username:
   ```python
   ANILIST_USERNAME = "YourUsernameHere"
   ```
   Your AniList list must be public. The bot reads it without logging in.

### 3. Add GitHub Secrets
In your fork, go to **Settings → Secrets and variables → Actions → New repository secret** and add:

| Name | Value |
|------|-------|
| `TELEGRAM_TOKEN` | Your bot token from BotFather |
| `CHAT_ID` | Your Telegram chat ID |

### 4. Enable and test
1. Open the **Actions** tab. Forks have Actions disabled by default, so click **Enable**.
2. Select **Daily Anime Notification → Run workflow** to test it.

The workflow then runs every night at **00:07 (UTC+3)**. GitHub sometimes starts scheduled jobs a few hours late; that's fine, because the checked day stays the same.

---

## 💻 Running Locally

```bash
pip install -r requirements.txt
```

Create a `local_secrets.py` file next to `main.py` (it's in `.gitignore`, so it won't be committed):

```python
TELEGRAM_TOKEN = "your-bot-token"
CHAT_ID = "your-chat-id"
```

Then run:

```bash
python main.py --dry-run   # prints the message without sending it
python main.py             # sends it to Telegram
```

---

## ⚙️ Configuration
In `main.py`:

* `CUTOFF_HOUR`: When the daily window ends (default `0` = midnight). If you change it, update the cron time in `.github/workflows/daily_bot.yml` to match.
* `TR_TZ`: Time zone used for the window and message times (default UTC+3).
