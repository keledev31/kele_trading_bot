"""
Database models for MeshTradeBot using SQLAlchemy.
Handles users, subscriptions, trades, API keys, and signals.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    Text, Enum as SQLEnum, ForeignKey, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class SubscriptionPlan(str, Enum):
    """Subscription tiers available"""
    FREE = "free"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_YEARLY = "premium_yearly"


class User(Base):
    """User model - stores Telegram users with subscription info"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(String(50), unique=True, nullable=False, index=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    username = Column(String(255))
    
    # Subscription
    subscription_plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE)
    subscription_expiry = Column(DateTime)  # NULL = lifetime or expired
    is_active = Column(Boolean, default=True)
    
    # Trading Preferences
    risk_percentage = Column(Float, default=1.0)  # % of trading account per trade
    auto_trade_enabled = Column(Boolean, default=False)
    copy_trading_enabled = Column(Boolean, default=False)
    
    # Premium Features
    receive_signals = Column(Boolean, default=True)
    copy_trade_master_account = Column(Boolean, default=False)  # Is this the master account?
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    api_keys = relationship("EncryptedAPIKey", back_populates="user", cascade="all, delete-orphan")
    trade_logs = relationship("TradeLog", back_populates="user", cascade="all, delete-orphan")
    signals_received = relationship("Signal", back_populates="user", cascade="all, delete-orphan")
    copy_config = relationship("CopyTradingConfig", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    def is_premium(self) -> bool:
        """Check if user has active premium subscription"""
        if self.subscription_plan == SubscriptionPlan.FREE:
            return False
        if self.subscription_expiry and self.subscription_expiry < datetime.utcnow():
            return False
        return True
    
    def days_until_expiry(self) -> int:
        """Days remaining until subscription expiry (-1 if expired)"""
        if not self.subscription_expiry:
            return -1
        days = (self.subscription_expiry - datetime.utcnow()).days
        return max(-1, days)


class EncryptedAPIKey(Base):
    """Encrypted API keys for exchanges (Binance, Bybit, OKX, etc.)"""
    __tablename__ = "encrypted_api_keys"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange = Column(String(50), nullable=False)  # 'binance', 'bybit', 'okx', etc.
    api_key_encrypted = Column(Text, nullable=False)  # Fernet encrypted
    api_secret_encrypted = Column(Text, nullable=False)  # Fernet encrypted
    
    # Optional: passphrase for some exchanges (OKX, etc.)
    passphrase_encrypted = Column(Text)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used = Column(DateTime)
    
    user = relationship("User", back_populates="api_keys")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'exchange', name='unique_user_exchange'),
    )


class Signal(Base):
    """Technical analysis signals sent to users"""
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)  # BTC/USDT, ETH/USDT, etc.
    signal_type = Column(String(10), nullable=False)  # BUY, SELL
    entry_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float, nullable=False)
    
    # FreqAI Confidence Scoring
    confidence_score = Column(Float, default=0.0)  # 0-100%
    
    # Signal Details
    technical_analysis = Column(Text)  # JSON with indicators (RSI, EMA, etc.)
    message_id = Column(String(50))  # Telegram message ID for editing
    
    is_executed = Column(Boolean, default=False)
    execution_price = Column(Float)
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, default=lambda: datetime.utcnow() + timedelta(hours=24))
    
    user = relationship("User", back_populates="signals_received")


class TradeLog(Base):
    """Executed trades log - tracks all trades made through the bot"""
    __tablename__ = "trade_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    freqtrade_trade_id = Column(String(50))  # Reference to Freqtrade's trade ID
    symbol = Column(String(20), nullable=False, index=True)
    
    # Trade Details
    side = Column(String(10), nullable=False)  # BUY, SELL
    entry_price = Column(Float, nullable=False)
    entry_amount = Column(Float, nullable=False)
    entry_cost = Column(Float, nullable=False)  # entry_price * entry_amount
    
    # Exit
    exit_price = Column(Float)
    exit_time = Column(DateTime)
    exit_reason = Column(String(50))  # 'stop_loss', 'take_profit', 'manual', 'trailing_stop'
    
    # PnL
    profit_loss = Column(Float)  # Actual profit/loss
    profit_loss_percentage = Column(Float)  # %
    
    # Risk Management
    stop_loss = Column(Float, nullable=False)
    take_profit = Column(Float)
    
    # Tracking
    is_manual = Column(Boolean, default=False)  # User executed manually or via bot?
    is_copy_trade = Column(Boolean, default=False)  # From copy trading?
    status = Column(String(20), default="open")  # open, closed, cancelled
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = Column(DateTime)
    
    user = relationship("User", back_populates="trade_logs")


class CopyTradingConfig(Base):
    """Copy trading configuration for users"""
    __tablename__ = "copy_trading_config"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Settings
    is_enabled = Column(Boolean, default=False)
    copy_from_master = Column(Boolean, default=True)
    max_risk_percentage = Column(Float, default=1.0)  # User's risk % per trade
    
    # Master Account Reference
    master_account_id = Column(String(50))  # Reference to master Freqtrade instance
    
    # Tracking
    total_copied_trades = Column(Integer, default=0)
    total_copy_pnl = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="copy_config")


class PaymentTransaction(Base):
    """Payment & subscription transaction history"""
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Transaction Details
    telegram_charge_id = Column(String(100), unique=True, nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="NGN")
    
    # Subscription Info
    subscription_plan = Column(SQLEnum(SubscriptionPlan), nullable=False)
    subscription_months = Column(Integer, default=1)  # Duration
    
    # Status
    status = Column(String(20), default="pending")  # pending, completed, failed, refunded
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    refunded_at = Column(DateTime)
    
    notes = Column(Text)  # Any additional notes


class BotStatistics(Base):
    """Daily/overall bot statistics and performance"""
    __tablename__ = "bot_statistics"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.utcnow, unique=True, index=True)
    
    # User Stats
    total_active_users = Column(Integer, default=0)
    total_premium_users = Column(Integer, default=0)
    new_users_today = Column(Integer, default=0)
    
    # Trading Stats
    total_signals_sent = Column(Integer, default=0)
    total_trades_executed = Column(Integer, default=0)
    
    # Financial Stats
    total_pnl = Column(Float, default=0.0)
    win_rate_percentage = Column(Float, default=0.0)
    
    # Performance
    average_trade_duration = Column(Float, default=0.0)  # hours
    total_revenue_ngn = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
