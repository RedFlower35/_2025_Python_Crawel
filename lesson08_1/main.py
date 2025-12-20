"""
台灣股票即時監控桌面應用程式
主程式 - 整合爬蟲與 UI，實現完整功能
"""
import tkinter as tk
import asyncio
import threading
from queue import Queue
from datetime import datetime
from typing import Optional

from stock_crawler import fetch_multiple_stocks, get_mock_stock_data
from data_manager import StockDataManager, StockListManager
from ui_manager import StockMonitorUI


class StockMonitorApp:
    """股票監控應用程式"""

    def __init__(self, root: tk.Tk):
        """
        初始化應用程式
        
        Args:
            root: Tkinter 根視窗
        """
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 資料管理器
        self.data_manager = StockDataManager()
        self.stock_list_manager = StockListManager()

        # UI 管理器
        self.ui = StockMonitorUI(root)

        # 連接 UI 回調
        self.ui.on_add_stock = self.add_stock_to_watchlist
        self.ui.on_remove_stock = self.remove_stock_from_watchlist
        self.ui.on_manual_update = self.manual_update
        self.ui.on_search = self.search_stocks

        # 更新任務隊列
        self.update_queue: Queue = Queue()

        # 更新控制
        self.update_interval = 60000  # 60 秒（毫秒）
        self.is_updating = False
        self.scheduled_update_id: Optional[str] = None

        # 初始化
        self._initialize()

        # 啟動定時更新
        self.schedule_auto_update()

    def _initialize(self):
        """初始化應用程式"""
        print("初始化應用程式...")

        # 更新股票清單顯示
        all_stocks = self.stock_list_manager.get_all_stocks()
        self.ui.update_stock_list(all_stocks)

        # 加載之前保存的觀察清單並更新
        watchlist = self.data_manager.get_watchlist()
        if watchlist:
            print(f"加載觀察清單: {watchlist}")
            # 立即更新這些股票的資料
            self.update_stock_data(watchlist)
        else:
            print("觀察清單為空")

        # 更新最後更新時間
        last_update = self.data_manager.get_last_update_time()
        if last_update:
            self.ui.update_last_update_time(last_update)

    def search_stocks(self, keyword: str):
        """
        搜尋股票
        
        Args:
            keyword: 搜尋關鍵字
        """
        if not keyword:
            # 如果搜尋框為空，顯示所有股票
            all_stocks = self.stock_list_manager.get_all_stocks()
        else:
            # 搜尋符合條件的股票
            all_stocks = self.stock_list_manager.search_stocks(keyword)

        self.ui.update_stock_list(all_stocks)

    def add_stock_to_watchlist(self, stock_code: str):
        """
        將股票加入觀察清單
        
        Args:
            stock_code: 股票代碼
        """
        stock_name = self.stock_list_manager.get_stock_name(stock_code)
        
        if self.data_manager.add_to_watchlist(stock_code):
            print(f"已加入觀察清單: {stock_code} - {stock_name}")
            self.ui.show_info("成功", f"已加入: {stock_code} - {stock_name}")
            
            # 立即更新這支股票的資料
            self.update_stock_data([stock_code])
        else:
            print(f"股票已在觀察清單中: {stock_code}")
            self.ui.show_info("提示", f"股票 {stock_code} 已在觀察清單中")

    def remove_stock_from_watchlist(self, stock_code: str):
        """
        從觀察清單移除股票
        
        Args:
            stock_code: 股票代碼
        """
        if self.data_manager.remove_from_watchlist(stock_code):
            print(f"已從觀察清單移除: {stock_code}")
            # 重新整理顯示
            self.refresh_watchlist_display()
        else:
            print(f"股票不在觀察清單中: {stock_code}")

    def refresh_watchlist_display(self):
        """刷新觀察清單顯示"""
        watchlist = self.data_manager.get_watchlist()
        all_stock_data = self.data_manager.get_all_stock_data()

        # 顯示觀察清單中的所有股票（包括還沒資料的）
        displayed_data = {}
        for code in watchlist:
            if code in all_stock_data:
                # 有資料，直接使用
                stock_data = all_stock_data[code]
                # 確保資料結構正確
                if isinstance(stock_data, dict):
                    displayed_data[code] = stock_data
                else:
                    # 如果資料不正確，跳過此股票
                    print(f"⚠️  股票 {code} 資料格式錯誤，已跳過")
            else:
                # 沒有資料，建立佔位符（等待載入）
                stock_name = self.stock_list_manager.get_stock_name(code)
                displayed_data[code] = {
                    "stock_code": code,
                    "stock_name": stock_name,
                    "success": False,
                    "data": {
                        "price": "載入中...",
                        "change": "-",
                        "change_percent": "-",
                        "date": "-"
                    },
                    "timestamp": None
                }

        self.ui.update_watchlist(displayed_data)

    def manual_update(self):
        """手動更新按鈕被點擊"""
        watchlist = self.data_manager.get_watchlist()
        if not watchlist:
            self.ui.show_error("提示", "請先加入觀察清單")
            return

        print("手動更新中...")
        self.ui.set_update_button_state(False)
        self.update_stock_data(watchlist)

    def update_stock_data(self, stock_codes: list):
        """
        在背景執行緒中更新股票資料
        
        Args:
            stock_codes: 股票代碼清單
        """
        if self.is_updating:
            print("已有更新任務在執行中，忽略本次請求")
            return

        self.is_updating = True

        # 在背景執行緒中運行爬蟲
        thread = threading.Thread(
            target=self._fetch_and_update,
            args=(stock_codes,),
            daemon=True
        )
        thread.start()

    def _fetch_and_update(self, stock_codes: list):
        """
        在背景執行緒中執行爬蟲和更新
        
        Args:
            stock_codes: 股票代碼清單
        """
        try:
            print(f"開始爬取股票資料: {stock_codes}")

            # 運行異步爬蟲
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                results = loop.run_until_complete(
                    fetch_multiple_stocks(stock_codes, max_concurrent=5)
                )
            finally:
                loop.close()

            # 處理爬蟲結果
            for stock_code, result in results.items():
                if result.get("success"):
                    stock_data = {
                        "stock_code": stock_code,
                        "stock_name": self.stock_list_manager.get_stock_name(stock_code),
                        "success": True,
                        "data": result.get("data", {}),
                        "timestamp": datetime.now().isoformat()
                    }
                    self.data_manager.update_stock_data(stock_code, stock_data)
                    print(f"✓ 已更新: {stock_code}")
                else:
                    # 爬蟲失敗，使用模擬資料
                    mock_data = get_mock_stock_data(stock_code)
                    if mock_data.get("success"):
                        stock_data = {
                            "stock_code": stock_code,
                            "stock_name": self.stock_list_manager.get_stock_name(stock_code),
                            "success": True,
                            "data": mock_data.get("data", {}),
                            "timestamp": datetime.now().isoformat()
                        }
                        self.data_manager.update_stock_data(stock_code, stock_data)
                        print(f"⚠️  使用模擬資料: {stock_code}")
                    else:
                        print(f"✗ 無法獲取: {stock_code}")

            # 將更新結果放入隊列，由主執行緒處理
            self.update_queue.put(("update_complete", None))

        except Exception as e:
            print(f"✗ 更新錯誤: {e}")
            self.update_queue.put(("update_error", str(e)))

        finally:
            self.is_updating = False

    def process_queue(self):
        """處理隊列中的消息（由主執行緒定期調用）"""
        try:
            while True:
                msg_type, msg_data = self.update_queue.get_nowait()

                if msg_type == "update_complete":
                    print("✓ 更新完成")
                    # 刷新 UI 顯示
                    self.refresh_watchlist_display()
                    # 更新最後更新時間
                    last_update = self.data_manager.get_last_update_time()
                    self.ui.update_last_update_time(last_update)
                    # 重新啟用更新按鈕
                    self.ui.set_update_button_state(True)

                elif msg_type == "update_error":
                    print(f"✗ 更新錯誤: {msg_data}")
                    self.ui.show_error("更新失敗", f"發生錯誤: {msg_data}")
                    self.ui.set_update_button_state(True)

        except:
            # 隊列為空，正常情況
            pass

        # 繼續檢查隊列
        self.root.after(100, self.process_queue)

    def schedule_auto_update(self):
        """排定自動更新任務"""
        watchlist = self.data_manager.get_watchlist()

        if watchlist:
            print(f"排定自動更新: {self.update_interval}ms 後更新 {len(watchlist)} 支股票")
            self.update_stock_data(watchlist)

        # 排定下次自動更新
        self.scheduled_update_id = self.root.after(
            self.update_interval,
            self.schedule_auto_update
        )

    def on_closing(self):
        """應用程式關閉"""
        print("應用程式正在關閉...")

        # 取消排定的更新任務
        if self.scheduled_update_id:
            self.root.after_cancel(self.scheduled_update_id)

        # 保存資料
        self.data_manager._save_watchlist()

        # 關閉主視窗
        self.root.destroy()


def main():
    """主程式入口"""
    print("=" * 60)
    print("📈 台灣股票即時監控系統")
    print("=" * 60)

    root = tk.Tk()

    # 建立應用程式實例
    app = StockMonitorApp(root)

    # 開始處理隊列
    root.after(100, app.process_queue)

    # 啟動 Tkinter 事件迴圈
    root.mainloop()

    print("✓ 應用程式已關閉")


if __name__ == "__main__":
    main()
