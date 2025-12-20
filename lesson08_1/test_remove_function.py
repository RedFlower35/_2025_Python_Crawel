"""
移除功能測試
驗證修復後的移除功能是否正常工作
"""
import sys
sys.path.insert(0, r'd:\Study\2025_Python_Crawel\lesson08_1')

from data_manager import StockDataManager

def test_remove_stock():
    """測試移除股票功能"""
    print("=" * 60)
    print("測試: 移除股票功能")
    print("=" * 60)
    
    # 建立資料管理器
    dm = StockDataManager("test_watchlist.json")
    
    # 測試 1: 加入股票
    print("\n[測試 1] 加入股票...")
    result = dm.add_to_watchlist("2330")
    assert result == True, "加入股票失敗"
    print("✓ 成功加入 2330")
    
    # 驗證股票在清單中
    assert dm.is_in_watchlist("2330"), "股票不在清單中"
    print("✓ 確認 2330 在清單中")
    
    # 測試 2: 更新股票資料
    print("\n[測試 2] 更新股票資料...")
    stock_data = {
        "stock_code": "2330",
        "stock_name": "台積電",
        "success": True,
        "data": {
            "即時價格": "1000.00",
            "漲跌": "+10.00",
            "漲跌百分比": "+1.00%"
        }
    }
    dm.update_stock_data("2330", stock_data)
    print("✓ 成功更新股票資料")
    
    # 驗證資料格式
    retrieved_data = dm.get_stock_data("2330")
    assert retrieved_data is not None, "無法檢索股票資料"
    assert isinstance(retrieved_data, dict), "資料格式錯誤"
    assert retrieved_data.get("success") == True, "success 應為 True"
    assert isinstance(retrieved_data.get("data"), dict), "data 應為字典"
    print("✓ 資料格式驗證通過")
    
    # 測試 3: 移除股票
    print("\n[測試 3] 移除股票...")
    result = dm.remove_from_watchlist("2330")
    assert result == True, "移除股票失敗"
    print("✓ 成功移除 2330")
    
    # 驗證股票已移除
    assert not dm.is_in_watchlist("2330"), "股票仍在清單中"
    print("✓ 確認 2330 已從清單移除")
    
    # 驗證資料已清除
    retrieved_data = dm.get_stock_data("2330")
    assert retrieved_data is None, "資料應已被刪除"
    print("✓ 確認股票資料已清除")
    
    # 測試 4: 邊界情況
    print("\n[測試 4] 邊界情況...")
    
    # 移除不存在的股票
    result = dm.remove_from_watchlist("9999")
    assert result == False, "移除不存在的股票應返回 False"
    print("✓ 移除不存在的股票返回 False")
    
    # 加入同一支股票兩次
    dm.add_to_watchlist("2330")
    result = dm.add_to_watchlist("2330")
    assert result == False, "再次加入同一支股票應返回 False"
    print("✓ 再次加入同一支股票返回 False")
    
    print("\n" + "=" * 60)
    print("✅ 所有測試通過！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_remove_stock()
    except AssertionError as e:
        print(f"\n❌ 測試失敗: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
