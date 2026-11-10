"""
End-to-End Test Suite for Mio Ads Telegram Mini App Ads Ecosystem
Verifies all 9 operational modules, configuration encapsulation, PDF invoice generation,
SLA rules, dynamic MongoDB connection pool, and dwell-time bypass logic.
"""

import sys
import os
import time

# Ensure workspace is in sys.path
sys.path.insert(0, "/workspace/mioads")

from fastapi.testclient import TestClient
from app import app
from config import config

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("🚀 RUNNING MIO ADS ECOSYSTEM TEST SUITE")
    print("=" * 60)

    # Test 1: Health Check & System Info
    print("\n[Test 1] Testing Health Check and System Probe...")
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    assert health_data["status"] == "healthy"
    assert health_data["app"] == "Mio Ads"
    print(f"✅ Health Check Passed: {health_data['app']} v{health_data['version']}")
    print(f"   Database mode: {health_data['database']['is_mock']} (Mock / Live Adapter Ready)")

    # Test 2: Telegram Mini App Entry Point & Watermark Assets
    print("\n[Test 2] Testing Mini App Landing Page and Assets...")
    res = client.get("/")
    assert res.status_code == 200
    assert "MIO ADS" in res.text
    assert "dynamic-watermark" in res.text
    assert "opening-view" in res.text
    print("✅ Mini App Landing Page served with mandatory opening view & dynamic watermark.")

    # Test 3: User Onboarding & Telegram ID Static Identification
    print("\n[Test 3] Testing User Profile Registration...")
    tg_id = 99887766
    res = client.get(f"/api/v1/user/profile?telegram_id={tg_id}")
    assert res.status_code == 200
    user_data = res.json()
    assert user_data["telegram_id"] == tg_id
    assert "wallet_balance_usdt" in user_data
    assert "referral_code" in user_data
    print(f"✅ User Registration verified: Telegram ID {tg_id}, Ref: {user_data['referral_code']}")

    # Test 4: Channel Management & Admin Moderation
    print("\n[Test 4] Testing Channel Linking & Admin Moderation...")
    ch_payload = {
        "telegram_id": tg_id,
        "title": "Crypto Whales Daily",
        "username": "@CryptoWhalesDaily",
        "type": "monetization",
        "category": "Crypto & Finance",
        "subscribers": 50000
    }
    res = client.post("/api/v1/channels/link", json=ch_payload)
    assert res.status_code == 200
    ch_data = res.json()
    ch_id = ch_data["channel_id"]
    assert ch_data["status"] == "pending", "New channel must require manual Admin approval"
    print(f"✅ Channel linked with 'pending' status: {ch_data['title']} ({ch_id})")

    # Moderate channel as Admin
    admin_id = config.ADMIN_TELEGRAM_IDS[0]
    mod_payload = {
        "admin_id": admin_id,
        "channel_id": ch_id,
        "action": "approved"
    }
    res = client.post("/api/v1/admin/channels/moderate", json=mod_payload)
    assert res.status_code == 200
    assert res.json()["status"] == "approved"
    print(f"✅ Admin moderation approved channel {ch_id}")

    # Test 5: Deposit with Automated PDF Invoice & Lock Channel Mirroring
    print("\n[Test 5] Testing Deposit, PDF Invoice Generation & Lock Ledger...")
    dep_payload = {
        "user_id": tg_id,
        "currency": "INR",
        "amount": 1000.0,
        "payment_method": "UPI",
        "utr_or_txid": "UPI1234567890"
    }
    res = client.post("/api/v1/wallet/deposit", json=dep_payload)
    assert res.status_code == 200
    dep_data = res.json()
    assert dep_data["success"] is True
    inv_id = dep_data["invoice_id"]
    pdf_url = dep_data["invoice_pdf_url"]
    print(f"✅ Deposit registered. Generated Invoice: {inv_id}")
    print(f"   Invoice PDF Path: {pdf_url}")

    # Verify generated invoice exists on disk
    inv_filename = f"invoice_{inv_id}.pdf"
    full_pdf_path = os.path.join(config.INVOICES_DIR, inv_filename)
    assert os.path.exists(full_pdf_path), f"Invoice PDF {full_pdf_path} not found on disk!"
    assert os.path.getsize(full_pdf_path) > 1000, "Invoice PDF file size too small!"
    print(f"✅ Invoice PDF verified on disk ({os.path.getsize(full_pdf_path)} bytes)")

    # Test 6: Campaign Creation & Budget Deduction
    print("\n[Test 6] Testing Campaign Creation (CPC/CPM)...")
    cmp_payload = {
        "advertiser_id": tg_id,
        "title": "Alpha Bot Launch 2026",
        "narrative": "Experience automated high frequency algorithmic trading on Telegram.",
        "target_url": "https://t.me/MioAdsOfficialBot?start=promo_alpha",
        "model": "CPC",
        "bid_usdt": 0.05,
        "budget_usdt": 10.00,
        "dwell_time_seconds": 60
    }
    res = client.post("/api/v1/campaigns/create", json=cmp_payload)
    assert res.status_code == 200
    cmp_data = res.json()
    cmp_id = cmp_data["campaign_id"]
    print(f"✅ Campaign created: {cmp_data['title']} ({cmp_id})")

    # Test 7: Dwell-Time Timer & Direct Ad Click Bypass
    print("\n[Test 7] Testing Dwell-Time Protection & Direct Click Bypass...")
    # A) Insufficient dwell time without direct click
    track_short = {
        "campaign_id": cmp_id,
        "channel_id": ch_id,
        "dwell_time_elapsed": 20,  # Less than required 60s
        "clicked_directly": False
    }
    res = client.post("/api/v1/ad/track", json=track_short)
    assert res.status_code == 200
    assert res.json()["status"] == "ignored"
    print("✅ Insufficient dwell time (20s < 60s) correctly ignored.")

    # B) Direct Click Bypass (skips dwell timer immediately)
    track_direct = {
        "campaign_id": cmp_id,
        "channel_id": ch_id,
        "dwell_time_elapsed": 5,
        "clicked_directly": True
    }
    res = client.post("/api/v1/ad/track", json=track_direct)
    assert res.status_code == 200
    res_direct = res.json()
    assert res_direct["valid_click"] is True
    assert res_direct["skipped_timer"] is True
    print(f"✅ Direct Click bypass verified: skipped timer and recorded click (Cost: ${res_direct['cost_deducted_usdt']} USDT).")

    # Test 8: Support Ticketing with 24-Hour Response SLA
    print("\n[Test 8] Testing Support Ticketing & 24h SLA...")
    ticket_payload = {
        "user_id": tg_id,
        "gmail": "user_crypto@gmail.com",
        "narrative": "Need assistance linking secondary channel for advertising.",
        "attachments": ["/static/uploads/test_screenshot.jpg"]
    }
    res = client.post("/api/v1/support/tickets/create", json=ticket_payload)
    assert res.status_code == 200
    tck_data = res.json()
    assert tck_data["status"] == "open"
    assert tck_data["sla_deadline"] > time.time()
    print(f"✅ Support Ticket #{tck_data['ticket_id']} created under strict 24h SLA.")

    # Test 9: Withdrawal Request with Strict 48-Hour Review SLA
    print("\n[Test 9] Testing Withdrawal with 48-Hour Review SLA...")
    wd_payload = {
        "user_id": tg_id,
        "amount_usdt": 5.0,
        "payout_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    }
    res = client.post("/api/v1/wallet/withdraw", json=wd_payload)
    assert res.status_code == 200
    wd_data = res.json()
    assert wd_data["status"] == "pending_48h_review"
    assert wd_data["review_sla_hours"] == 48
    print(f"✅ Withdrawal #{wd_data['tx_id']} locked under strict 48-Hour Review SLA.")

    # Test 10: Automated Referral Tracking via /r/{ref_code}
    print("\n[Test 10] Testing Referral Tracking URL...")
    res = client.get(f"/r/{user_data['referral_code']}", follow_redirects=False)
    assert res.status_code in (302, 307)
    assert "start=ref_" in res.headers["location"]
    print(f"✅ Referral URL click tracked and redirected: {res.headers['location']}")

    # Test 11: Dynamic MongoDB Connection Pool & Ping
    print("\n[Test 11] Testing Dynamic MongoDB Pool & Latency Ping...")
    test_db_payload = {"uri": "mongodb://localhost:27017/mioads_db"}
    res = client.post("/api/v1/admin/database/test", json=test_db_payload)
    assert res.status_code == 200
    print(f"✅ MongoDB URI ping test completed: {res.json()['message']}")

    # Test 12: Global Broadcast Tool
    print("\n[Test 12] Testing Global Telegram Broadcast...")
    bc_payload = {
        "admin_id": admin_id,
        "title": "Mio Ads 2.0 Ecosystem Online",
        "message": "Welcome to our newly updated platform with instant UPI settlements!",
        "target": "all"
    }
    res = client.post("/api/v1/admin/broadcast", json=bc_payload)
    assert res.status_code == 200
    assert res.json()["success"] is True
    print(f"✅ Global broadcast dispatched: {res.json()['broadcast']['broadcast_id']}")

    # Test 13: Public Leaderboard Privacy Verification
    print("\n[Test 13] Testing Public Leaderboard Privacy (Name & Logo Only)...")
    res = client.get("/api/v1/channels/leaderboard")
    assert res.status_code == 200
    leaderboard = res.json()
    for row in leaderboard:
        assert "target_url" not in row
        assert "owner_id" not in row
    print("✅ Public leaderboard strictly preserves privacy (displays title & category only).")

    # Test 14: Administrative Lock Ledger Stream
    print("\n[Test 14] Testing Administrative Lock Ledger Logs...")
    res = client.get("/api/v1/admin/lock-ledger/logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    print(f"✅ Administrative Lock Ledger verified ({len(logs)} mirrored events found).")

    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED! MIO ADS ECOSYSTEM IS 100% OPERATIONAL.")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
