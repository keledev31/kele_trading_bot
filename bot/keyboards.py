"""
Telegram inline keyboards and button layouts (aiogram 3.x)

Provides all keyboard layouts for the bot interface.
Status: Phase 2 of development
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Main menu keyboard with all primary options"""
    keyboard = [
        [KeyboardButton(text="📈 Buy Signals"), KeyboardButton(text="📉 Sell Signals")],
        [KeyboardButton(text="📊 My Trades"), KeyboardButton(text="📈 Performance")],
        [KeyboardButton(text="💎 Subscribe"), KeyboardButton(text="🔑 Add Keys")],
        [KeyboardButton(text="🤖 Auto Mode"), KeyboardButton(text="👥 Copy Trade")],
        [KeyboardButton(text="⚙️ Settings"), KeyboardButton(text="🆘 Support")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_exchange_selection_keyboard() -> ReplyKeyboardMarkup:
    """Keyboard for selecting exchange during API key setup"""
    keyboard = [
        [KeyboardButton(text="Binance"), KeyboardButton(text="Bybit")],
        [KeyboardButton(text="OKX"), KeyboardButton(text="KuCoin")],
        [KeyboardButton(text="Cancel")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


def get_signal_action_keyboard(signal_type: str, symbol: str) -> InlineKeyboardMarkup:
    """Inline keyboard for signal actions (confirm/ignore)"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Confirm Trade", callback_data=f"confirm_{signal_type}_{symbol}")],
        [InlineKeyboardButton(text="❌ Ignore", callback_data=f"ignore_{signal_type}_{symbol}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """Subscription plan selection keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="💳 Monthly - ₦3,000", callback_data="subscribe_monthly")],
        [InlineKeyboardButton(text="💎 Yearly - ₦25,000", callback_data="subscribe_yearly")],
        [InlineKeyboardButton(text="❓ Learn More", callback_data="subscription_info")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Settings management keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Risk %", callback_data="change_risk")],
        [InlineKeyboardButton(text="🤖 Auto-Trading", callback_data="toggle_auto")],
        [InlineKeyboardButton(text="👥 Copy Trading", callback_data="toggle_copy")],
        [InlineKeyboardButton(text="📡 Signals", callback_data="toggle_signals")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_trade_management_keyboard() -> InlineKeyboardMarkup:
    """Trade management and monitoring keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_trades")],
        [InlineKeyboardButton(text="📊 Performance", callback_data="view_performance")],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="trade_settings")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_copy_trading_keyboard() -> InlineKeyboardMarkup:
    """Copy trading configuration keyboard"""
    keyboard = [
        [InlineKeyboardButton(text="📋 View Masters", callback_data="view_masters")],
        [InlineKeyboardButton(text="⚙️ Configure", callback_data="configure_copy")],
        [InlineKeyboardButton(text="📊 My Copy Stats", callback_data="copy_stats")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Admin panel keyboard (for admin users only)"""
    keyboard = [
        [InlineKeyboardButton(text="📊 Bot Stats", callback_data="admin_stats")],
        [InlineKeyboardButton(text="👥 User Management", callback_data="admin_users")],
        [InlineKeyboardButton(text="💰 Revenue", callback_data="admin_revenue")],
        [InlineKeyboardButton(text="🔧 System", callback_data="admin_system")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard(action: str, data: str = "") -> InlineKeyboardMarkup:
    """Generic confirmation keyboard for dangerous actions"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Confirm", callback_data=f"confirm_{action}_{data}")],
        [InlineKeyboardButton(text="❌ Cancel", callback_data=f"cancel_{action}_{data}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_pagination_keyboard(current_page: int, total_pages: int, prefix: str) -> InlineKeyboardMarkup:
    """Pagination keyboard for lists that span multiple pages"""
    keyboard = []

    # Navigation buttons
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"{prefix}_page_{current_page-1}"))

    nav_buttons.append(InlineKeyboardButton(text=f"📄 {current_page}/{total_pages}", callback_data="noop"))

    if current_page < total_pages:
        nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"{prefix}_page_{current_page+1}"))

    keyboard.append(nav_buttons)

    # Action buttons
    action_buttons = [
        InlineKeyboardButton(text="🔄 Refresh", callback_data=f"{prefix}_refresh"),
        InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")
    ]
    keyboard.append(action_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Simple cancel keyboard for multi-step operations"""
    keyboard = [
        [InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_operation")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
