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

class DatabaseManager:
    def __init__(self):
        self.active_uri_index = config.ACTIVE_DB_INDEX
        self.available_uris = [config.MONGODB_PRIMARY_URI] + list(config.MONGODB_SECONDARY_URIS)
        self.client = None
        self.db = None
        self.is_mock = False
        self._initialize_connection()

    def _initialize_connection(self):
        """Attempts to connect to the active MongoDB URI; falls back to mongomock if unavailable."""
        uri = self.available_uris[self.active_uri_index]
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            # Trigger server connection test
            client.admin.command('ping')
            self.client = client
            self.db = self.client[config.DB_NAME]
            self.is_mock = False
            print(f"[Database] Successfully connected to live MongoDB URI [{self.active_uri_index}]: {uri}")
        except Exception as e:
            print(f"[Database Warning] Unable to connect to live MongoDB at {uri} ({e}). Initializing high-fidelity MongoMock DB.")
            self.client = mongomock.MongoClient()
            self.db = self.client[config.DB_NAME]
            self.is_mock = True

        self._seed_initial_data()

    def test_connection(self, uri: str) -> Dict[str, Any]:
        """Tests a prospective MongoDB connection URL."""
        try:
            t0 = time.time()
            test_client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            test_client.admin.command('ping')
            latency_ms = round((time.time() - t0) * 1000, 2)
            return {
                "success": True,
                "message": f"Successfully connected to MongoDB ({latency_ms}ms latency)",
                "latency_ms": latency_ms
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}",
                "latency_ms": None
            }

    def switch_database_uri(self, uri_index: int, custom_uri: Optional[str] = None) -> Dict[str, Any]:
        """Switches active database connection to another URL configured via Admin Panel."""
        if custom_uri:
            if custom_uri not in self.available_uris:
                self.available_uris.append(custom_uri)
            self.active_uri_index = self.available_uris.index(custom_uri)
        elif 0 <= uri_index < len(self.available_uris):
            self.active_uri_index = uri_index
        else:
            return {"success": False, "message": "Invalid URI index"}

        self._initialize_connection()
        return {
            "success": True,
            "active_index": self.active_uri_index,
            "active_uri": self.available_uris[self.active_uri_index],
            "is_mock": self.is_mock
        }

    def get_database_status(self) -> Dict[str, Any]:
        """Returns list of all dynamic DB URLs and active status for Admin Panel."""
        return {
            "active_index": self.active_uri_index,
            "active_uri": self.available_uris[self.active_uri_index],
            "is_mock": self.is_mock,
            "available_uris": self.available_uris,
            "db_name": config.DB_NAME
        }

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
                "available_mongo_uris": self.available_uris,
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
                "target_url": "https://t.me/MioAdsOfficialBot?start=promo_masterclass",
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
                "target_url": "https://t.me/MioAdsOfficialBot?start=promo_game",
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
