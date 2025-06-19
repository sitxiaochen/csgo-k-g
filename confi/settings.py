"""
全局配置文件
请在此处填写你的聚合API密钥等敏感信息
"""
API_BASE_URL = "https://api.steamdt.com/v1/market"
API_KEY = "YOUR_API_KEY_HERE"  # <-- 请在此处填写你的API密钥

ANALYSIS_CONFIG = {
    "kline_min_points": 20,
    "kline_short": 5,
    "kline_long": 20,
    "kline_bullish": 0.03,
    "kline_bearish": 0.03,
    "sma_short": 5,
    "sma_long": 20,
    "sma_crossover": 0.03,
    "rsi_window": 14,
    "rsi_buy": 30,
    "rsi_sell": 70,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "volume_short": 5,
    "volume_long": 20,
    "volume_up": 0.2,
    "volume_down": 0.2,
    "arbitrage": 5,  # 百分比
    "min_buy": 2,
    "min_sell": 2,
    "min_sell_block": 1,
}