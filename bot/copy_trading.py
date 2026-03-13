"""
Copy trading module (aiogram 3.x)

Allows users to automatically copy trades from master accounts.
Features:
- Subscribe to master account signals
- Proportional position sizing
- Risk management per user
- Performance tracking
- Enable/disable per trading pair

Status: Phase 6 of development
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from database import get_db_session
from database.models import User, CopyTradingConfig, TradeLog
from bot.direct_trading import DirectTradingManager
from config.constants import RISK_DISCLAIMER

logger = logging.getLogger(__name__)


class CopyTradingManager:
    """Manages copy trading functionality"""

    def __init__(self):
        self.direct_trading = DirectTradingManager()

    def get_master_accounts(self) -> List[Dict[str, Any]]:
        """
        Get list of available master accounts for copy trading

        Returns:
            List of master account info
        """
        session = get_db_session()
        try:
            # Find users marked as master accounts
            masters = session.query(User).filter_by(copy_trade_master_account=True).all()

            master_list = []
            for master in masters:
                # Calculate performance metrics
                trades = session.query(TradeLog).filter_by(user_id=master.id).all()

                if trades:
                    total_trades = len(trades)
                    winning_trades = len([t for t in trades if t.profit_loss and t.profit_loss > 0])
                    win_rate = (winning_trades / total_trades) * 100 if total_trades > 0 else 0

                    total_pnl = sum(t.profit_loss for t in trades if t.profit_loss) or 0
                    total_pnl_percentage = sum(t.profit_loss_percentage for t in trades if t.profit_loss_percentage) or 0
                else:
                    total_trades = 0
                    win_rate = 0
                    total_pnl = 0
                    total_pnl_percentage = 0

                master_list.append({
                    "id": master.id,
                    "username": master.username,
                    "telegram_id": master.telegram_user_id,
                    "total_trades": total_trades,
                    "win_rate": round(win_rate, 1),
                    "total_pnl": round(total_pnl, 2),
                    "total_pnl_percentage": round(total_pnl_percentage, 2),
                    "risk_percentage": master.risk_percentage,
                    "is_active": master.is_active
                })

            return master_list

        finally:
            session.close()

    def subscribe_to_master(self, user_id: int, master_account_id: str, max_risk_percentage: float = 1.0) -> bool:
        """
        Subscribe user to copy trading from a master account

        Args:
            user_id: User's Telegram ID
            master_account_id: Master account identifier
            max_risk_percentage: Maximum risk per trade for this user

        Returns:
            True if subscription successful
        """
        session = get_db_session()
        try:
            user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return False

            if not user.is_premium():
                logger.error(f"User {user_id} is not premium")
                return False

            # Check if master exists
            master = session.query(User).filter_by(telegram_user_id=master_account_id).first()
            if not master or not master.copy_trade_master_account:
                logger.error(f"Master account {master_account_id} not found or not a master")
                return False

            # Create or update copy trading config
            config = session.query(CopyTradingConfig).filter_by(user_id=user.id).first()
            if not config:
                config = CopyTradingConfig(
                    user_id=user.id,
                    master_account_id=master_account_id,
                    max_risk_percentage=max_risk_percentage
                )
                session.add(config)
            else:
                config.master_account_id = master_account_id
                config.max_risk_percentage = max_risk_percentage
                config.is_enabled = True

            # Update user settings
            user.copy_trading_enabled = True

            session.commit()
            logger.info(f"User {user_id} subscribed to copy trading from master {master_account_id}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error subscribing user {user_id} to copy trading: {e}")
            return False
        finally:
            session.close()

    def unsubscribe_from_copy_trading(self, user_id: int) -> bool:
        """
        Unsubscribe user from copy trading

        Args:
            user_id: User's Telegram ID

        Returns:
            True if unsubscribed successfully
        """
        session = get_db_session()
        try:
            user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
            if not user:
                return False

            # Update user settings
            user.copy_trading_enabled = False

            # Update config
            config = session.query(CopyTradingConfig).filter_by(user_id=user.id).first()
            if config:
                config.is_enabled = False

            session.commit()
            logger.info(f"User {user_id} unsubscribed from copy trading")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"Error unsubscribing user {user_id} from copy trading: {e}")
            return False
        finally:
            session.close()

    def execute_copy_trade(self, master_trade: Dict[str, Any], user_id: int) -> bool:
        """
        Execute a copied trade for a user

        Args:
            master_trade: Master trade details
            user_id: User to copy trade for

        Returns:
            True if trade executed successfully
        """
        session = get_db_session()
        try:
            user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
            if not user or not user.copy_trading_enabled:
                return False

            config = session.query(CopyTradingConfig).filter_by(user_id=user.id).first()
            if not config or not config.is_enabled:
                return False

            # Calculate position size based on user's risk settings
            # This is a simplified calculation - in reality would need more sophisticated risk management
            master_risk = master_trade.get('risk_percentage', 1.0)
            user_risk = min(config.max_risk_percentage, user.risk_percentage)

            # Scale position size proportionally
            position_multiplier = user_risk / master_risk if master_risk > 0 else 1.0

            # Get user's API keys for trading
            api_keys = user.api_keys
            if not api_keys:
                logger.warning(f"User {user_id} has no API keys for copy trading")
                return False

            # Execute the trade using direct trading manager
            # This would need to be implemented based on the master trade details
            trade_result = self.direct_trading.execute_market_order(
                user_id=user.id,
                symbol=master_trade['symbol'],
                side=master_trade['side'],
                amount=master_trade['amount'] * position_multiplier,
                api_key_data=api_keys[0]  # Use first available API key
            )

            if trade_result:
                # Log the copied trade
                trade_log = TradeLog(
                    user_id=user.id,
                    symbol=master_trade['symbol'],
                    side=master_trade['side'],
                    entry_price=master_trade['entry_price'],
                    entry_amount=master_trade['amount'] * position_multiplier,
                    entry_cost=master_trade['entry_price'] * (master_trade['amount'] * position_multiplier),
                    stop_loss=master_trade.get('stop_loss'),
                    take_profit=master_trade.get('take_profit'),
                    is_copy_trade=True
                )
                session.add(trade_log)

                # Update copy trading stats
                config.total_copied_trades += 1

                session.commit()
                logger.info(f"Executed copy trade for user {user_id}: {master_trade['symbol']} {master_trade['side']}")
                return True
            else:
                logger.error(f"Failed to execute copy trade for user {user_id}")
                return False

        except Exception as e:
            session.rollback()
            logger.error(f"Error executing copy trade for user {user_id}: {e}")
            return False
        finally:
            session.close()

    def get_copy_trading_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get copy trading statistics for a user

        Args:
            user_id: User's Telegram ID

        Returns:
            Dict with copy trading stats
        """
        session = get_db_session()
        try:
            user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
            if not user:
                return {"error": "User not found"}

            config = session.query(CopyTradingConfig).filter_by(user_id=user.id).first()
            if not config:
                return {"enabled": False}

            # Get copy trades
            copy_trades = session.query(TradeLog).filter_by(
                user_id=user.id,
                is_copy_trade=True
            ).all()

            total_copy_trades = len(copy_trades)
            winning_trades = len([t for t in copy_trades if t.profit_loss and t.profit_loss > 0])
            win_rate = (winning_trades / total_copy_trades) * 100 if total_copy_trades > 0 else 0

            total_pnl = sum(t.profit_loss for t in copy_trades if t.profit_loss) or 0

            return {
                "enabled": config.is_enabled,
                "master_account": config.master_account_id,
                "max_risk_percentage": config.max_risk_percentage,
                "total_copied_trades": total_copy_trades,
                "win_rate": round(win_rate, 1),
                "total_pnl": round(total_pnl, 2),
                "trades": [
                    {
                        "symbol": t.symbol,
                        "side": t.side,
                        "entry_price": t.entry_price,
                        "profit_loss": t.profit_loss,
                        "profit_loss_percentage": t.profit_loss_percentage,
                        "created_at": t.created_at.isoformat()
                    } for t in copy_trades[-10:]  # Last 10 trades
                ]
            }

        finally:
            session.close()

    def broadcast_master_trade(self, master_user_id: int, trade_details: Dict[str, Any]) -> int:
        """
        Broadcast a master trade to all subscribers

        Args:
            master_user_id: Master's Telegram ID
            trade_details: Trade details to broadcast

        Returns:
            Number of users who received the trade signal
        """
        session = get_db_session()
        try:
            # Find all users subscribed to this master
            configs = session.query(CopyTradingConfig).filter_by(
                master_account_id=str(master_user_id),
                is_enabled=True
            ).all()

            broadcast_count = 0
            for config in configs:
                user = session.query(User).filter_by(id=config.user_id).first()
                if user and user.is_premium() and user.copy_trading_enabled:
                    # Execute copy trade for this user
                    if self.execute_copy_trade(trade_details, int(user.telegram_user_id)):
                        broadcast_count += 1

            logger.info(f"Broadcasted master trade to {broadcast_count} subscribers")
            return broadcast_count

        finally:
            session.close()


# Global copy trading manager instance
copy_trading_manager = CopyTradingManager()


def get_copy_trading_manager() -> CopyTradingManager:
    """Get the global copy trading manager instance"""
    return copy_trading_manager
