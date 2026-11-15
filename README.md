# AniList Telegram Notifier 📺🤖

An automated anime tracking system that fetches your "Watching" list from the [AniList GraphQL API](https://anilist.co/) and sends daily notifications directly to your Telegram about newly aired episodes within the last 24 hours.

## 🌟 Features
* **Automated Daily Checks:** Runs automatically every day using GitHub Actions.
* **Smart Tracking:** Only alerts you for anime you are currently watching (checks `Watching` and `Current` lists).
* **Detailed Notifications:** Tells you exactly which episode aired and how many hours ago it was released.
* **Zero Server Cost:** Entirely serverless and hosted via GitHub Actions (no need for a VPS or 24/7 server).
* **Secure:** Uses GitHub Secrets to keep your Telegram Bot Token and Chat ID completely hidden.

## 🛠️ Technologies Used
* **Python 3.12**
* **AniList GraphQL API** (for fetching user data & airing schedules)
* **Telegram Bot API** (for push notifications)
* **GitHub Actions** (for cron job automation)

---

## 🚀 How to Set Up (GitHub Actions / Serverless)
The easiest way to run this bot is by using GitHub Actions.

### 1. Create a Telegram Bot
1. Go to Telegram and search for the **@BotFather**.
2. Send `/newbot` and follow the instructions to create a bot.
3. Copy the **HTTP API Token** provided by BotFather.
4. Start a chat with your new bot and send a simple `/start` message.
5. Get your **Chat ID** (You can use bots like `@userinfobot` or `@RawDataBot` to find your Chat ID).

### 2. Fork & Configure the Repository
1. Fork this repository to your own GitHub account.
2. Go to the `main.py` file and change `ANILIST_USERNAME` to your own AniList username:
   ```python
   ANILIST_USERNAME = "YourUsernameHere"
