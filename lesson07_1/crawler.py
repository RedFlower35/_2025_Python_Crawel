"""
匯率爬蟲模組
使用 crawl4ai 爬取台幣匯率資料
"""
import asyncio
import re
from typing import Dict, List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode


async def fetch_exchange_rates() -> Dict[str, Dict[str, str]]:
    """
    爬取匯率資料
    
    Returns:
        Dict[str, Dict[str, str]]: 匯率資料字典
        格式: {
            'USD': {'rate': '31.50', 'status': '交易中'},
            'JPY': {'rate': '0.21', 'status': '交易中'},
            ...
        }
    """
    try:
        # 配置瀏覽器選項
        browser_config = BrowserConfig(
            headless=True  # 無頭模式執行
        )

        # 配置爬蟲選項
        run_config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS  # 不使用快取，每次都重新爬取
        )

        # 建立爬蟲實體並執行爬取
        async with AsyncWebCrawler(config=browser_config) as crawler:
            # 爬取台灣銀行匯率資料
            result = await crawler.arun(
                url='https://rate.bot.com.tw/xrt?Lang=zh-TW',
                config=run_config
            )

        if not result.success:
            print(f"爬取失敗: {result.error_message}")
            return {}

        # 解析 HTML 資料
        rates_data = _parse_exchange_rates(result.html)
        return rates_data

    except Exception as e:
        print(f"爬蟲執行錯誤: {e}")
        return {}


def _parse_exchange_rates(html: str) -> Dict[str, Dict[str, str]]:
    """
    解析匯率 HTML 資料
    
    Args:
        html (str): 爬取的 HTML 內容
        
    Returns:
        Dict[str, Dict[str, str]]: 匯率資料
    """
    rates = {}

    try:
        # 正則表達式匹配匯率資料
        # 查找所有行包含貨幣代碼和匯率
        pattern = r'<td[^>]*>(\w{3})</td>.*?<td[^>]*>([\d.]+)</td>.*?<td[^>]*>(\w+)</td>'

        matches = re.finditer(pattern, html, re.DOTALL)

        for match in matches:
            currency = match.group(1)
            rate = match.group(2)
            status = match.group(3)

            # 只保存有效的匯率資料
            if currency and rate and status:
                rates[currency] = {
                    'rate': rate,
                    'status': status
                }

        # 如果沒有找到資料，嘗試替代解析方法
        if not rates:
            rates = _parse_exchange_rates_fallback(html)

    except Exception as e:
        print(f"解析匯率資料錯誤: {e}")

    return rates


def _parse_exchange_rates_fallback(html: str) -> Dict[str, Dict[str, str]]:
    """
    備用匯率解析方法
    當主要解析失敗時使用
    
    Args:
        html (str): 爬取的 HTML 內容
        
    Returns:
        Dict[str, Dict[str, str]]: 匯率資料
    """
    rates = {}

    try:
        # 更靈活的正則表達式
        # 匹配貨幣代碼 (3個大寫字母) 和後續數字
        pattern = r'>(\w{3})<.*?>([\d.]+)<'

        matches = re.finditer(pattern, html)
        currencies = []

        for match in matches:
            currency = match.group(1)
            rate = match.group(2)

            # 驗證貨幣代碼是否有效（3個大寫字母）
            if len(currency) == 3 and currency.isupper():
                if currency not in [c[0] for c in currencies]:
                    currencies.append((currency, rate))

        # 將前15個貨幣作為匯率資料
        for currency, rate in currencies[:15]:
            rates[currency] = {
                'rate': rate,
                'status': '交易中'
            }

    except Exception as e:
        print(f"備用解析失敗: {e}")

    return rates


async def get_exchange_rates_async() -> Dict[str, Dict[str, str]]:
    """
    非同步獲取匯率資料的包裝函數
    
    Returns:
        Dict[str, Dict[str, str]]: 匯率資料
    """
    return await fetch_exchange_rates()


def get_exchange_rates() -> Dict[str, Dict[str, str]]:
    """
    同步獲取匯率資料的包裝函數
    在 Streamlit 中使用
    
    Returns:
        Dict[str, Dict[str, str]]: 匯率資料
    """
    try:
        # 在 Windows 上需要設置事件迴圈策略
        if asyncio.get_event_loop().is_closed():
            asyncio.set_event_loop(asyncio.new_event_loop())

        loop = asyncio.get_event_loop()
        return loop.run_until_complete(fetch_exchange_rates())
    except RuntimeError:
        # 如果無法獲取事件迴圈，建立新的
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(fetch_exchange_rates())


# 測試用匯率資料（當爬蟲失敗時使用）
MOCK_RATES = {
    'USD': {'rate': '31.50', 'status': '交易中'},
    'JPY': {'rate': '0.21', 'status': '交易中'},
    'EUR': {'rate': '34.50', 'status': '交易中'},
    'GBP': {'rate': '39.80', 'status': '交易中'},
    'AUD': {'rate': '21.00', 'status': '交易中'},
    'CAD': {'rate': '23.50', 'status': '交易中'},
    'SGD': {'rate': '23.80', 'status': '交易中'},
    'HKD': {'rate': '4.00', 'status': '交易中'},
    'CNY': {'rate': '4.30', 'status': '交易中'},
    'KRW': {'rate': '0.024', 'status': '交易中'},
}


def get_mock_rates() -> Dict[str, Dict[str, str]]:
    """
    返回測試用匯率資料
    當爬蟲無法正常運作時使用
    
    Returns:
        Dict[str, Dict[str, str]]: 測試匯率資料
    """
    return MOCK_RATES.copy()
