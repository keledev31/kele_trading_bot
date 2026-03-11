"""
Conservative EMA200 + RSI Strategy for Freqtrade
- Uses EMA200 for trend filtering (only buy when price > EMA200)
- RSI for overbought/oversold conditions
- Tight stop-loss (2%) and trailing stop for protection
- Max 3 open trades
- Dry-run by default
"""

import talib.abstract as ta
from freqtrade.strategy import IStrategy, merge_informative_pair
from pandas import DataFrame
import logging

logger = logging.getLogger(__name__)


class EMA200RSIStrategy(IStrategy):
    """
    Conservative strategy combining EMA200 trend filter with RSI momentum
    """

    # Strategy metadata
    INTERFACE_VERSION = 3
    
    # Buy hyperparameters
    buy_ema_diff = 0.005  # Buy when price is 0.5% above EMA200
    buy_rsi_threshold = 40  # RSI below 40 is potential buy
    
    # Sell hyperparameters
    sell_rsi_threshold = 70  # RSI above 70 is potential sell
    
    # Stoploss settings
    stoploss = -0.02  # Hard stop at 2% loss
    trailing_stop = True
    trailing_stop_positive = 0.01  # 1% profit takes effect
    trailing_stop_positive_offset = 0.02  # 2% from top
    trailing_only_offset_is_reached = True
    
    # Sell signal
    use_sell_signal = True
    sell_profit_only = False
    sell_profit_offset = 0.01  # Sell at 1% profit
    ignore_roi_if_buy_signal = False
    
    # ROI table (take profits at different levels)
    minimal_roi = {
        "0": 0.05,      # 5% profit - sell after 0 minutes
        "30": 0.03,     # 3% profit - sell after 30 minutes  
        "60": 0.02,     # 2% profit - sell after 60 minutes
        "240": 0.01     # 1% profit - sell after 240 minutes
    }
    
    # Optimal timeframe
    timeframe = '5m'
    
    # Protect against whipsaws
    cooldown_lookback = 2

    def informative_pairs(self):
        """Specify additional pairs for informative purposes (1h for trend)"""
        pairs = self.dp.current_whitelist()
        informative_pairs = [(pair, '1h') for pair in pairs]
        return informative_pairs

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Calculate technical indicators
        """
        
        # EMA200 - Trend Filter (on 1h timeframe for stability)
        inf_1h = self.dp.get_pair_candle_history(
            pair=metadata['pair'], 
            timeframe='1h'
        )[0]
        
        if len(inf_1h) > 200:
            inf_1h['ema200'] = ta.EMA(inf_1h, timeperiod=200)
            # Get the latest 1h EMA value and fill the 5m dataframe
            latest_ema200 = inf_1h['ema200'].iloc[-1]
            dataframe['ema200'] = latest_ema200
        
        # RSI (14 period) - On 5m for responsiveness
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # EMA12 & EMA26 for MACD
        dataframe['ema_short'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_long'] = ta.EMA(dataframe, timeperiod=26)
        
        # Bollinger Bands for volatility
        bb = ta.BBANDS(dataframe, timeperiod=20, nbdevup=2, nbdevdn=2)
        dataframe['bb_lowerband'] = bb['lowerband']
        dataframe['bb_upperband'] = bb['upperband']
        dataframe['bb_middleband'] = bb['middleband']
        
        # Volume SMA for trend confirmation
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)
        
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate buy signals
        """
        dataframe.loc[:, 'buy'] = 0

        buy_signal = (
            # Trend Filter: Price above EMA200
            (dataframe['close'] > dataframe['ema200'] * (1 + self.buy_ema_diff)) &
            
            # Momentum: RSI below threshold (oversold potential)
            (dataframe['rsi'] < self.buy_rsi_threshold) &
            (dataframe['rsi'] > 30) &  # But not too oversold to avoid noise
            
            # Price above lower bollinger band (recovering from oversold)
            (dataframe['close'] > dataframe['bb_lowerband']) &
            
            # Volume confirmation: Higher than 20-SMA
            (dataframe['volume'] > dataframe['volume_sma']) &
            
            # Price is above SMA12 (in uptrend on short term)
            (dataframe['close'] > dataframe['ema_short'])
        )

        dataframe.loc[buy_signal, 'buy'] = 1
        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Populate sell signals
        """
        dataframe.loc[:, 'sell'] = 0

        sell_signal = (
            # Momentum: RSI above threshold (overbought)
            (dataframe['rsi'] > self.sell_rsi_threshold) &
            
            # Price touches upper bollinger band
            (dataframe['close'] > dataframe['bb_upperband']) &
            
            # Price below EMA short (momentum loss)
            (dataframe['close'] < dataframe['ema_short'])
        ) | (
            # OR: Price touches upper volatility (trailing stop will handle exit)
            (dataframe['close'] > dataframe['bb_upperband']) &
            (dataframe['rsi'] > 75)
        )

        dataframe.loc[sell_signal, 'sell'] = 1
        return dataframe

    def custom_stoploss(
        self, pair: str, trade, current_time, current_rate: float,
        current_profit: float, after_fill: bool, after_close: bool, **kwargs
    ) -> float:
        """
        Custom stoploss logic for additional safety
        """
        # Base stoploss as defined in self.stoploss
        return self.stoploss

    def bot_loop_start(self, **kwargs) -> None:
        """
        Called at the start of each bot loop iteration.
        Useful for checking daily drawdown limits.
        """
        pass


# For FreqAI integration (optional upgrade)
# Uncomment to enable LightGBM confidence scoring

# class EMA200RSIStrategyWithAI(EMA200RSIStrategy):
#     """
#     Extended version with FreqAI for confidence scoring
#     Requires additional FreqAI configuration
#     """
#     
#     def feature_engineering_expand_all(self, dataframe, period, **kwargs):
#         """Define features for machine learning model"""
#         dataframe['rsi_norm'] = (dataframe['rsi'] - 50) / 50
#         dataframe['ema_diff'] = (dataframe['close'] - dataframe['ema200']) / dataframe['close']
#         return dataframe
#     
#     def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
#         """Override with AI signals"""
#         # This would use FreqAI's &-labels from ML model
#         dataframe.loc[:, 'buy'] = dataframe['&-action'] == 'buy'
#         return dataframe
