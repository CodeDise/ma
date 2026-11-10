# 🚀 Mio Ads: Telegram Mini App Ads Ecosystem

An enterprise-grade Telegram Mini App and Ads Network backend engineered with FastAPI, MongoDB, ReportLab, and pure CSS/JS for direct deployment on Render's free tier.

![Mio Ads Logo](/static/images/logo.png)

---

## 🏛 System Architecture & Stack

| Layer | Component | Description |
|---|---|---|
| **Front-End** | Telegram Mini App | Responsive UI with mandatory opening view, dynamic watermark MA logo, and persistent PNG bottom navigation. |
| **Back-End** | FastAPI (Python 3.8+) | Scalable asynchronous ASGI web service optimized for Render's free tier. |
| **Config** | `config.py` | Centralized local encapsulation of all API keys, operational thresholds, and dynamic values. |
| **Database** | MongoDB Only (`database.py`) | Multi-URI dynamic connection pool with connection testing and MongoMock failover. |
| **Invoicing** | ReportLab (`invoices.py`) | Automated PDF invoices for deposits, withdrawals, and campaign budgets. |
| **Audit** | Administrative Lock Channel (`lock_channel.py`) | Instantaneous security mirroring for all tickets, invoices, and SLA trackers. |

---

## 🎨 Visual Identity & Dynamic Watermark

- **Color Palette:** Deep Navy Blue (`#0B192C`) & Crisp White (`#FFFFFF`).
- **Brand Identity:** Centered 1:1 aspect ratio MA monogram logo.
- **Dynamic Watermark:** Pure CSS watermark centered in the background that dynamically adjusts opacity and blend mode based on Light and Dark theme toggles.
- **Persistent Bottom Navigation:** Crisp 64x64 PNG icons exclusively (`home.png`, `channels.png`, `wallet.png`, `stats.png`, `support.png`, `admin.png`, `settings.png`).
- **Language Selector Theme Inversion:** Active selected language card renders in **Dark Theme** with an electric cyan border, while inactive languages display in **Light Theme**.

---

## 🔑 Operational Modules

1. **User Onboarding & Static Telegram ID:** Users register once with their numeric Telegram ID as the static unique identifier.
2. **Channel Management & Moderation:** Link Telegram channels for Promotion or Monetization. All linked channels enter a `pending` state requiring manual Admin moderation before ad delivery begins.
3. **Monetization & Promotion (CPC / CPM):** Minimum deposit is ₹500 INR (UPI) or $10 USDT. Withdrawals have a $5 USDT minimum and are governed by a strict 48-Hour Admin Review SLA.
4. **Dwell-Time Timer & Direct Click Bypass:** Ad impressions require 60–120 seconds dwell time before verifying, unless users click directly through to the ad (skipping the timer immediately).
5. **Multi-Currency & Global Localization:** Real-time USDT/INR currency conversion ($1 = ₹80 default). Localization covers Hindi, Bengali, Tamil, Telugu, Marathi, Gujarati, Kannada, Malayalam, Punjabi, Russian, English, Japanese, Chinese, Korean, Spanish, and Arabic.
6. **Support Ticketing & 24h SLA:** Open support tickets with Gmail, narrative, and multi-file attachments (images, video, documents). Tracked with live 24h countdown and mirrored to the private Lock Channel.
7. **Automated PDF Invoices & Lock Ledger:** Deposits, payouts, and campaign deductions generate itemized PDF invoices with cryptographic reference IDs and full metadata backup.
8. **Automated Referral & Affiliate Tracking:** Custom referral URLs (`/r/{code}`) count clicks per link. Users can apply for high-volume affiliate tiers with configurable per-click rates.
9. **Granular Publisher Analytics & Leaderboard:** Real-time Daily, Weekly, Monthly, and Total click metrics. The public volume leaderboard preserves privacy by displaying channel name and logo only.
10. **Unified Global Command Interface:** Standard bot commands (`/start`, `/wallet`, `/channels`, `/stats`, `/help`, `/admin`) can be executed through the Mini App global command input bar or Telegram chat.

---

## 🛠 Local Setup & Running

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate PNG navigation icons
python generate_icons.py

# 3. Run automated end-to-end test suite
python test_ecosystem.py

# 4. Start the server
uvicorn app:app --host 0.0.0.0 --port 8000
```

Access the Mini App locally at: `http://localhost:8000`

---

## ☁️ Render Deployment (Free Tier)

This repository includes `render.yaml` and `Procfile` configured for direct deployment on Render:
1. Push code to your GitHub/GitLab repository.
2. In Render Dashboard, click **New +** -> **Web Service** or **Blueprint**.
3. Select your repository. Render automatically reads `render.yaml`:
   - **Build Command:** `pip install -r requirements.txt && python generate_icons.py`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health`
