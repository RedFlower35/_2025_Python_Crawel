from pathlib import Path
# import asyncio
from playwright.sync_api import sync_playwright

def get_html_path() -> str:
    """回傳檔案的絕對路徑（ waiting_demo.html 與此檔同目錄）"""
    html_path = Path(__file__).parent / "waiting_demo.html"
    return f"{html_path.resolve()}"

def demo_1_delayed_element(page):
    button_delay = page.locator("#trigger-delayed")  # 取得 Locator 按鈕
    button_delay.click() # 點擊按鈕

    # 等待載入指示器出現
    # page.wait_for_selector("#loading-1", state="visible")
    # print("載入指示器已出現")
    # # 等待載入指示器消失
    # page.wait_for_selector("#loading-1", state="hidden")
    # print("載入指示器已消失")
    # page.wait_for_selector("div#delayed-result.result.show", state="visible")

    # 取得內容
    content = page.locator("#delayed-content").text_content()
    print(f"延遲加載的內容: {content}")

# 示範 2：動態內容加載  AJAX
def demo_2_dynamic_content(page):
    page.click("#load-data")  # 點擊按鈕_動態內容載入 AJAX

    page.wait_for_function("document.querySelectorAll('#dynamic-content > .item').length >= 1")
    items = page.locator("#dynamic-content > .item").all()
    for item in items:
        print(f"動態加載的項目: {item.text_content()}")

def main():
    html_path = "file:///" +get_html_path()
    print(html_path)

    with sync_playwright() as p:
        browser =  p.chromium.launch(headless=False,slow_mo=500) # 啟動瀏覽器
        page =  browser.new_page() # 建立新分頁
        page.goto(html_path)

        page.wait_for_load_state("networkidle") # 等待頁面載入完成

        demo_1_delayed_element(page) # 示範 1：延遲元素加載

        demo_2_dynamic_content(page) # 示範 2：動態內容加載


        page.wait_for_timeout(3000) # 停留 3 秒

        browser.close()
    
if __name__ == "__main__":
    main()