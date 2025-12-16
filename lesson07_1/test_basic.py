"""
快速測試爬蟲和主程式邏輯
"""
import sys
sys.path.insert(0, r'd:\Study\2025_Python_Crawel\lesson7_1')

try:
    from crawler import get_mock_rates
    print("✅ crawler.py 導入成功")
    
    # 測試模擬資料
    rates = get_mock_rates()
    print(f"✅ 獲取模擬匯率資料: {len(rates)} 種貨幣")
    
    # 測試格式化
    for currency, data in list(rates.items())[:3]:
        rate = float(data.get('rate', '0'))
        print(f"  {currency}: {rate}")
    
    print("\n✅ 所有測試通過！")
    print("\n可用的貨幣:")
    for currency in sorted(rates.keys()):
        print(f"  - {currency}")
    
except ImportError as e:
    print(f"❌ 導入錯誤: {e}")
except Exception as e:
    print(f"❌ 執行錯誤: {e}")
