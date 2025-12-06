import asyncio
from crawl4ai import AsyncWebCrawler,BrowserConfig,CrawlerRunConfig, CacheMode

async def main():
    """
    非同步主要函數，用於配置和初始化 AsyncWebCrawler。
    此函數設定瀏覽器配置選項，包括無頭模式和隱私模式，
    然後在非同步上下文管理器中建立 AsyncWebCrawler 的實例。
    """

    #配置瀏覽器選項
    browser_config = BrowserConfig(
        headless=False  # 啟用非無頭模式，瀏覽器面將可見
        # ,incognito=True  # 啟用隱私模式
    )

    # 配置 CrawlerRunconfig 選項
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS # 不使用快取模式
    )

    #建立一個AsyncWebCrawler的實體
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url='http://www.example.com/',
            config=run_config)
    print(result.markdown)
        # print(type(result))
        # #列印取出的結果
        # # print(result.markdown)
        # # print(result.cleaned_html)
        # # print(result.raw_html)
        # if result.success:
        #     with open('output.md', 'w', encoding='utf-8') as f:
        #         f.write(result.markdown)
        #     print("存檔成功 !")
        # else:
        #     print("失敗 !")

if __name__ == "__main__":
    #py檔執行
    asyncio.run(main())