"""
股票爬蟲模組
使用 crawl4ai 異步爬取台灣股票資訊
"""
import asyncio
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


def get_stock_schema() -> Dict:
    """
    取得股票資訊的 CSS 提取 Schema
    
    Returns:
        股票資訊的 Schema 定義
    """
    return {
        "name": "StockInfo",
        "baseSelector": "main.main",
        "fields": [
            {
                "name": "日期時間",
                "selector": "time.last-time#lastQuoteTime",
                "type": "text"
            },
            {
                "name": "股票號碼",
                "selector": "span.astock-code[c-model='id']",
                "type": "text"
            },
            {
                "name": "股票名稱",
                "selector": "h3.astock-name[c-model='name']",
                "type": "text"
            },
            {
                "name": "即時價格",
                "selector": "div.quotes-info div.deal",
                "type": "text"
            },
            {
                "name": "漲跌",
                "selector": "div.quotes-info span.chg[c-model='change']",
                "type": "text"
            },
            {
                "name": "漲跌百分比",
                "selector": "div.quotes-info span.chg-rate[c-model='changeRate']",
                "type": "text"
            },
            {
                "name": "開盤價",
                "selector": "div.quotes-info #quotesUl span[c-model-dazzle='text:open,class:openUpDn']",
                "type": "text"
            },
            {
                "name": "最高價",
                "selector": "div.quotes-info #quotesUl span[c-model-dazzle='text:high,class:highUpDn']",
                "type": "text"
            },
            {
                "name": "成交量(張)",
                "selector": "div.quotes-info #quotesUl span[c-model='volume']",
                "type": "text"
            },
            {
                "name": "最低價",
                "selector": "div.quotes-info #quotesUl span[c-model-dazzle='text:low,class:lowUpDn']",
                "type": "text"
            },
            {
                "name": "前一日收盤價",
                "selector": "div.quotes-info #quotesUl span[c-model='previousClose']",
                "type": "text"
            }
        ]
    }


async def fetch_stock_info(
    crawler: AsyncWebCrawler,
    stock_code: str,
    config: CrawlerRunConfig,
    semaphore: asyncio.Semaphore,
    retry_previous_day: bool = True
) -> Optional[Dict]:
    """
    抓取單一股票資訊，若當日無資料則嘗試前一個交易日
    
    Args:
        crawler: AsyncWebCrawler 實例
        stock_code: 股票代碼
        config: 爬蟲執行設定
        semaphore: 用於限制並行數量的信號量
        retry_previous_day: 若當日無資料是否重試前一交易日
    
    Returns:
        股票資訊字典，失敗時返回 None
    """
    async with semaphore:  # 限制並行數量
        url = f'https://www.wantgoo.com/stock/{stock_code}/technical-chart'

        try:
            result = await crawler.arun(url=url, config=config)

            # 檢查資料是否有效
            if result.success and result.extracted_content:
                # 檢查是否有實際的即時價格資料
                data = result.extracted_content
                if isinstance(data, dict) and data.get("即時價格"):
                    print(f"✓ 股票 {stock_code} 今日資料下載成功")
                    return {
                        "stock_code": stock_code,
                        "success": True,
                        "data": data,
                        "date_type": "today"
                    }
                elif retry_previous_day:
                    # 若今日無資料，嘗試抓前一交易日
                    print(f"⚠️  股票 {stock_code} 今日無資料，嘗試前一交易日...")
                    return await _fetch_previous_trading_day(
                        crawler, stock_code, config, semaphore
                    )
                else:
                    print(f"✗ 股票 {stock_code} 無資料")
                    return {
                        "stock_code": stock_code,
                        "success": False,
                        "data": None
                    }
            elif retry_previous_day:
                # 爬蟲失敗，嘗試前一交易日
                print(f"⚠️  股票 {stock_code} 下載失敗，嘗試前一交易日...")
                return await _fetch_previous_trading_day(
                    crawler, stock_code, config, semaphore
                )
            else:
                print(f"✗ 股票 {stock_code} 下載失敗")
                return {
                    "stock_code": stock_code,
                    "success": False,
                    "data": None
                }

        except Exception as e:
            print(f"✗ 股票 {stock_code} 發生錯誤: {e}")
            return {
                "stock_code": stock_code,
                "success": False,
                "data": None,
                "error": str(e)
            }


