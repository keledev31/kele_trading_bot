"""
Telegram bot command handlers (aiogram 3.x)

Implements all user-facing commands and button handlers.
Status: Phase 2 of development
"""

from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from database import get_db_session
from database.models import User, SubscriptionPlan
from keyboards import get_main_menu_keyboard, get_signal_keyboard
from config.constants import RISK_DISCLAIMER
import logging

router = Router()
logger = logging.getLogger(__name__)


# FSM States for multi-step commands
class AddKeysStates(StatesGroup):
    waiting_for_exchange = State()
    waiting_for_api_key = State()
    waiting_for_api_secret = State()
    waiting_for_passphrase = State()


class SettingsStates(StatesGroup):
    waiting_for_risk_percentage = State()
    waiting_for_confirmation = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Handle /start command - register user and show main menu"""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    first_name = message.from_user.first_name or ""

    # Clear any existing state
    await state.clear()

    # Register user in database if not exists
    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            user = User(
                telegram_user_id=str(user_id),
                username=username,
                first_name=first_name,
                subscription_plan=SubscriptionPlan.FREE
            )
            session.add(user)
            session.commit()
            logger.info(f"New user registered: {username} ({user_id})")

        welcome_text = (
            f"🤖 Welcome to MeshTradeBot, {first_name or username}!\n\n"
            "I'm your AI-powered crypto trading assistant.\n"
            "Choose an option from the menu below:"
        )

        await message.reply(welcome_text, reply_markup=get_main_menu_keyboard())
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        await message.reply("❌ Error occurred. Please try again.")
    finally:
        session.close()


@router.message(Command("buy"))
async def cmd_buy(message: types.Message):
    """Handle /buy command - show latest buy signals"""
    user_id = message.from_user.id

    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            await message.reply("❌ User not found. Please use /start first.")
            return

        if not user.is_premium():
            await message.reply(
                "💎 This feature requires a Premium subscription.\n\n"
                "Use /subscribe to upgrade.",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # TODO: Fetch real signals from Freqtrade in Phase 4
        # For now, show placeholder
        signals_text = (
            "📈 Latest Buy Signals:\n\n"
            "🔹 BTC/USDT - Entry: $43,250\n"
            "   📊 Confidence: 85%\n"
            "   🎯 Target: $44,500 | Stop: $42,100\n\n"
            "🔹 ETH/USDT - Entry: $2,650\n"
            "   📊 Confidence: 78%\n"
            "   🎯 Target: $2,750 | Stop: $2,580\n\n"
            f"{RISK_DISCLAIMER}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_buy_signals")],
            [InlineKeyboardButton(text="📊 My Trades", callback_data="view_my_trades")]
        ])

        await message.reply(signals_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in buy command: {e}")
        await message.reply("❌ Error fetching signals. Please try again.")
    finally:
        session.close()


@router.message(Command("sell"))
async def cmd_sell(message: types.Message):
    """Handle /sell command - show latest sell signals"""
    user_id = message.from_user.id

    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            await message.reply("❌ User not found. Please use /start first.")
            return

        if not user.is_premium():
            await message.reply(
                "💎 This feature requires a Premium subscription.\n\n"
                "Use /subscribe to upgrade.",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # TODO: Fetch real signals from Freqtrade in Phase 4
        signals_text = (
            "📉 Latest Sell Signals:\n\n"
            "🔹 ADA/USDT - Entry: $0.45\n"
            "   📊 Confidence: 82%\n"
            "   🎯 Target: $0.42 | Stop: $0.47\n\n"
            f"{RISK_DISCLAIMER}"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_sell_signals")],
            [InlineKeyboardButton(text="📊 My Trades", callback_data="view_my_trades")]
        ])

        await message.reply(signals_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in sell command: {e}")
        await message.reply("❌ Error fetching signals. Please try again.")
    finally:
        session.close()


@router.message(Command("mytrades"))
async def cmd_mytrades(message: types.Message):
    """Handle /mytrades command - show user's trade history"""
    user_id = message.from_user.id

    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            await message.reply("❌ User not found. Please use /start first.")
            return

        # TODO: Fetch real trade history in Phase 6
        trades_text = (
            "📊 Your Trade History:\n\n"
            "🔹 BTC/USDT - BUY - $43,250\n"
            "   📅 2024-01-15 | 💰 +2.3%\n\n"
            "🔹 ETH/USDT - SELL - $2,650\n"
            "   📅 2024-01-14 | 💰 -1.1%\n\n"
            "📈 Total P&L: +1.2%\n"
            "💼 Win Rate: 60%"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📈 Performance", callback_data="view_performance")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh_trades")]
        ])

        await message.reply(trades_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in mytrades command: {e}")
        await message.reply("❌ Error fetching trade history. Please try again.")
    finally:
        session.close()


@router.message(Command("performance"))
async def cmd_performance(message: types.Message):
    """Handle /performance command - show trading performance stats"""
    user_id = message.from_user.id

    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            await message.reply("❌ User not found. Please use /start first.")
            return

        # TODO: Calculate real performance metrics in Phase 8
        performance_text = (
            "📈 Trading Performance:\n\n"
            "💰 Total P&L: +$1,250 (5.2%)\n"
            "📊 Win Rate: 62%\n"
            "🎯 Avg. Trade Duration: 4.2 hours\n"
            "📅 Total Trades: 47\n\n"
            "📊 Monthly Breakdown:\n"
            "• January: +3.1%\n"
            "• December: +2.8%\n"
            "• November: -1.4%\n\n"
            "🎖️ Best Trade: +8.5% (BTC/USDT)\n"
            "⚠️ Worst Trade: -2.1% (ADA/USDT)"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Detailed Stats", callback_data="detailed_stats")],
            [InlineKeyboardButton(text="📈 Charts", callback_data="performance_charts")]
        ])

        await message.reply(performance_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in performance command: {e}")
        await message.reply("❌ Error fetching performance data. Please try again.")
    finally:
        session.close()


@router.message(Command("subscribe"))
async def cmd_subscribe(message: types.Message):
    """Handle /subscribe command - show subscription options"""
    subscribe_text = (
        "💎 Premium Subscription Plans:\n\n"
        "🔹 **Monthly Plan**: ₦3,000/month\n"
        "   ✅ Real-time signals\n"
        "   ✅ Auto-trading\n"
        "   ✅ Copy trading\n"
        "   ✅ Priority support\n\n"
        "🔹 **Yearly Plan**: ₦25,000/year (30% savings)\n"
        "   ✅ All monthly features\n"
        "   ✅ Advanced analytics\n"
        "   ✅ Custom strategies\n\n"
        "💳 Secure payment via Telegram Payments"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Subscribe Monthly", callback_data="subscribe_monthly")],
        [InlineKeyboardButton(text="💎 Subscribe Yearly", callback_data="subscribe_yearly")],
        [InlineKeyboardButton(text="❓ Learn More", callback_data="subscription_info")]
    ])

    await message.reply(subscribe_text, reply_markup=keyboard)


