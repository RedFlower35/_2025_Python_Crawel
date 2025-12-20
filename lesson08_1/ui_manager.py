"""
UI 管理模組
使用 Tkinter 構建用戶介面
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Optional


class StockMonitorUI:
    """股票監控應用的 UI 管理器"""

    def __init__(self, root: tk.Tk):
        """
        初始化 UI
        
        Args:
            root: Tkinter 根視窗
        """
        self.root = root
        self.root.title("📈 台灣股票即時監控系統")
        self.root.geometry("1400x800")
        
        # 字體設定（16號字體）
        self.font_title = ("微軟正黑體", 16, "bold")
        self.font_normal = ("微軟正黑體", 16)
        self.font_small = ("微軟正黑體", 14)
        
        # 回調函數
        self.on_add_stock: Optional[Callable] = None
        self.on_remove_stock: Optional[Callable] = None
        self.on_manual_update: Optional[Callable] = None
        self.on_search: Optional[Callable] = None

        # 建立 UI
        self._create_widgets()

    def _create_widgets(self):
        """建立 UI 元件"""
        # 頂部工具欄
        self._create_toolbar()

        # 主要內容區域
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左側面板（股票選擇區）
        self._create_left_panel(main_frame)

        # 右側面板（資料顯示區）
        self._create_right_panel(main_frame)

    def _create_toolbar(self):
        """建立頂部工具欄"""
        toolbar = ttk.Frame(self.root, relief=tk.RAISED, borderwidth=1)
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        # 標題
        title_label = tk.Label(
            toolbar,
            text="📈 台灣股票即時監控系統",
            font=self.font_title,
            fg="#1f77b4"
        )
        title_label.pack(side=tk.LEFT, padx=10, pady=10)

        # 更新時間顯示
        self.update_time_label = tk.Label(
            toolbar,
            text="最後更新: --:--:--",
            font=self.font_small,
            fg="#666666"
        )
        self.update_time_label.pack(side=tk.RIGHT, padx=10, pady=10)

        # 手動更新按鈕
        self.update_button = ttk.Button(
            toolbar,
            text="🔄 手動更新",
            command=self._on_manual_update_clicked
        )
        self.update_button.pack(side=tk.RIGHT, padx=5)

    def _create_left_panel(self, parent):
        """建立左側面板（股票選擇區）"""
        # 左側框架
        left_frame = ttk.LabelFrame(
            parent,
            text="📋 股票選擇",
            padding=10
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))
        left_frame.configure(width=400)

        # 搜尋框
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        search_label = tk.Label(
            search_frame,
            text="搜尋股票:",
            font=self.font_normal
        )
        search_label.pack(side=tk.LEFT, padx=(0, 5))

        self.search_entry = ttk.Entry(search_frame, font=self.font_normal)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.bind("<KeyRelease>", lambda e: self._on_search())

        # 股票清單（Listbox）
        list_label = tk.Label(
            left_frame,
            text="可選擇股票:",
            font=self.font_normal
        )
        list_label.pack(anchor=tk.W, pady=(10, 5))

        # 使用 Treeview 替代 Listbox，以支援更好的樣式
        tree_frame = ttk.Frame(left_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.stock_listbox = tk.Listbox(
            tree_frame,
            font=self.font_normal,
            yscrollcommand=scrollbar.set,
            height=25
        )
        self.stock_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.stock_listbox.bind("<Double-Button-1>", lambda e: self._on_stock_selected())
        scrollbar.config(command=self.stock_listbox.yview)

        # 加入按鈕
        self.add_button = ttk.Button(
            left_frame,
            text="➕ 加入觀察清單",
            command=self._on_add_stock_clicked
        )
        self.add_button.pack(fill=tk.X)

        # 說明文字
        help_text = tk.Label(
            left_frame,
            text="雙擊項目或按加入按鈕\n",
            font=("微軟正黑體", 12),
            fg="#999999"
        )
        help_text.pack(anchor=tk.W, pady=(5, 0))

    def _create_right_panel(self, parent):
        """建立右側面板（資料顯示區）"""
        # 右側框架
        self.right_frame = ttk.LabelFrame(
            parent,
            text="📊 觀察清單",
            padding=10
        )
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 觀察清單標籤
        watchlist_label = tk.Label(
            self.right_frame,
            text="即時資訊:",
            font=self.font_normal
        )
        watchlist_label.pack(anchor=tk.W, pady=(0, 10))

        # 股票資訊容器（使用 Canvas 和 Scrollbar）
        canvas_frame = ttk.Frame(self.right_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(canvas_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(
            canvas_frame,
            yscrollcommand=scrollbar.set
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)

        # Canvas 內的框架（用於放置股票卡片）
        self.stocks_container = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            0, 0,
            window=self.stocks_container,
            anchor="nw"
        )

        # 綁定滾動事件
        self.stocks_container.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.bind_all(
            "<MouseWheel>",
            self._on_mousewheel
        )

        # 空白提示
        self.empty_label = tk.Label(
            self.stocks_container,
            text="⬅️  從左邊選擇股票加入觀察清單",
            font=self.font_normal,
            fg="#999999",
            pady=50
        )
        self.empty_label.pack()

    def _create_stock_card(self, stock_code: str, stock_data: Dict) -> tk.Frame:
        """
        建立股票資訊卡片
        
        Args:
            stock_code: 股票代碼
            stock_data: 股票資訊字典
        
        Returns:
            股票卡片框架
        """
        card = tk.Frame(
            self.stocks_container,
            bg="#f0f0f0",
            relief=tk.RAISED,
            borderwidth=1
        )
        card.pack(fill=tk.X, pady=5, padx=5)

        # 頭部：代碼、名稱和移除按鈕
        header = tk.Frame(card, bg="#f0f0f0")
        header.pack(fill=tk.X, padx=10, pady=10)

        code_label = tk.Label(
            header,
            text=f"{stock_code}",
            font=("微軟正黑體", 16, "bold"),
            bg="#f0f0f0",
            fg="#1f77b4"
        )
        code_label.pack(side=tk.LEFT, padx=(0, 10))

        name_label = tk.Label(
            header,
            text=stock_data.get("stock_name", "N/A"),
            font=self.font_normal,
            bg="#f0f0f0"
        )
        name_label.pack(side=tk.LEFT)

        # 移除按鈕
        remove_button = ttk.Button(
            header,
            text="❌ 移除",
            command=lambda: self._on_remove_stock_clicked(stock_code)
        )
        remove_button.pack(side=tk.RIGHT)

        # 價格資訊
        price_info = stock_data.get("data") if stock_data.get("success") else None
        if price_info is None:
            price_info = {}

        # 檢查資料日期類型
        date_type = stock_data.get("date_type", "today")
        date_type_text = ""
        if date_type == "previous_trading_day":
            trading_date = stock_data.get("trading_date", "N/A")
            date_type_text = f" (前一交易日 {trading_date})"

        # 決定漲跌顏色
        change_text = price_info.get("漲跌", "N/A") if isinstance(price_info, dict) else "N/A"
        change_rate = price_info.get("漲跌百分比", "N/A") if isinstance(price_info, dict) else "N/A"
        
        # 根據漲跌決定顏色
        if "+" in str(change_text):
            price_color = "#ff0000"  # 紅色（上漲）
        elif "-" in str(change_text):
            price_color = "#00aa00"  # 綠色（下跌）
        else:
            price_color = "#000000"  # 黑色

        price_label = tk.Label(
            card,
            text=f"即時價格: {price_info.get('即時價格', 'N/A') if isinstance(price_info, dict) else 'N/A'} TWD{date_type_text}",
            font=("微軟正黑體", 16, "bold"),
            bg="#f0f0f0",
            fg=price_color
        )
        price_label.pack(anchor=tk.W, padx=20, pady=5)

        change_label = tk.Label(
            card,
            text=f"漲跌: {change_text}  ({change_rate})",
            font=self.font_normal,
            bg="#f0f0f0",
            fg=price_color
        )
        change_label.pack(anchor=tk.W, padx=20)

        # 詳細資訊網格
        info_frame = tk.Frame(card, bg="#f0f0f0")
        info_frame.pack(fill=tk.X, padx=20, pady=10)

        # 左欄
        left_info = tk.Frame(info_frame, bg="#f0f0f0")
        left_info.pack(side=tk.LEFT, fill=tk.X, expand=True)

        info_items = [
            ("開盤價", price_info.get("開盤價", "N/A") if isinstance(price_info, dict) else "N/A"),
            ("最高價", price_info.get("最高價", "N/A") if isinstance(price_info, dict) else "N/A"),
            ("最低價", price_info.get("最低價", "N/A") if isinstance(price_info, dict) else "N/A"),
        ]

        for label_text, value in info_items:
            row = tk.Frame(left_info, bg="#f0f0f0")
            row.pack(fill=tk.X, pady=2)
            
            label = tk.Label(
                row,
                text=f"{label_text}:",
                font=self.font_small,
                bg="#f0f0f0",
                fg="#666666",
                width=10,
                anchor=tk.W
            )
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(
                row,
                text=str(value),
                font=self.font_normal,
                bg="#f0f0f0"
            )
            value_label.pack(side=tk.LEFT, padx=10)

        # 右欄
        right_info = tk.Frame(info_frame, bg="#f0f0f0")
        right_info.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        right_items = [
            ("成交量", price_info.get("成交量(張)", "N/A") if isinstance(price_info, dict) else "N/A"),
            ("前一日收盤", price_info.get("前一日收盤價", "N/A") if isinstance(price_info, dict) else "N/A"),
            ("更新時間", price_info.get("日期時間", "N/A") if isinstance(price_info, dict) else "N/A"),
        ]

        for label_text, value in right_items:
            row = tk.Frame(right_info, bg="#f0f0f0")
            row.pack(fill=tk.X, pady=2)
            
            label = tk.Label(
                row,
                text=f"{label_text}:",
                font=self.font_small,
                bg="#f0f0f0",
                fg="#666666",
                width=10,
                anchor=tk.W
            )
            label.pack(side=tk.LEFT)
            
            value_label = tk.Label(
                row,
                text=str(value),
                font=self.font_normal,
                bg="#f0f0f0"
            )
            value_label.pack(side=tk.LEFT, padx=10)

        return card

    def update_stock_list(self, stocks: Dict[str, str]):
        """
        更新左側股票清單
        
        Args:
            stocks: {股票代碼: 股票名稱} 的字典
        """
        self.stock_listbox.delete(0, tk.END)
        for code, name in sorted(stocks.items()):
            self.stock_listbox.insert(tk.END, f"{code} - {name}")

    def update_watchlist(self, stocks_data: Dict[str, Dict]):
        """
        更新右側觀察清單
        
        Args:
            stocks_data: {股票代碼: 股票資訊} 的字典
        """
        # 清空現有卡片
        for widget in self.stocks_container.winfo_children():
            widget.destroy()

        if not stocks_data:
            # 顯示空白提示
            self.empty_label = tk.Label(
                self.stocks_container,
                text="⬅️  從左邊選擇股票加入觀察清單",
                font=self.font_normal,
                fg="#999999",
                pady=50
            )
            self.empty_label.pack()
        else:
            # 顯示股票卡片
            for stock_code in sorted(stocks_data.keys()):
                try:
                    stock_info = stocks_data[stock_code]
                    
                    # 驗證資料格式
                    if not isinstance(stock_info, dict):
                        print(f"⚠️  股票 {stock_code} 資料格式錯誤，已跳過")
                        continue
                    
                    # 提取股票資訊
                    card_data = {
                        "stock_name": stock_info.get("stock_name", "N/A"),
                        "success": stock_info.get("success", False),
                        "data": stock_info.get("data", {})
                    }
                    
                    # 確保 data 是字典
                    if not isinstance(card_data["data"], dict):
                        card_data["data"] = {}
                    
                    self._create_stock_card(stock_code, card_data)
                except Exception as e:
                    print(f"✗ 創建股票卡片失敗 {stock_code}: {e}")
                    continue

    def update_last_update_time(self, time_str: str):
        """
        更新最後更新時間顯示
        
        Args:
            time_str: 時間字符串
        """
        self.update_time_label.config(text=f"最後更新: {time_str}")

    def set_update_button_state(self, enabled: bool):
        """
        設定更新按鈕狀態
        
        Args:
            enabled: 是否啟用
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        self.update_button.config(state=state)

    def show_error(self, title: str, message: str):
        """
        顯示錯誤對話框
        
        Args:
            title: 標題
            message: 訊息
        """
        messagebox.showerror(title, message)

    def show_info(self, title: str, message: str):
        """
        顯示資訊對話框
        
        Args:
            title: 標題
            message: 訊息
        """
        messagebox.showinfo(title, message)

    # 回調方法
    def _on_add_stock_clicked(self):
        """加入按鈕被點擊"""
        selection = self.stock_listbox.curselection()
        if selection:
            index = selection[0]
            item_text = self.stock_listbox.get(index)
            stock_code = item_text.split(" - ")[0].strip()
            if self.on_add_stock:
                self.on_add_stock(stock_code)
        else:
            self.show_error("選擇錯誤", "請先選擇一支股票")

    def _on_stock_selected(self):
        """股票被雙擊選擇"""
        self._on_add_stock_clicked()

    def _on_remove_stock_clicked(self, stock_code: str):
        """移除按鈕被點擊"""
        if self.on_remove_stock:
            self.on_remove_stock(stock_code)

    def _on_manual_update_clicked(self):
        """手動更新按鈕被點擊"""
        if self.on_manual_update:
            self.on_manual_update()

    def _on_search(self):
        """搜尋框內容改變"""
        if self.on_search:
            keyword = self.search_entry.get()
            self.on_search(keyword)

    def _on_mousewheel(self, event):
        """滑鼠滾輪滾動"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
