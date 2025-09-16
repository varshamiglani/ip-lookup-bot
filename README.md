# 🕵️‍♀️ Telegram IP Info Bot

A **Python-powered Telegram bot** that lets you look up IP addresses and domains with ease.  
Get **geolocation 🌍, ISP, ASN, timezone, reverse DNS, Google Maps link 🗺️, and raw JSON output ⚡** — all inside Telegram!

---

## ✨ Features
- 🔎 `/ip <ip-or-domain>` — Lookup any IP or domain  
- 🌐 Domain resolution to IP included  
- 🏷 Shows ISP, ASN, and organization  
- 📍 City, region, country + ZIP code  
- 🗺 Google Maps link for quick view  
- 🕒 Timezone info  
- 🔁 Reverse DNS lookup  
- ⚙ Proxy & Hosting detection flags  
- 📦 `/raw` command for raw JSON response

---

## 🚀 Quick Start

### 1️⃣ Clone the repo
```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2️⃣ Set up Python environment
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scriptsctivate
pip install -r requirements.txt
```

### 3️⃣ Get your Telegram Bot token
- Go to [@BotFather](https://t.me/BotFather) on Telegram  
- Create a bot and copy the **API token**  
- Export it as an environment variable:
```bash
export TELEGRAM_TOKEN="123456:ABC-DEF..."   # Linux/Mac
setx TELEGRAM_TOKEN "123456:ABC-DEF..."     # Windows PowerShell
```

### 4️⃣ Run the bot
```bash
python bot.py
```

🎉 Done! Now talk to your bot on Telegram and try `/ip 8.8.8.8`.

---

## 🐳 Run with Docker

### Build the image
```bash
docker build -t telegram-ip-bot .
```

### Run the container
```bash
docker run --rm -e TELEGRAM_TOKEN="$TELEGRAM_TOKEN" telegram-ip-bot
```

---

## ⚡ Run with Docker Compose

1. Copy `.env.example` to `.env` and put your bot token inside.
```bash
cp .env.example .env
```

2. Start the bot:
```bash
docker compose up --build
```

---

## 📂 Project Structure
```
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker build
├── docker-compose.yml  # Compose setup
├── .env.example        # Env file example
├── Procfile            # For Heroku deployment
├── LICENSE             # MIT License
└── README.md           # This file
```

---

## 🛠️ Deployment Options
- **Heroku** → Uses `Procfile` (`worker: python bot.py`)  
- **Railway / Render / Fly.io** → Deploy with Dockerfile  
- **VPS (Linux server)** → Just run `python bot.py` inside `screen`/`tmux`

---

## 🧑‍💻 Tech Stack
- **Python 3.11+**  
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) (async)  
- [aiohttp](https://docs.aiohttp.org/) for async HTTP requests  
- [ip-api.com](http://ip-api.com) free geolocation API

---

## 💡 Example

**User:**
```
/ip 8.8.8.8
```

**Bot Reply:**
```
🔍 Query: 8.8.8.8

🏷 ASN / Org / ISP: AS15169 Google LLC
📍 Location: Mountain View, California, United States
🗺 Coordinates: 37.4056, -122.0775 — [Map](https://www.google.com/maps/search/?api=1&query=37.4056,-122.0775)
🕒 Timezone: America/Los_Angeles
🌐 Country code: US • Continent: NA
```

---

## 📜 License
This project is licensed under the **MIT License** — feel free to use, modify, and share!

---

## 👩‍💻 Author
Made with ❤️ by **Varsha Miglani**
