"""
Pydantic Schemas and Domain Models for Mio Ads Telegram Mini App Ecosystem
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# User & Profile
class UserRegisterRequest(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    preferred_currency: Optional[str] = "USDT"
    language: Optional[str] = "en"
    referred_by: Optional[str] = None

class UserProfileResponse(BaseModel):
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    role: str
    preferred_currency: str
    language: str
    wallet_balance_usdt: float
    wallet_balance_inr: float
    api_key: str
    referral_code: str
    total_referral_clicks: int = 0
    is_affiliate_approved: bool = False
    created_at: float

# Channel Management
class ChannelCreateRequest(BaseModel):
    telegram_id: int
    title: str
    username: str
    type: str = Field(..., description="'promotion' or 'monetization'")
    category: str
    subscribers: int = Field(default=1000, ge=100)

class ChannelModerationRequest(BaseModel):
    admin_id: int
    channel_id: str
    action: str = Field(..., description="'approved' or 'rejected'")
    notes: Optional[str] = None

# Advertising Campaign
class CampaignCreateRequest(BaseModel):
    advertiser_id: int
    title: str
    narrative: str
    target_url: str
    banner_url: Optional[str] = "/static/images/logo.png"
    model: str = Field(..., description="'CPC' or 'CPM'")
    bid_usdt: float = Field(..., gt=0)
    budget_usdt: float = Field(..., ge=5.0)
    dwell_time_seconds: int = Field(default=60, ge=30, le=120)

# Deposit & Withdrawal
class DepositRequest(BaseModel):
    user_id: int
    currency: str = Field(..., description="'INR' or 'USDT'")
    amount: float = Field(..., gt=0)
    payment_method: str = Field(default="UPI", description="'UPI' or 'USDT_TRC20'")
    utr_or_txid: Optional[str] = None

class WithdrawalRequest(BaseModel):
    user_id: int
    amount_usdt: float = Field(..., ge=5.0)
    payout_address: str
    currency: str = "USDT"

class WithdrawalModerationRequest(BaseModel):
    admin_id: int
    tx_id: str
    action: str = Field(..., description="'approved' or 'rejected'")

# Support Tickets
class TicketCreateRequest(BaseModel):
    user_id: int
    gmail: str
    narrative: str
    attachments: Optional[List[str]] = []

class TicketResponseRequest(BaseModel):
    admin_id: int
    ticket_id: str
    response_text: str

# Affiliate Program
class AffiliateApplyRequest(BaseModel):
    user_id: int
    traffic_source: str
    estimated_volume: str
    notes: Optional[str] = None

class AffiliateModerationRequest(BaseModel):
    admin_id: int
    user_id: int
    action: str = Field(..., description="'approved' or 'rejected'")
    custom_per_click_rate_usdt: Optional[float] = None

# Admin System Config
class SystemSettingsUpdateRequest(BaseModel):
    admin_id: int
    platform_fee_percent: Optional[float] = None
    usdt_to_inr_rate: Optional[float] = None
    affiliate_click_rate_usdt: Optional[float] = None
    default_dwell_time_seconds: Optional[int] = None
    lock_channel_id: Optional[str] = None

class DatabaseSwitchRequest(BaseModel):
    admin_id: int
    uri_index: Optional[int] = 0
    custom_uri: Optional[str] = None

class DatabaseTestRequest(BaseModel):
    uri: str

class BroadcastRequest(BaseModel):
    admin_id: int
    title: str
    message: str
    target: str = Field(default="all", description="'all', 'publishers', 'advertisers'")
    action_url: Optional[str] = None

# Ad Tracking
class AdImpressionTrackRequest(BaseModel):
    campaign_id: str
    channel_id: Optional[str] = None
    dwell_time_elapsed: int = 0
    clicked_directly: bool = False
    visitor_ip: Optional[str] = None
    user_agent: Optional[str] = None


class AdminLoginRequest(BaseModel):
    telegram_id: int
    token: str

class AdminManageRequest(BaseModel):
    telegram_id: int

class DatabaseAddRequest(BaseModel):
    uri: str

class DatabaseRemoveRequest(BaseModel):
    db_id: str