@router.message(Command("addkeys"))
async def cmd_addkeys(message: types.Message, state: FSMContext):
    """Handle /addkeys command - start API key setup process"""
    user_id = message.from_user.id

    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            await message.reply("❌ User not found. Please use /start first.")
            return

        if not user.is_premium():
            await message.reply(
                "💎 This feature requires a Premium subscription.\n\n"
                "Use /subscribe to upgrade.",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # Start FSM for adding keys
        await state.set_state(AddKeysStates.waiting_for_exchange)

        exchange_keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Binance"), KeyboardButton(text="Bybit")],
                [KeyboardButton(text="OKX"), KeyboardButton(text="KuCoin")],
                [KeyboardButton(text="Cancel")]
            ],
            resize_keyboard=True
        )

        await message.reply(
            "🔑 Add Exchange API Keys\n\n"
            "Select your exchange:",
            reply_markup=exchange_keyboard
        )
    except Exception as e:
        logger.error(f"Error in addkeys command: {e}")
        await message.reply("❌ Error starting key setup. Please try again.")
    finally:
        session.close()


@router.message(Command("automode"))
async def cmd_automode(message: types.Message):
    """Handle /automode command - toggle auto-trading"""
    user_id = message.from_user.id

    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            await message.reply("❌ User not found. Please use /start first.")
            return

        if not user.is_premium():
            await message.reply(
                "💎 This feature requires a Premium subscription.\n\n"
                "Use /subscribe to upgrade.",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # Toggle auto-trading
        user.auto_trade_enabled = not user.auto_trade_enabled
        session.commit()

        status = "ENABLED ✅" if user.auto_trade_enabled else "DISABLED ❌"
        risk_note = f"\n\n⚠️ Current risk setting: {user.risk_percentage}% per trade"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⚙️ Change Risk %", callback_data="change_risk")],
            [InlineKeyboardButton(text="📊 View Settings", callback_data="view_settings")]
        ])

        await message.reply(
            f"🤖 Auto-Trading: {status}{risk_note}\n\n"
            "When enabled, the bot will automatically execute trades based on signals.",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Error in automode command: {e}")
        await message.reply("❌ Error toggling auto-mode. Please try again.")
    finally:
        session.close()


@router.message(Command("copytrade"))
async def cmd_copytrade(message: types.Message):
    """Handle /copytrade command - copy trading settings"""
    user_id = message.from_user.id

    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            await message.reply("❌ User not found. Please use /start first.")
            return

        if not user.is_premium():
            await message.reply(
                "💎 This feature requires a Premium subscription.\n\n"
                "Use /subscribe to upgrade.",
                reply_markup=get_main_menu_keyboard()
            )
            return

        # TODO: Implement copy trading setup in Phase 7
        copy_text = (
            "👥 Copy Trading Setup\n\n"
            "Copy trades from successful master accounts automatically.\n\n"
            "🔹 **How it works:**\n"
            "• Mirror trades from pro traders\n"
            "• Automatic position sizing\n"
            "• Risk management applied\n\n"
            "⚠️ Feature coming in Phase 7"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 View Masters", callback_data="view_masters")],
            [InlineKeyboardButton(text="⚙️ Configure", callback_data="configure_copy")]
        ])

        await message.reply(copy_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in copytrade command: {e}")
        await message.reply("❌ Error accessing copy trading. Please try again.")
    finally:
        session.close()


@router.message(Command("support"))
async def cmd_support(message: types.Message):
    """Handle /support command - show support information"""
    support_text = (
        "🆘 Support & Help\n\n"
        "📧 **Email:** support@meshtradebot.com\n"
        "💬 **Telegram:** @MeshTradeBotSupport\n"
        "📖 **Documentation:** https://docs.meshtradebot.com\n\n"
        "⏰ **Response Time:** 24 hours\n\n"
        "❓ **Common Issues:**\n"
        "• Bot not responding? Try /start\n"
        "• Signals not appearing? Check subscription\n"
        "• API key issues? Use /addkeys\n\n"
        f"{RISK_DISCLAIMER}"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Contact Support", url="https://t.me/MeshTradeBotSupport")],
        [InlineKeyboardButton(text="📖 Documentation", url="https://docs.meshtradebot.com")]
    ])

    await message.reply(support_text, reply_markup=keyboard)


