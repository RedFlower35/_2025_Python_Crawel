"""
資料管理層
管理股票觀察清單、快取資料和更新時間
"""
import json
from datetime import datetime
from typing import Dict, Set, Optional
from pathlib import Path


class StockDataManager:
    """股票資料管理器"""

    def __init__(self, data_file: str = "stock_watchlist.json"):
        """
        初始化資料管理器
        
        Args:
            data_file: 儲存觀察清單的 JSON 檔案路徑
        """
        self.data_file = Path(data_file)
        self.watchlist: Set[str] = set()  # 觀察清單
        self.stock_data: Dict[str, Dict] = {}  # 股票資料快取
        self.last_update_time: Optional[datetime] = None  # 最後更新時間

        # 加載既有資料
        self._load_watchlist()

    def _load_watchlist(self):
        """從檔案加載觀察清單"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.watchlist = set(data.get('watchlist', []))
                    print(f"✓ 加載觀察清單: {len(self.watchlist)} 支股票")
            except Exception as e:
                print(f"✗ 加載觀察清單失敗: {e}")
                self.watchlist = set()
        else:
            self.watchlist = set()

    def _save_watchlist(self):
        """保存觀察清單到檔案"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'watchlist': list(self.watchlist),
                    'last_updated': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"✗ 保存觀察清單失敗: {e}")

    def add_to_watchlist(self, stock_code: str) -> bool:
        """
        將股票加入觀察清單
        
        Args:
            stock_code: 股票代碼
        
        Returns:
            是否成功加入（True=成功，False=已存在）
        """
        if stock_code not in self.watchlist:
            self.watchlist.add(stock_code)
            self._save_watchlist()
            return True
        return False

    def remove_from_watchlist(self, stock_code: str) -> bool:
        """
        從觀察清單移除股票
        
        Args:
            stock_code: 股票代碼
        
        Returns:
            是否成功移除
        """
        if stock_code in self.watchlist:
            self.watchlist.discard(stock_code)
            # 同時移除快取資料
            if stock_code in self.stock_data:
                del self.stock_data[stock_code]
            self._save_watchlist()
            return True
        return False

    def is_in_watchlist(self, stock_code: str) -> bool:
        """
        檢查股票是否在觀察清單中
        
        Args:
            stock_code: 股票代碼
        
        Returns:
            是否在觀察清單中
        """
        return stock_code in self.watchlist

    def get_watchlist(self) -> list:
        """
        獲取觀察清單
        
        Returns:
            股票代碼清單
        """
        return sorted(list(self.watchlist))

    def clear_watchlist(self):
        """清空觀察清單"""
        self.watchlist.clear()
        self.stock_data.clear()
        self._save_watchlist()

    def update_stock_data(self, stock_code: str, data: Dict):
        """
        更新股票資料快取
        
        Args:
            stock_code: 股票代碼
            data: 股票資料字典
        """
        self.stock_data[stock_code] = data
        self.last_update_time = datetime.now()

    def get_stock_data(self, stock_code: str) -> Optional[Dict]:
        """
        獲取股票資料
        
        Args:
            stock_code: 股票代碼
        
        Returns:
            股票資料字典，不存在時返回 None
        """
        return self.stock_data.get(stock_code)

    def get_all_stock_data(self) -> Dict[str, Dict]:
        """
        獲取所有股票資料
        
        Returns:
            所有股票資料的字典
        """
        return self.stock_data.copy()

    def get_last_update_time(self) -> Optional[str]:
        """
        獲取最後更新時間（格式化字符串）
        
        Returns:
            時間字符串，格式: "YYYY-MM-DD HH:MM:SS"
        """
        if self.last_update_time:
            return self.last_update_time.strftime("%Y-%m-%d %H:%M:%S")
        return None

    def get_last_update_datetime(self) -> Optional[datetime]:
        """
        獲取最後更新時間（datetime 物件）
        
        Returns:
            datetime 物件
        """
        return self.last_update_time


class StockListManager:
    """台灣股票清單管理器"""

    def __init__(self):
        """初始化股票清單管理器"""
        self.all_stocks = self._load_stock_list()

    def _load_stock_list(self) -> Dict[str, str]:
        """
        加載台灣股票清單
        
        Returns:
            {股票代碼: 股票名稱} 的字典
        """
        try:
            # 首先嘗試使用本地的完整股票列表
            from taiwan_stocks import get_all_stocks_dict
            stocks = get_all_stocks_dict()
            print(f"✓ 已加載 {len(stocks)} 支台灣股票和 ETF")
            return stocks
        except ImportError:
            print("⚠️  taiwan_stocks 模組未找到，嘗試使用 twstock...")
            try:
                import twstock
                # 取得所有上市股票
                stocks = {}
                # 使用 twstock 的上市公司清單
                for sid, name in twstock.twse_tickers.items():
                    stocks[sid] = name
                return stocks
            except ImportError:
                print("⚠️  twstock 未安裝，使用預設股票清單")
                return self._get_default_stock_list()
            except Exception as e:
                print(f"⚠️  加載股票清單失敗: {e}，使用預設清單")
                return self._get_default_stock_list()

    def _get_default_stock_list(self) -> Dict[str, str]:
        """
        預設股票清單（大型股）
        
        Returns:
            {股票代碼: 股票名稱} 的字典
        """
        return {
            "2330": "台積電",
            "2317": "鴻海",
            "2454": "聯發科",
            "2412": "中華電",
            "2308": "台達電",
            "1101": "台泥",
            "1213": "大飯店",
            "1216": "統一",
            "1301": "台塑",
            "1303": "南亞",
            "1326": "台化",
            "1402": "遠東新",
            "1590": "亞德客",
            "1605": "華新",
            "2002": "鑫新",
            "2105": "正新",
            "2203": "台塑化",
            "2207": "和泰",
            "2301": "光磊",
            "2327": "光磊",
            "2382": "廣達",
            "2390": "互盛",
            "2408": "南亞科",
            "2409": "友達",
            "2436": "偉詮電",
            "2880": "華新",
            "3008": "大立光",
            "3045": "台灣大",
            "4904": "遠傳",
            "6505": "恆耀",
        }

    def get_all_stocks(self) -> Dict[str, str]:
        """
        獲取所有股票清單
        
        Returns:
            {股票代碼: 股票名稱} 的字典
        """
        return self.all_stocks.copy()

    def search_stocks(self, keyword: str) -> Dict[str, str]:
        """
        搜尋股票（支援代碼和名稱搜尋）
        
        Args:
            keyword: 搜尋關鍵字（代碼或名稱）
        
        Returns:
            符合條件的 {股票代碼: 股票名稱} 字典
        """
        keyword_upper = keyword.upper()
        results = {}

        for code, name in self.all_stocks.items():
            # 搜尋代碼
            if code.startswith(keyword_upper):
                results[code] = name
            # 搜尋名稱
            elif keyword in name:
                results[code] = name

        return results

    def get_stock_name(self, stock_code: str) -> Optional[str]:
        """
        根據代碼獲取股票名稱
        
        Args:
            stock_code: 股票代碼
        
        Returns:
            股票名稱，不存在時返回 None
        """
        return self.all_stocks.get(stock_code)
