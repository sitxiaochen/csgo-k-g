import requests
from config.settings import API_BASE_URL, API_KEY

def fetch_skin_data(skin_url: str) -> dict:
    """
    通过API获取饰品数据
    :param skin_url: 用户输入的饰品链接
    :return: 返回饰品的原始数据字典
    """
    params = {
        "apikey": API_KEY,
        "url": skin_url
    }
    response = requests.get(f"{API_BASE_URL}/item", params=params)
    response.raise_for_status()
    return response.json()

def fetch_supported_markets() -> list:
    """
    获取API支持的所有市场平台信息
    """
    params = {"apikey": API_KEY}
    response = requests.get(f"{API_BASE_URL}/markets", params=params)
    response.raise_for_status()
    return response.json().get("data", [])