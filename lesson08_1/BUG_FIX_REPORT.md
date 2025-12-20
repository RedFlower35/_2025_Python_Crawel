# 移除股票功能 Bug 修復報告

## 🐛 問題描述

用戶點擊「❌ 移除」按鈕時出現崩潰，錯誤信息：

```
AttributeError: 'NoneType' object has no attribute 'get'
```

錯誤棧跟蹤顯示：
- `ui_manager.py` 第 264 行：`change_text = price_info.get("漲跌", "N/A")`
- 原因：`price_info` 為 `None`，無法調用 `.get()` 方法

---

## 📊 根本原因分析

### 錯誤流程

```
用戶點擊「❌ 移除」按鈕
  ↓
_on_remove_stock_clicked(stock_code)  # ui_manager.py:256
  ↓
remove_stock_from_watchlist(stock_code)  # main.py:124
  ├─ DataManager.remove_from_watchlist()
  ├─ 刪除快取中的股票資料
  └─ 調用 refresh_watchlist_display()  # main.py:140
      ↓
      update_watchlist(displayed_data)  # ui_manager.py:409
        ↓
        _create_stock_card(stock_code, card_data)  # ui_manager.py:411
          ↓
          price_info = card_data.get("data")  # 可能為 None
            ↓
            price_info.get("漲跌")  # ❌ 崩潰！
```

### 根本原因

1. `stock_data.get("data")` 返回 `None` 而不是空字典
2. 後續代碼假設 `price_info` 是字典，直接調用 `.get()` 方法
3. 沒有類型檢查導致 NoneType 錯誤

---

## ✅ 修復方案

### 修改 1: ui_manager.py 第 260-267 行

**問題代碼：**
```python
price_info = stock_data.get("data", {}) if stock_data.get("success") else {}
change_text = price_info.get("漲跌", "N/A")
change_rate = price_info.get("漲跌百分比", "N/A")
```

**修復後：**
```python
price_info = stock_data.get("data") if stock_data.get("success") else None
if price_info is None:
    price_info = {}

change_text = price_info.get("漲跌", "N/A") if isinstance(price_info, dict) else "N/A"
change_rate = price_info.get("漲跌百分比", "N/A") if isinstance(price_info, dict) else "N/A"
```

**改進點：**
- 明確檢查 `price_info` 是否為 `None`
- 在調用 `.get()` 前驗證類型
- 提供安全的備用值

### 修改 2: ui_manager.py 第 277-283 行

**問題代碼：**
```python
text=f"即時價格: {price_info.get('即時價格', 'N/A')} TWD",
```

**修復後：**
```python
text=f"即時價格: {price_info.get('即時價格', 'N/A') if isinstance(price_info, dict) else 'N/A'} TWD",
```

### 修改 3: ui_manager.py 第 303-306 行 和 第 328-331 行

**修復後：**
```python
info_items = [
    ("開盤價", price_info.get("開盤價", "N/A") if isinstance(price_info, dict) else "N/A"),
    ("最高價", price_info.get("最高價", "N/A") if isinstance(price_info, dict) else "N/A"),
    ("最低價", price_info.get("最低價", "N/A") if isinstance(price_info, dict) else "N/A"),
]

right_items = [
    ("成交量", price_info.get("成交量(張)", "N/A") if isinstance(price_info, dict) else "N/A"),
    ("前一日收盤", price_info.get("前一日收盤價", "N/A") if isinstance(price_info, dict) else "N/A"),
    ("更新時間", price_info.get("日期時間", "N/A") if isinstance(price_info, dict) else "N/A"),
]
```

### 修改 4: main.py 第 135-147 行

**問題代碼：**
```python
displayed_data = {
    code: all_stock_data[code]
    for code in watchlist
    if code in all_stock_data
}
```

**修復後：**
```python
displayed_data = {}
for code in watchlist:
    if code in all_stock_data:
        stock_data = all_stock_data[code]
        # 確保資料結構正確
        if isinstance(stock_data, dict):
            displayed_data[code] = stock_data
        else:
            # 如果資料不正確，跳過此股票
            print(f"⚠️  股票 {code} 資料格式錯誤，已跳過")
```

### 修改 5: ui_manager.py 第 399-411 行

**修復後：**
```python
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
```

---

## 🧪 測試驗證

已建立測試文件 `test_remove_function.py`，驗證修復：

```bash
python test_remove_function.py
```

**測試項目：**
✅ 加入股票  
✅ 更新股票資料  
✅ 移除股票  
✅ 驗證資料已清除  
✅ 移除不存在的股票  
✅ 邊界情況處理  

**測試結果：** ✅ 所有測試通過！

---

## 📈 修復前後對比

### 修復前
```
點擊移除 → AttributeError: 'NoneType' object has no attribute 'get' → 崩潰
```

### 修復後
```
點擊移除 → 驗證資料 → 類型檢查 → 安全移除 → 重新渲染 UI → 成功
```

---

## 🛡️ 防御性編程改進

修復後的代碼加入了以下防御層：

1. **None 檢查**：明確檢查值是否為 None
2. **類型驗證**：使用 `isinstance()` 驗證資料類型
3. **備用值**：提供安全的預設值
4. **異常捕獲**：使用 try-except 處理意外情況
5. **日誌記錄**：打印詳細的錯誤信息

---

## 💡 最佳實踐

從這個 bug 學到的最佳實踐：

1. **始終驗證外部資料**：不要假設資料格式
2. **使用防御性編程**：添加類型檢查和邊界驗證
3. **提供有意義的錯誤訊息**：幫助調試
4. **編寫單元測試**：驗證邊界情況
5. **使用日誌**：追蹤執行流程

---

## 📝 檔案更新清單

- ✅ `ui_manager.py` - 修改 `_create_stock_card()` 和 `update_watchlist()`
- ✅ `main.py` - 改進 `refresh_watchlist_display()`
- ✅ `test_remove_function.py` - 新增測試文件

---

## ✨ 修復總結

**問題**：移除股票時崩潰  
**原因**：資料為 None，未進行類型檢查  
**解決**：添加 None 檢查和類型驗證  
**狀態**：✅ 修復完成，所有測試通過  

現在用戶可以安全地移除觀察清單中的股票！