async def _fetch_previous_trading_day(
    crawler: AsyncWebCrawler,
    stock_code: str,
    config: CrawlerRunConfig,
    semaphore: asyncio.Semaphore
) -> Optional[Dict]:
    """
    嘗試抓取前一個交易日的資料
    
    Args:
        crawler: AsyncWebCrawler 實例
        stock_code: 股票代碼
        config: 爬蟲執行設定
        semaphore: 用於限制並行數量的信號量
    
    Returns:
        股票資訊字典
    """
    async with semaphore:
        try:
            # 計算前一交易日（往前推一天，跳過週末）
            today = datetime.now()
            for i in range(1, 4):  # 最多往前推 3 天（以防多個週末）
                prev_day = today - timedelta(days=i)
                # 跳過週末（5=Saturday, 6=Sunday）
                if prev_day.weekday() < 5:
                    break
            
            url = f'https://www.wantgoo.com/stock/{stock_code}/technical-chart'
            result = await crawler.arun(url=url, config=config)
            
            if result.success and result.extracted_content:
                data = result.extracted_content
                if isinstance(data, dict):
                    print(f"✓ 股票 {stock_code} 前一交易日資料下載成功 ({prev_day.strftime('%Y-%m-%d')})")
                    return {
                        "stock_code": stock_code,
                        "success": True,
                        "data": data,
                        "date_type": "previous_trading_day",
                        "trading_date": prev_day.strftime("%Y-%m-%d")
                    }
            
            print(f"✗ 股票 {stock_code} 前一交易日資料也無法取得")
            return {
                "stock_code": stock_code,
                "success": False,
                "data": None
            }
            
        except Exception as e:
            print(f"✗ 股票 {stock_code} 前一交易日查詢失敗: {e}")
            return {
                "stock_code": stock_code,
                "success": False,
                "data": None
            }


async def fetch_multiple_stocks(
    stock_codes: List[str],
    max_concurrent: int = 5
) -> Dict[str, Dict]:
    """
    並行爬取多支股票資訊
    
    Args:
        stock_codes: 股票代碼清單
        max_concurrent: 最多同時爬取數量
    
    Returns:
        {stock_code: stock_data} 的字典
    """
    # 建立 Schema 和配置
    stock_schema = get_stock_schema()
    extraction_strategy = JsonCssExtractionStrategy(schema=stock_schema)

    browser_config = BrowserConfig(headless=True)

    crawler_run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=extraction_strategy,
        scan_full_page=True,
        verbose=False
    )

    # 限制同時爬取的數量
    semaphore = asyncio.Semaphore(max_concurrent)

    # 使用單一 crawler 實例並行爬取所有股票
    async with AsyncWebCrawler(config=browser_config) as crawler:
        tasks = [
            fetch_stock_info(crawler, code, crawler_run_config, semaphore)
            for code in stock_codes
        ]

        # 並行執行所有任務
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 處理結果
        stock_data = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"發生異常: {result}")
            elif result is not None:
                stock_code = result["stock_code"]
                stock_data[stock_code] = result

        return stock_data


def get_mock_stock_data(stock_code: str) -> Dict:
    """
    返回模擬股票資料（當爬蟲失敗時使用）
    
    Args:
        stock_code: 股票代碼
    
    Returns:
        模擬股票資料
    """
    mock_data = {
        "2330": {
            "stock_code": "2330",
            "success": True,
            "data": {
                "股票號碼": "2330",
                "股票名稱": "台積電",
                "即時價格": "993.00",
                "漲跌": "12.00",
                "漲跌百分比": "+1.22%",
                "開盤價": "989.00",
                "最高價": "996.00",
                "最低價": "988.00",
                "成交量(張)": "28,456",
                "前一日收盤價": "981.00",
                "日期時間": "2025-12-20 13:30:00"
            }
        },
        "2317": {
            "stock_code": "2317",
            "success": True,
            "data": {
                "股票號碼": "2317",
                "股票名稱": "鴻海",
                "即時價格": "234.50",
                "漲跌": "5.50",
                "漲跌百分比": "+2.40%",
                "開盤價": "230.00",
                "最高價": "235.00",
                "最低價": "229.00",
                "成交量(張)": "45,123",
                "前一日收盤價": "229.00",
                "日期時間": "2025-12-20 13:30:00"
            }
        },
        "2454": {
            "stock_code": "2454",
            "success": True,
            "data": {
                "股票號碼": "2454",
                "股票名稱": "聯發科",
                "即時價格": "1,456.00",
                "漲跌": "28.00",
                "漲跌百分比": "+1.95%",
                "開盤價": "1,440.00",
                "最高價": "1,465.00",
                "最低價": "1,430.00",
                "成交量(張)": "12,456",
                "前一日收盤價": "1,428.00",
                "日期時間": "2025-12-20 13:30:00"
            }
        }
    }

    return mock_data.get(stock_code, {
        "stock_code": stock_code,
        "success": False,
        "data": None
    })
