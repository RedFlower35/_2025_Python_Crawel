from pathlib import Path
import asyncio
from playwright.sync_api import sync_playwright
from datetime import datetime, timedelta

def get_html_path() -> str:
    """回傳檔案的絕對路徑（ waiting_demo.html 與此檔同目錄）"""
    html_path = Path(__file__).parent / "waiting_demo.html"
    return f"{html_path.resolve()}"

def get_news(page):
    lis = page.locator("ul#alltype-news > li")  # 取得所有 li 元素
    print(f"最新消息共有 {lis.count()} 筆")
    for i in range(lis.count()):
        title = lis.nth(i).locator(".news-title").text_content()
        date = lis.nth(i).locator(".news-date").text_content()
        print(f"{date} - {title}")

def schedule_and_fare(page):
    page.locator("#select_location01").select_option("台北")
    page.locator("#select_location02").select_option("台南")

    #計算當前時間加1小時
    now = datetime.now() + timedelta(hours=1)
    depart_date = now.strftime("%Y/%m/%d")
    depart_time = now.strftime("%H:%M")

    # 填入出發日期與時間
    page.fill("#Departdate03", depart_date)
    page.fill("#outWardTime", depart_time)
    page.click("#start-search")  # 點擊 查詢按鈕


def main():
    html_path = "https://www.thsrc.com.tw/"
    print(html_path)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False,slow_mo=500) # 啟動瀏覽器
        page = browser.new_page() # 建立新分頁
        page.goto(html_path)

        page.wait_for_load_state("domcontentloaded") # 等待頁面載入完成
        page.locator("button",has_text="不同意").click()  # 取得 Locator 按鈕，並點擊 不同意

        get_news(page) # 取得最新消息
        schedule_and_fare(page) # 查詢時刻與票價



        page.wait_for_timeout(3000) # 停留 3 秒

        browser.close()
    
if __name__ == "__main__":
    main()