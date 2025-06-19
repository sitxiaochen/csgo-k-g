import pandas as pd

def extract_key_data(raw_data: dict) -> pd.DataFrame:
    """
    从原始数据中提取关键字段，返回DataFrame
    :param raw_data: API返回的原始数据
    :return: 关键数据DataFrame
    """
    # 假设API返回的数据结构中有历史价格、交易量等
    # 这里需要根据实际API返回结构调整
    history = raw_data.get("price_history", [])
    if not history:
        return pd.DataFrame()
    df = pd.DataFrame(history)
    # 统一字段名
    df.rename(columns={
        "price": "combined_price",
        "volume": "combined_volume",
        "buff_price": "buff_price",
        "steam_price": "steam_price",
        "timestamp": "timestamp"
    }, inplace=True)
    # 计算价差百分比
    if "buff_price" in df and "steam_price" in df:
        df["price_diff_ratio"] = (df["steam_price"] - df["buff_price"]) / df["buff_price"] * 100
    return df