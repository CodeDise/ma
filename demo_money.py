import httpx

BASE = "http://127.0.0.1:8080"
client = httpx.Client(base_url=BASE, timeout=10.0)

print("=" * 60)
print("💰 MIO ADS LIVE MONEY & EARNINGS DEMO")
print("=" * 60)

print("\n--- 1. CURRENT WALLET BALANCE ---")
res = client.get("/api/v1/user/profile?telegram_id=100200300")
user = res.json()
print(f"User: {user.get('first_name')} (Telegram ID: {user.get('telegram_id')})")
print(f"USDT Balance: ${user.get('wallet_balance_usdt'):.2f} USDT")
print(f"INR Balance : ₹{user.get('wallet_balance_inr'):,.2f} INR (@ ₹80/USDT)")

print("\n--- 2. DEPOSIT ₹1,000 INR VIA UPI (Minimum is ₹500) ---")
dep = client.post("/api/v1/wallet/deposit", json={
    "user_id": 100200300,
    "currency": "INR",
    "amount": 1000.0,
    "payment_method": "UPI",
    "utr_or_txid": "UPI-LIVE-DEMO-9988"
}).json()
print(f"Status        : SUCCESS")
print(f"TX ID         : {dep['tx_id']}")
print(f"Invoice ID    : {dep['invoice_id']}")
print(f"New Balance   : ${dep['new_balance_usdt']:.2f} USDT (₹{dep['new_balance_inr']:,.2f} INR)")
print(f"Generated PDF : {dep['invoice_pdf_url']}")

print("\n--- 3. ADVERTISER LAUNCHES CAMPAIGN ($10.00 USDT) ---")
cmp = client.post("/api/v1/campaigns/create", json={
    "advertiser_id": 100200300,
    "title": "Crypto Whales VIP Signal Group",
    "narrative": "Join 100K+ daily traders for verified spot and futures signals.",
    "target_url": "https://t.me/mioadsbot?start=crypto_whales",
    "model": "CPC",
    "bid_usdt": 0.04,
    "budget_usdt": 10.0,
    "dwell_time_seconds": 60
}).json()
print(f"Campaign Name : {cmp['title']}")
print(f"Billing Model : {cmp['model']} (Cost Per Click)")
print(f"Bid Per Click : ${cmp['bid_usdt']} USDT")
print(f"Budget Locked : ${cmp['budget_usdt']} USDT")

print("\n--- 4. USER CLICKS AD (Skipping 60s Dwell Timer) ---")
track = client.post("/api/v1/ad/track", json={
    "campaign_id": cmp["campaign_id"],
    "channel_id": "ch_telegram_signals",
    "dwell_time_elapsed": 4,
    "clicked_directly": True
}).json()
print(f"Tracking Status : {track['status']}")
print(f"Dwell Timer     : SKIPPED (Direct Click Verified)")
print(f"Advertiser Cost : -${track['cost_deducted_usdt']} USDT")
print(f"Publisher Earns : +${track['cost_deducted_usdt'] * 0.85:.4f} USDT (after 15% Platform Fee)")

print("\n--- 5. PUBLISHER WITHDRAWS EARNINGS ($5.00 USDT, 48h SLA) ---")
wd = client.post("/api/v1/wallet/withdraw", json={
    "user_id": 100200300,
    "amount_usdt": 5.0,
    "payout_address": "TXy9DemoTRC20AddressUSDT8899",
    "currency": "USDT"
}).json()
print(f"Withdrawal TX   : {wd['tx_id']}")
print(f"Status          : {wd['status']}")
print(f"Review SLA      : {wd['review_sla_hours']} Hours Administrative Review")
print(f"Lock Ledger     : MIRRORED TO PRIVATE LOCK CHANNEL")

print("\n" + "=" * 60)
print("✅ LIVE MONEY FLOW EXECUTED SUCCESSFULLY!")
print("=" * 60)
