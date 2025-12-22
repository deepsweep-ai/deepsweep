"""
Pricing and tier management.

Tiers:
- FREE: 100 scans/month, 3 projects, basic features
- PRO ($20/month): Unlimited scans, SARIF export, API access
- TEAM ($15/user/month): Pro + team dashboard
- ENTERPRISE: Custom pricing

Stripe Integration:
- Production and development price IDs configured
- Webhook endpoints at api.deepsweep.ai
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Tuple, Dict

from deepsweep_ai.config import Config, Tier, TierLimits


# Stripe Price Configuration
# Environment determines which price IDs to use

@dataclass
class StripePrices:
    """Stripe price IDs for a given environment."""
    pro_monthly: str
    pro_annual: str
    team_monthly: str
    team_annual: str
    webhook_endpoint: str


# Production Stripe Prices
STRIPE_PRICES_PROD = StripePrices(
    pro_monthly="price_1Sf7qOLLFqn3U97Pc8oztYVn",
    pro_annual="price_1Sf7qvLLFqn3U97PuMvwoRrZ",
    team_monthly="price_1Sf843LLFqn3U97P7f11YWwU",
    team_annual="price_1Sf843LLFqn3U97PbUu7lEwc",
    webhook_endpoint="https://api.deepsweep.ai/prod/webhooks/stripe",
)

# Development Stripe Prices
STRIPE_PRICES_DEV = StripePrices(
    pro_monthly="price_1Sf8NNLLFqn3U97PCJOmbl8P",
    pro_annual="price_1Sf8O1LLFqn3U97P9RpVB0KC",
    team_monthly="price_1Sf8R3LLFqn3U97P669XyPSU",
    team_annual="price_1Sf8R3LLFqn3U97PRbFNYk5l",
    webhook_endpoint="https://api-dev.deepsweep.ai/dev/webhooks/stripe",
)

# Stripe Product IDs
STRIPE_PRODUCTS = {
    "prod": {
        "pro": "prod_TUo9W5meTIaTh0",
        "team": "prod_TcMnNP3zmF1Vwe",
    },
    "dev": {
        "pro": "prod_TUoTtII1F6OJi4",
        "team": "prod_TcNBbQ1EHhMnFs",
    },
}


def get_stripe_prices() -> StripePrices:
    """Get Stripe prices for current environment."""
    env = os.environ.get("DEEPSWEEP_ENV", "prod").lower()
    if env in ("dev", "development", "staging"):
        return STRIPE_PRICES_DEV
    return STRIPE_PRICES_PROD


def get_checkout_url(tier: Tier, annual: bool = False) -> str:
    """
    Get Stripe checkout URL for a given tier.

    Args:
        tier: The pricing tier (PRO or TEAM)
        annual: Whether to use annual pricing

    Returns:
        Checkout URL for the tier
    """
    prices = get_stripe_prices()
    base_url = "https://deepsweep.ai/checkout"

    if tier == Tier.PRO:
        price_id = prices.pro_annual if annual else prices.pro_monthly
    elif tier == Tier.TEAM:
        price_id = prices.team_annual if annual else prices.team_monthly
    else:
        return "https://deepsweep.ai/pricing"

    return f"{base_url}?price={price_id}"


def check_tier_limits(config: Config) -> Tuple[bool, str]:
    """
    Check if current usage is within tier limits.

    Returns:
        Tuple of (is_ok, message)
    """
    limits = TierLimits.for_tier(config.tier)

    # For MVP, we don't enforce limits strictly
    # Just return True with informational message

    if config.tier == Tier.FREE:
        return True, "Free tier: 100 scans/month remaining"

    return True, f"{config.tier.value.title()} tier active"


def get_upgrade_message() -> str:
    """Get upgrade prompt message."""
    return """
Pro: Unlimited scans, SARIF export, API access.
https://deepsweep.ai/pro
"""


def get_pricing_table() -> str:
    """Get pricing comparison table."""
    return """
┌─────────────────┬─────────────┬─────────────┬─────────────┐
│ Feature         │ Free        │ Pro $20/mo  │ Team $15/u  │
├─────────────────┼─────────────┼─────────────┼─────────────┤
│ Scans/month     │ 100         │ Unlimited   │ Unlimited   │
│ Projects        │ 3           │ Unlimited   │ Unlimited   │
│ SARIF export    │ -           │ Yes         │ Yes         │
│ API access      │ -           │ Yes         │ Yes         │
│ Team dashboard  │ -           │ -           │ Yes         │
│ Support         │ Community   │ Email       │ Priority    │
└─────────────────┴─────────────┴─────────────┴─────────────┘
"""


def get_tier_features(tier: Tier) -> Dict[str, bool]:
    """Get feature availability for a tier."""
    limits = TierLimits.for_tier(tier)
    return {
        "unlimited_scans": limits.scans_per_month == -1,
        "sarif_export": limits.sarif_export,
        "api_access": limits.api_access,
        "priority_support": limits.priority_support,
        "team_dashboard": tier in (Tier.TEAM, Tier.ENTERPRISE),
    }
