"""
Database Layer for Mio Ads Telegram Mini App Ads Ecosystem
Strictly MongoDB only. Supports multiple dynamic database URLs configurable via Admin Panel,
connection testing, and seamless failover / fallback.
"""

import time
from typing import Dict, Any, List, Optional
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import mongomock

from config import config

import os, json, hashlib, re

def _uri_id(uri: str) -> str:
    return hashlib.sha1(uri.encode()).hexdigest()[:10]

def _mask(uri: str) -> str:
    return re.sub(r'(://[^:/@]+:)[^@]+@', r'\1***@', uri)

class DatabaseManager:
    """MongoDB manager: admin can add/remove many URLs; the first reachable URL is active."""
    def __init__(self):
        self.urls: List[str] = self._load_urls()
        self.active_uri: Optional[str] = None
        self.client = None
        self.db = None
        self.is_mock = False
        self._connect()

    # ---- persistence ----
    def _load_urls(self) -> List[str]:
        try:
            with open(config.DB_URLS_FILE) as f:
                urls = [u for u in json.load(f) if isinstance(u, str) and u]
                if urls:
                    return urls
        except Exception:
            pass
        return [config.MONGODB_PRIMARY_URI]

    def _save_urls(self):
        try:
            os.makedirs(os.path.dirname(config.DB_URLS_FILE), exist_ok=True)
            with open(config.DB_URLS_FILE, "w") as f:
                json.dump(self.urls, f)
        except Exception as e:
            print(f"[Database Warning] Could not save URL list file: {e}")
        # Mirror in the live DB too, so the list survives restarts on hosts with temporary disk
        try:
            if not self.is_mock and self.db is not None:
                self.db.system_settings.update_one({"_id": "db_urls"}, {"$set": {"urls": self.urls}}, upsert=True)
        except Exception:
            pass

    def _merge_urls_from_db(self):
        try:
            doc = self.db.system_settings.find_one({"_id": "db_urls"})
            if doc:
                for u in doc.get("urls", []):
                    if u not in self.urls:
                        self.urls.append(u)
        except Exception:
            pass

    # ---- connection ----
    def _connect(self):
        """Connects to the first reachable URL in the list; MongoMock only if none work."""
        for uri in self.urls:
            try:
                client = MongoClient(uri, serverSelectionTimeoutMS=2500)
                client.admin.command('ping')
                self.client, self.active_uri, self.is_mock = client, uri, False
                self.db = client[config.DB_NAME]
                print(f"[Database] Connected to live MongoDB: {_mask(uri)}")
                self._merge_urls_from_db()
                self._seed_initial_data()
                return
            except Exception as e:
                print(f"[Database Warning] Cannot connect to {_mask(uri)} ({e})")
        print("[Database Warning] No live MongoDB reachable. Using temporary MongoMock DB.")
        self.client = mongomock.MongoClient()
        self.db = self.client[config.DB_NAME]
        self.active_uri, self.is_mock = None, True
        self._seed_initial_data()

    def test_connection(self, uri: str) -> Dict[str, Any]:
        try:
            t0 = time.time()
            c = MongoClient(uri, serverSelectionTimeoutMS=3000)
            c.admin.command('ping')
            ms = round((time.time() - t0) * 1000, 1)
            c.close()
            return {"success": True, "message": f"Connected ({ms} ms)", "latency_ms": ms}
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)[:120]}", "latency_ms": None}

    def add_url(self, uri: str) -> Dict[str, Any]:
        uri = (uri or "").strip()
        if not re.match(r'^mongodb(\+srv)?://', uri):
            return {"success": False, "message": "URL must start with mongodb:// or mongodb+srv://"}
        if uri in self.urls:
            return {"success": False, "message": "This URL is already added"}
        res = self.test_connection(uri)
        if not res["success"]:
            return {"success": False, "message": res["message"]}
        self.urls.append(uri)
        if self.is_mock:           # first working URL replaces the temporary mock DB
            self._connect()
        self._save_urls()
        return {"success": True, "message": "MongoDB URL added", "latency_ms": res["latency_ms"]}

    def remove_url(self, db_id: str) -> Dict[str, Any]:
        target = next((u for u in self.urls if _uri_id(u) == db_id), None)
        if not target:
            return {"success": False, "message": "URL not found"}
        if len(self.urls) <= 1:
            return {"success": False, "message": "Cannot remove the last MongoDB URL"}
        self.urls.remove(target)
        if target == self.active_uri:
            self._connect()        # fail over to the next reachable URL
        self._save_urls()
        return {"success": True, "message": "MongoDB URL removed"}

    def get_database_status(self) -> Dict[str, Any]:
        items = []
        for uri in self.urls:
            if uri == self.active_uri:
                ok, ms = True, None
                try:
                    t0 = time.time(); self.client.admin.command('ping'); ms = round((time.time() - t0) * 1000, 1)
                except Exception:
                    ok = False
            else:
                r = self.test_connection(uri); ok, ms = r["success"], r["latency_ms"]
            items.append({"db_id": _uri_id(uri), "uri": _mask(uri), "connected": ok,
                          "latency_ms": ms, "active": uri == self.active_uri})
        return {"is_mock": self.is_mock, "db_name": config.DB_NAME, "urls": items}

    def _seed_initial_data(self):
        """Pre-populates sample verified channels, active campaigns, and admin defaults if empty."""
        # Dynamic system settings
        if not self.db.system_settings.find_one({"_id": "global_config"}):
            self.db.system_settings.insert_one({
                "_id": "global_config",
                "platform_fee_percent": config.PLATFORM_FEE_PERCENT,
                "usdt_to_inr_rate": config.USDT_TO_INR_RATE,
                "affiliate_click_rate_usdt": config.AFFILIATE_CLICK_RATE_USDT,
                "default_dwell_time_seconds": config.DEFAULT_DWELL_TIME_SECONDS,
                "lock_channel_id": config.LOCK_CHANNEL_ID,
                "updated_at": time.time()
            })

        # Seed sample demo admin user
        for admin_id in config.ADMIN_TELEGRAM_IDS:
            if not self.db.users.find_one({"telegram_id": admin_id}):
                self.db.users.insert_one({
                    "telegram_id": admin_id,
                    "username": f"admin_{admin_id}",
                    "first_name": "Mio Ads Admin",
                    "role": "admin",
                    "preferred_currency": "USDT",
                    "language": "en",
                    "wallet_balance_usdt": 1250.00,
                    "wallet_balance_inr": 100000.00,
                    "api_key": f"mio_adm_key_{admin_id}_{int(time.time())}",
                    "referral_code": f"REF{admin_id}",
                    "referred_by": None,
                    "created_at": time.time()
                })

        # Seed a regular demo publisher/advertiser user
        demo_user_id = 100200300
        if not self.db.users.find_one({"telegram_id": demo_user_id}):
            self.db.users.insert_one({
                "telegram_id": demo_user_id,
                "username": "crypto_trader_in",
                "first_name": "Arjun Sharma",
                "role": "user",
                "preferred_currency": "INR",
                "language": "hi",
                "wallet_balance_usdt": 85.50,
                "wallet_balance_inr": 6840.00,
                "api_key": f"mio_usr_key_{demo_user_id}",
                "referral_code": "ARJUN77",
                "referred_by": None,
                "created_at": time.time() - 86400 * 5
            })

        # Seed sample channels
        sample_channels = [
            {
                "channel_id": "ch_telegram_signals",
                "telegram_id": demo_user_id,
                "title": "Crypto Signals & Alpha India",
                "username": "@CryptoSignalsAlphaIN",
                "type": "monetization",
                "category": "Crypto & Finance",
                "subscribers": 142000,
                "status": "approved",
                "total_clicks": 3420,
                "total_views": 85200,
                "earnings_usdt": 170.40,
                "created_at": time.time() - 86400 * 10
            },
            {
                "channel_id": "ch_tech_deals",
                "telegram_id": demo_user_id,
                "title": "Daily Tech Deals & Loot",
                "username": "@TechDealsLootHub",
                "type": "monetization",
                "category": "E-Commerce & Tech",
                "subscribers": 98500,
                "status": "approved",
                "total_clicks": 1890,
                "total_views": 49000,
                "earnings_usdt": 98.00,
                "created_at": time.time() - 86400 * 8
            },
            {
                "channel_id": "ch_pending_promo",
                "telegram_id": demo_user_id,
                "title": "FinTech Startup Launch",
                "username": "@FinTechStartupHQ",
                "type": "promotion",
                "category": "Startups & Business",
                "subscribers": 25000,
                "status": "pending",
                "total_clicks": 0,
                "total_views": 0,
                "earnings_usdt": 0.0,
                "created_at": time.time() - 3600 * 4
            }
        ]
        for ch in sample_channels:
            if not self.db.channels.find_one({"channel_id": ch["channel_id"]}):
                self.db.channels.insert_one(ch)

        # Seed sample campaigns
        sample_campaigns = [
            {
                "campaign_id": "cmp_001",
                "advertiser_id": demo_user_id,
                "title": "Join Top Trading Masterclass 2026",
                "narrative": "Exclusive Telegram VIP Trading Group. High accuracy signals, educational webinars, and weekly portfolio reviews.",
                "banner_url": "/static/images/logo.png",
                "target_url": "https://t.me/mioadsbot?start=promo_masterclass",
                "model": "CPC",
                "bid_usdt": 0.03,
                "budget_usdt": 150.00,
                "spent_usdt": 42.60,
                "dwell_time_seconds": 60,
                "impressions": 14200,
                "clicks": 1420,
                "status": "active",
                "created_at": time.time() - 86400 * 3
            },
            {
                "campaign_id": "cmp_002",
                "advertiser_id": demo_user_id,
                "title": "Next-Gen Web3 Gaming Bot",
                "narrative": "Play, farm tokens, and earn TON rewards directly inside Telegram Mini App. Over 1M daily active players!",
                "banner_url": "/static/images/logo.png",
                "target_url": "https://t.me/mioadsbot?start=promo_game",
                "model": "CPM",
                "bid_usdt": 2.50,
                "budget_usdt": 300.00,
                "spent_usdt": 125.00,
                "dwell_time_seconds": 60,
                "impressions": 50000,
                "clicks": 2840,
                "status": "active",
                "created_at": time.time() - 86400 * 6
            }
        ]
        for cmp in sample_campaigns:
            if not self.db.campaigns.find_one({"campaign_id": cmp["campaign_id"]}):
                self.db.campaigns.insert_one(cmp)

# Global db manager instance
db_manager = DatabaseManager()
db = db_manager.db
