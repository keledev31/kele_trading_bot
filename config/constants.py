"""
Global constants for MeshTradeBot.
"""

# Subscription Plans & Pricing
SUBSCRIPTION_PLANS = {
    "FREE": {
        "price": 0,
        "currency": "NGN",
        "features": [
            "Basic signals",
            "Up to 24 hours signal history",
            "Limited to 1 trade log view"
        ]
    },
    "PREMIUM_MONTHLY": {
        "price": 3000,  # Nigerian Naira
        "currency": "NGN",
        "duration_days": 30,
        "features": [
            "All Free features",
            "Direct trading capability",
            "Copy trading setup",
            "Full trade history",
            "Performance analytics",
            "Priority support"
        ]
    },
    "PREMIUM_YEARLY": {
        "price": 25000,  # Nigerian Naira
        "currency": "NGN",
        "duration_days": 365,
        "features": [
            "All Premium Monthly features",
            "33% discount vs monthly",
            "Advanced analytics"
        ]
    }
}

# Trading Configuration
MAX_OPEN_TRADES = 3
DEFAULT_RISK_PERCENTAGE = 1.0  # % of account per trade
MAX_DAILY_DRAWDOWN = -5.0  # -5% triggers pause
MAX_STOP_LOSS_PERCENTAGE = 3.0  # Hard limit

# Supported Exchanges
SUPPORTED_EXCHANGES = [
    "binance",
    "bybit",
    "okx",
    "kraken",
    "kucoin"
]

# Trading Pairs (Default Whitelist)
DEFAULT_TRADING_PAIRS = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "ADA/USDT",
    "XRP/USDT"
]

# Signal Configuration
SIGNAL_EXPIRE_HOURS = 24
MIN_CONFIDENCE_SCORE = 50  # Minimum FreqAI confidence to send signal
MAX_SIGNALS_PER_HOUR = 10  # Rate limit

# Copy Trading Settings
MIN_COPY_RISK_PERCENTAGE = 0.5
MAX_COPY_RISK_PERCENTAGE = 2.0

# Risk Management Disclaimers
RISK_DISCLAIMER = """
⚠️ **TRADING DISCLAIMER** ⚠️

Trading cryptocurrencies involves substantial risk of loss. Your losses can exceed your initial investment.

🔴 MeshTradeBot is NOT financial advice. 
🔴 Past performance does not guarantee future results.
🔴 Start with small amounts you can afford to lose.
🔴 Use this bot at your own risk - we are not liable for losses.

✅ Always verify signals before trading manually.
✅ Use stop-losses on all trades.
✅ Diversify your portfolio.
✅ Never invest money you can't afford to lose.

By using MeshTradeBot, you acknowledge these risks.
"""

# Telegram UI Configuration
EMOJI_MAP = {
    "buy": "🟢",
    "sell": "🔴",
    "signal": "📊",
    "trade": "💰",
    "profit": "📈",
    "loss": "📉",
    "warning": "⚠️",
    "success": "✅",
    "error": "❌",
    "info": "ℹ️",
    "lock": "🔒",
    "unlock": "🔓",
    "settings": "⚙️",
    "history": "📜",
    "trending": "🚀",
    "risk": "☢️",
    "pause": "⏸️",
    "play": "▶️",
    "copy": "📋",
}

# API Configuration
WEBHOOK_TIMEOUT = 30  # seconds
FREQTRADE_API_TIMEOUT = 10  # seconds
SIGNAL_SEND_RETRY_COUNT = 3
SIGNAL_SEND_RETRY_DELAY = 5  # seconds

# Database Configuration
DB_BACKUP_INTERVAL_HOURS = 24
DB_AUTO_VACUUM = True

# Logging
SENSITIVE_FIELDS = [
    "api_key",
    "secret",
    "password",
    "token",
    "private_key"
]

# Feature Flags
ENABLE_FREQAI = True  # Use FreqAI for confidence scoring
ENABLE_COPY_TRADING = True
ENABLE_DIRECT_TRADING = True
ENABLE_PAYMENTS = True

# Rate Limiting
USER_COMMAND_RATE_LIMIT = 30  # seconds between commands
USER_TRADE_RATE_LIMIT = 60  # seconds between trades

print("✓ Constants loaded successfully")
