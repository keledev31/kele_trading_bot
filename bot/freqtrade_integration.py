"""
Freqtrade integration module (aiogram 3.x)

Handles communication with Freqtrade bot:
- Webhook signal reception
- RPC API communication
- Signal processing and filtering
- Trade execution coordination
- Strategy management

Status: Phase 4 of development
"""

import logging
import requests
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import os
from database import get_db_session
from database.models import User, Signal, TradeLog
from bot.direct_trading import get_direct_trading_manager
from bot.copy_trading import get_copy_trading_manager

logger = logging.getLogger(__name__)


class FreqtradeManager:
    """Manages Freqtrade bot integration"""

    def __init__(self):
        self.rpc_url = os.getenv("FREQTRADE_RPC_URL", "http://freqtrade:8080")
        self.jwt_secret = os.getenv("FREQTRADE_JWT_SECRET")
        self.webhook_secret = os.getenv("WEBHOOK_SECRET")

        # Initialize managers
        self.direct_trading = get_direct_trading_manager()
        self.copy_trading = get_copy_trading_manager()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for RPC calls"""
        if self.jwt_secret:
            return {"Authorization": f"Bearer {self.jwt_secret}"}
        return {}

    def test_connection(self) -> bool:
        """
        Test connection to Freqtrade RPC API

        Returns:
            True if connection successful
        """
        try:
            response = requests.get(
                f"{self.rpc_url}/api/v1/status",
                headers=self._get_auth_headers(),
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Failed to connect to Freqtrade RPC: {e}")
            return False

    def get_bot_status(self) -> Optional[Dict[str, Any]]:
        """
        Get Freqtrade bot status

        Returns:
            Bot status information or None if error
        """
        try:
            response = requests.get(
                f"{self.rpc_url}/api/v1/status",
                headers=self._get_auth_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get bot status: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting bot status: {e}")
            return None

    def get_open_trades(self) -> Optional[List[Dict[str, Any]]]:
        """
        Get open trades from Freqtrade

        Returns:
            List of open trades or None if error
        """
        try:
            response = requests.get(
                f"{self.rpc_url}/api/v1/status",
                headers=self._get_auth_headers(),
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('trade_count', 0), data.get('open_trades', [])
            else:
                logger.error(f"Failed to get open trades: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting open trades: {e}")
            return None

    def get_strategy_performance(self, strategy_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get strategy performance statistics

        Args:
            strategy_name: Specific strategy or None for all

        Returns:
            Performance data or None if error
        """
        try:
            url = f"{self.rpc_url}/api/v1/profit"
            if strategy_name:
                url += f"?strategy={strategy_name}"

            response = requests.get(
                url,
                headers=self._get_auth_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get strategy performance: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting strategy performance: {e}")
            return None

    def process_webhook_signal(self, webhook_data: Dict[str, Any], webhook_secret: str) -> bool:
        """
        Process incoming webhook signal from Freqtrade

        Args:
            webhook_data: Webhook payload
            webhook_secret: Secret for validation

        Returns:
            True if processed successfully
        """
        try:
            # Validate webhook secret
            if self.webhook_secret and webhook_secret != self.webhook_secret:
                logger.error("Invalid webhook secret")
                return False

            signal_type = webhook_data.get('signal', '').upper()
            if signal_type not in ['BUY', 'SELL']:
                logger.error(f"Invalid signal type: {signal_type}")
                return False

            symbol = webhook_data.get('pair', '')
            if not symbol:
                logger.error("No symbol in webhook data")
                return False

            # Extract signal data
            signal_data = {
                'symbol': symbol,
                'signal_type': signal_type,
                'entry_price': webhook_data.get('price', 0),
                'stop_loss': webhook_data.get('stoploss', 0),
                'take_profit': webhook_data.get('takeprofit', 0),
                'confidence_score': webhook_data.get('confidence', 50),
                'technical_analysis': json.dumps(webhook_data.get('indicators', {})),
                'strategy': webhook_data.get('strategy', 'unknown'),
                'timestamp': datetime.utcnow()
            }

            # Save signal to database
            self._save_signal(signal_data)

            # Distribute signal to users
            self._distribute_signal_to_users(signal_data)

            logger.info(f"Processed {signal_type} signal for {symbol}")
            return True

        except Exception as e:
            logger.error(f"Error processing webhook signal: {e}")
            return False

    def _save_signal(self, signal_data: Dict[str, Any]) -> Optional[int]:
        """
        Save signal to database

        Args:
            signal_data: Signal information

        Returns:
            Signal ID if saved successfully
        """
        session = get_db_session()
        try:
            # Create signal record (will be associated with users when distributed)
            signal = Signal(
                user_id=None,  # Will be set when distributed to specific users
                symbol=signal_data['symbol'],
                signal_type=signal_data['signal_type'],
                entry_price=signal_data['entry_price'],
                stop_loss=signal_data['stop_loss'],
                take_profit=signal_data['take_profit'],
                confidence_score=signal_data['confidence_score'],
                technical_analysis=signal_data['technical_analysis']
            )

            session.add(signal)
            session.commit()

            return signal.id

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving signal: {e}")
            return None
        finally:
            session.close()

    def _distribute_signal_to_users(self, signal_data: Dict[str, Any]):
        """
        Distribute signal to eligible users

        Args:
            signal_data: Signal information
        """
        session = get_db_session()
        try:
            # Get all premium users who want signals
            premium_users = session.query(User).filter_by(
                subscription_plan__in=['premium_monthly', 'premium_yearly'],
                receive_signals=True,
                is_active=True
            ).all()

            distributed_count = 0
            for user in premium_users:
                try:
                    # Create user-specific signal record
                    user_signal = Signal(
                        user_id=user.id,
                        symbol=signal_data['symbol'],
                        signal_type=signal_data['signal_type'],
                        entry_price=signal_data['entry_price'],
                        stop_loss=signal_data['stop_loss'],
                        take_profit=signal_data['take_profit'],
                        confidence_score=signal_data['confidence_score'],
                        technical_analysis=signal_data['technical_analysis']
                    )

                    session.add(user_signal)

                    # TODO: Send Telegram notification to user
                    # This would be implemented in the bot handlers

                    distributed_count += 1

                except Exception as e:
                    logger.error(f"Error distributing signal to user {user.telegram_user_id}: {e}")

            session.commit()
            logger.info(f"Distributed signal to {distributed_count} users")

        except Exception as e:
            session.rollback()
            logger.error(f"Error distributing signals: {e}")
        finally:
            session.close()

    def execute_signal_trade(self, user_id: int, signal_id: int) -> bool:
        """
        Execute a trade based on a signal for a user

        Args:
            user_id: User's Telegram ID
            signal_id: Signal ID

        Returns:
            True if trade executed successfully
        """
        session = get_db_session()
        try:
            user = session.query(User).filter_by(telegram_user_id=str(user_id)).first()
            if not user or not user.auto_trade_enabled:
                return False

            signal = session.query(Signal).filter_by(id=signal_id, user_id=user.id).first()
            if not signal or signal.is_executed:
                return False

            # Calculate position size based on user's risk settings
            # This is a simplified calculation
            risk_amount = (user.risk_percentage / 100) * 1000  # Assume $1000 account for demo
            position_size = risk_amount / signal.entry_price

            # Execute trade using direct trading
            trade_result = self.direct_trading.execute_market_order(
                user_id=user_id,
                symbol=signal.symbol,
                side=signal.signal_type.lower(),
                amount=position_size
            )

            if trade_result:
                # Mark signal as executed
                signal.is_executed = True
                signal.execution_price = signal.entry_price  # In reality, get from order result

                # Log the trade
                trade_log = TradeLog(
                    user_id=user.id,
                    symbol=signal.symbol,
                    side=signal.signal_type,
                    entry_price=signal.entry_price,
                    entry_amount=position_size,
                    entry_cost=signal.entry_price * position_size,
                    stop_loss=signal.stop_loss,
                    take_profit=signal.take_profit,
                    is_manual=False
                )

                session.add(trade_log)
                session.commit()

                logger.info(f"Executed signal trade for user {user_id}: {signal.symbol} {signal.signal_type}")
                return True
            else:
                logger.error(f"Failed to execute signal trade for user {user_id}")
                return False

        except Exception as e:
            session.rollback()
            logger.error(f"Error executing signal trade for user {user_id}: {e}")
            return False
        finally:
            session.close()

    def get_recent_signals(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent signals from Freqtrade

        Args:
            limit: Maximum number of signals to return

        Returns:
            List of recent signals
        """
        session = get_db_session()
        try:
            signals = session.query(Signal).filter(
                Signal.created_at >= datetime.utcnow() - timedelta(hours=24)
            ).order_by(Signal.created_at.desc()).limit(limit).all()

            return [
                {
                    'id': s.id,
                    'symbol': s.symbol,
                    'signal_type': s.signal_type,
                    'entry_price': s.entry_price,
                    'stop_loss': s.stop_loss,
                    'take_profit': s.take_profit,
                    'confidence_score': s.confidence_score,
                    'created_at': s.created_at.isoformat(),
                    'is_executed': s.is_executed
                } for s in signals
            ]

        finally:
            session.close()

    def get_signal_stats(self) -> Dict[str, Any]:
        """
        Get signal statistics

        Returns:
            Signal statistics
        """
        session = get_db_session()
        try:
            total_signals = session.query(Signal).count()
            buy_signals = session.query(Signal).filter_by(signal_type='BUY').count()
            sell_signals = session.query(Signal).filter_by(signal_type='SELL').count()
            executed_signals = session.query(Signal).filter_by(is_executed=True).count()

            return {
                'total_signals': total_signals,
                'buy_signals': buy_signals,
                'sell_signals': sell_signals,
                'executed_signals': executed_signals,
                'execution_rate': (executed_signals / total_signals * 100) if total_signals > 0 else 0
            }

        finally:
            session.close()

    def force_buy(self, pair: str, price: float = None) -> Optional[Dict[str, Any]]:
        """
        Force a buy order in Freqtrade (for testing)

        Args:
            pair: Trading pair
            price: Optional price

        Returns:
            Order result or None if error
        """
        try:
            data = {'pair': pair}
            if price:
                data['price'] = price

            response = requests.post(
                f"{self.rpc_url}/api/v1/forcebuy",
                json=data,
                headers=self._get_auth_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to force buy: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error forcing buy: {e}")
            return None

    def force_sell(self, tradeid: str) -> Optional[Dict[str, Any]]:
        """
        Force a sell order in Freqtrade (for testing)

        Args:
            tradeid: Trade ID to sell

        Returns:
            Order result or None if error
        """
        try:
            response = requests.post(
                f"{self.rpc_url}/api/v1/forcesell",
                json={'tradeid': tradeid},
                headers=self._get_auth_headers(),
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to force sell: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error forcing sell: {e}")
            return None


# Global Freqtrade manager instance
freqtrade_manager = FreqtradeManager()


def get_freqtrade_manager() -> FreqtradeManager:
    """Get the global Freqtrade manager instance"""
    return freqtrade_manager
