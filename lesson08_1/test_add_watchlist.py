"""
測試新增股票到觀察清單的功能
"""
import sys
from pathlib import Path

# 加入專案路徑
sys.path.insert(0, str(Path(__file__).parent))

from data_manager import StockDataManager
from taiwan_stocks import get_all_stocks_dict


def test_add_to_watchlist():
    """測試新增股票到觀察清單"""
    print("=== 測試新增股票到觀察清單 ===\n")
    
    # 獲取股票名稱字典
    all_stocks = get_all_stocks_dict()
    
    # 初始化資料管理器
    dm = StockDataManager("test_watchlist.json")
    
    # 1. 測試新增股票
    print("1. 測試新增股票...")
    test_stock = "2330"  # 台積電
    result = dm.add_to_watchlist(test_stock)
    print(f"   新增 {test_stock}: {result}")
    
    # 2. 檢查 watchlist
    print("\n2. 檢查 watchlist...")
    watchlist = dm.get_watchlist()
    print(f"   觀察清單: {watchlist}")
    print(f"   股票在清單中: {test_stock in watchlist}")
    
    # 3. 檢查資料（應該還沒有）
    print("\n3. 檢查資料...")
    all_data = dm.get_all_stock_data()
    print(f"   資料中有該股票: {test_stock in all_data}")
    
    # 4. 手動添加模擬資料
    print("\n4. 添加模擬資料...")
    stock_name = all_stocks.get(test_stock, "未知")
    mock_stock_data = {
        "stock_code": test_stock,
        "stock_name": stock_name,
        "success": True,
        "data": {
            "price": 1000.00,
            "change": 10.00,
            "change_percent": 1.01,
            "date": "2025-01-01"
        },
        "timestamp": "2025-01-01T10:00:00"
    }
    dm.update_stock_data(test_stock, mock_stock_data)
    
    # 5. 再次檢查資料
    print("\n5. 再次檢查資料...")
    all_data = dm.get_all_stock_data()
    print(f"   資料中有該股票: {test_stock in all_data}")
    if test_stock in all_data:
        print(f"   股票資料: {all_data[test_stock]}")
    
    # 6. 清理
    import os
    if os.path.exists("test_watchlist.json"):
        os.remove("test_watchlist.json")
    print("\n✓ 測試完成！")


if __name__ == "__main__":
    test_add_to_watchlist()