@router.message(Command("settings"))
async def cmd_settings(message: types.Message, state: FSMContext):
    """Handle /settings command - show user settings"""
    user_id = message.from_user.id

    session = get_db_session()
    try:
        user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
        if not user:
            await message.reply("❌ User not found. Please use /start first.")
            return

        settings_text = (
            "⚙️ Your Settings:\n\n"
            f"👤 **User:** {user.first_name or user.username}\n"
            f"💎 **Plan:** {user.subscription_plan.value.title()}\n"
            f"📊 **Risk %:** {user.risk_percentage}%\n"
            f"🤖 **Auto-Trading:** {'✅ Enabled' if user.auto_trade_enabled else '❌ Disabled'}\n"
            f"👥 **Copy Trading:** {'✅ Enabled' if user.copy_trading_enabled else '❌ Disabled'}\n"
            f"📡 **Signals:** {'✅ Enabled' if user.receive_signals else '❌ Disabled'}\n\n"
            "Select what to change:"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Risk %", callback_data="change_risk")],
            [InlineKeyboardButton(text="🤖 Auto-Trading", callback_data="toggle_auto")],
            [InlineKeyboardButton(text="👥 Copy Trading", callback_data="toggle_copy")],
            [InlineKeyboardButton(text="📡 Signals", callback_data="toggle_signals")]
        ])

        await message.reply(settings_text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in settings command: {e}")
        await message.reply("❌ Error loading settings. Please try again.")
    finally:
        session.close()


# Button handlers (text-based buttons from keyboard)
@router.message(F.text == "📈 Buy Signals")
async def btn_buy_signals(message: types.Message):
    await cmd_buy(message)

@router.message(F.text == "📉 Sell Signals")
async def btn_sell_signals(message: types.Message):
    await cmd_sell(message)

@router.message(F.text == "📊 My Trades")
async def btn_my_trades(message: types.Message):
    await cmd_mytrades(message)

@router.message(F.text == "📈 Performance")
async def btn_performance(message: types.Message):
    await cmd_performance(message)

@router.message(F.text == "💎 Subscribe")
async def btn_subscribe(message: types.Message):
    await cmd_subscribe(message)

@router.message(F.text == "🔑 Add Keys")
async def btn_add_keys(message: types.Message, state: FSMContext):
    await cmd_addkeys(message, state)

@router.message(F.text == "🤖 Auto Mode")
async def btn_auto_mode(message: types.Message):
    await cmd_automode(message)

@router.message(F.text == "👥 Copy Trade")
async def btn_copy_trade(message: types.Message):
    await cmd_copytrade(message)

@router.message(F.text == "⚙️ Settings")
async def btn_settings(message: types.Message, state: FSMContext):
    await cmd_settings(message, state)

@router.message(F.text == "🆘 Support")
async def btn_support(message: types.Message):
    await cmd_support(message)


# Inline keyboard callback handlers
@router.callback_query(F.data == "refresh_buy_signals")
async def callback_refresh_buy(callback: types.CallbackQuery):
    await callback.answer("🔄 Refreshing signals...")
    # TODO: Implement signal refresh
    await callback.message.edit_text("Signals refreshed! (Feature coming soon)")

@router.callback_query(F.data == "refresh_sell_signals")
async def callback_refresh_sell(callback: types.CallbackQuery):
    await callback.answer("🔄 Refreshing signals...")
    # TODO: Implement signal refresh
    await callback.message.edit_text("Signals refreshed! (Feature coming soon)")

@router.callback_query(F.data == "view_my_trades")
async def callback_view_trades(callback: types.CallbackQuery):
    await callback.answer()
    # Redirect to mytrades command
    await cmd_mytrades(callback.message)

@router.callback_query(F.data == "view_performance")
async def callback_view_performance(callback: types.CallbackQuery):
    await callback.answer()
    # Redirect to performance command
    await cmd_performance(callback.message)

# TODO: Add more callback handlers for subscription, settings, etc. in Phase 3+
