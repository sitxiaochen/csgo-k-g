import pandas as pd
import numpy as np
from confi.settings import ANALYSIS_CONFIG

class Analyzer:
    """
    适配CSGO饰品市场的金融分析器。
    采用K线趋势、SMA/EMA、RSI、MACD、交易量、套利等多指标，结合保守策略给出建议。
    """

    @staticmethod
    def _sma(data: pd.Series, window: int) -> pd.Series:
        return data.rolling(window=window, min_periods=1).mean()

    @staticmethod
    def _ema(data: pd.Series, window: int) -> pd.Series:
        return data.ewm(span=window, adjust=False, min_periods=1).mean()

    @staticmethod
    def _rsi(data: pd.Series, window: int) -> pd.Series:
        delta = data.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.ewm(com=window - 1, adjust=False, min_periods=1).mean()
        avg_loss = loss.ewm(com=window - 1, adjust=False, min_periods=1).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def _macd(data: pd.Series, fast: int, slow: int, signal: int):
        exp1 = data.ewm(span=fast, adjust=False, min_periods=1).mean()
        exp2 = data.ewm(span=slow, adjust=False, min_periods=1).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=signal, adjust=False, min_periods=1).mean()
        hist = macd_line - signal_line
        return macd_line, signal_line, hist

    @staticmethod
    def _kline(df: pd.DataFrame) -> tuple[bool, str]:
        if 'combined_price' not in df or len(df) < ANALYSIS_CONFIG['kline_min_points']:
            return False, "K线分析：数据不足。"
        prices = df['combined_price'].dropna()
        if prices.empty:
            return False, "K线分析：无有效价格数据。"
        recent = prices.tail(ANALYSIS_CONFIG['kline_short']).mean()
        long = prices.tail(ANALYSIS_CONFIG['kline_long']).mean()
        if recent > long * (1 + ANALYSIS_CONFIG['kline_bullish']):
            return True, f"K线：近期均价({recent:.2f})高于长期({long:.2f})，有上涨迹象。"
        elif recent < long * (1 - ANALYSIS_CONFIG['kline_bearish']):
            return False, f"K线：近期均价({recent:.2f})低于长期({long:.2f})，有下跌风险。"
        else:
            return False, "K线：价格波动小，市场横盘。"

    @staticmethod
    def _indicators(df: pd.DataFrame) -> tuple[bool, str]:
        signals = []
        prices = df['combined_price'].dropna()
        if len(prices) < ANALYSIS_CONFIG['sma_long']:
            return False, "指标分析：数据不足。"
        df['SMA_Short'] = Analyzer._sma(prices, ANALYSIS_CONFIG['sma_short'])
        df['SMA_Long'] = Analyzer._sma(prices, ANALYSIS_CONFIG['sma_long'])
        if df['SMA_Short'].iloc[-1] > df['SMA_Long'].iloc[-1]:
            signals.append("SMA: 短期均线高于长期，偏多。")
        else:
            signals.append("SMA: 短期均线低于长期，偏空。")
        df['RSI'] = Analyzer._rsi(prices, ANALYSIS_CONFIG['rsi_window'])
        rsi = df['RSI'].iloc[-1]
        if rsi < ANALYSIS_CONFIG['rsi_buy']:
            signals.append(f"RSI({rsi:.1f}): 超卖，或有反弹。")
        elif rsi > ANALYSIS_CONFIG['rsi_sell']:
            signals.append(f"RSI({rsi:.1f}): 超买，警惕回调。")
        else:
            signals.append(f"RSI({rsi:.1f}): 正常。")
        macd, sig, hist = Analyzer._macd(prices, ANALYSIS_CONFIG['macd_fast'], ANALYSIS_CONFIG['macd_slow'], ANALYSIS_CONFIG['macd_signal'])
        if macd.iloc[-1] > sig.iloc[-1] and hist.iloc[-1] > 0:
            signals.append("MACD: 金叉，动能偏强。")
        elif macd.iloc[-1] < sig.iloc[-1] and hist.iloc[-1] < 0:
            signals.append("MACD: 死叉，动能偏弱。")
        else:
            signals.append("MACD: 信号不明显。")
        if 'combined_volume' in df:
            vols = df['combined_volume'].dropna()
            if len(vols) >= ANALYSIS_CONFIG['volume_long']:
                recent_vol = vols.tail(ANALYSIS_CONFIG['volume_short']).mean()
                long_vol = vols.tail(ANALYSIS_CONFIG['volume_long']).mean()
                if recent_vol > long_vol * (1 + ANALYSIS_CONFIG['volume_up']):
                    signals.append("交易量：近期放大，关注趋势。")
                elif recent_vol < long_vol * (1 - ANALYSIS_CONFIG['volume_down']):
                    signals.append("交易量：近期萎缩，活跃度下降。")
                else:
                    signals.append("交易量：稳定。")
        if 'price_diff_ratio' in df and not df['price_diff_ratio'].isnull().all():
            diff = df['price_diff_ratio'].iloc[-1]
            if diff > ANALYSIS_CONFIG['arbitrage']:
                signals.append("套利：Steam高于Buff，存在套利空间。")
            elif diff < -ANALYSIS_CONFIG['arbitrage']:
                signals.append("套利：Buff高于Steam，存在反向套利。")
            else:
                signals.append("套利：价差不明显。")
        buy = sum("高于" in s or "金叉" in s or "超卖" in s or "套利" in s for s in signals)
        sell = sum("低于" in s or "死叉" in s or "超买" in s for s in signals)
        if buy >= ANALYSIS_CONFIG['min_buy'] and sell < ANALYSIS_CONFIG['min_sell_block']:
            return True, "\n".join(signals) + "\n建议：可考虑购入。"
        elif sell >= ANALYSIS_CONFIG['min_sell']:
            return False, "\n".join(signals) + "\n建议：观望或卖出。"
        else:
            return False, "\n".join(signals) + "\n建议：信号不明，建议观望。"

    @staticmethod
    def analyze_skin(df: pd.DataFrame) -> tuple[bool, str]:
        if df.empty or 'combined_price' not in df or df['combined_price'].isnull().all():
            return False, "无有效数据，无法分析。"
        if 'timestamp' in df:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp').set_index('timestamp')
        else:
            return False, "缺少时间戳，无法分析。"
        k_buy, k_reason = Analyzer._kline(df)
        i_buy, i_reason = Analyzer._indicators(df)
        if k_buy and i_buy:
            return True, f"{k_reason}\n{i_reason}\n最终建议：K线与指标均偏多，建议购入。"
        elif i_buy:
            return True, f"{k_reason}\n{i_reason}\n最终建议：指标偏多，K线平稳，可谨慎购入。"
        elif k_buy:
            return False, f"{k_reason}\n{i_reason}\n最终建议：K线偏多但指标不明，建议观望。"
        else:
            return False, f"{k_reason}\n{i_reason}\n最终建议：信号不明或偏空，建议观望。"