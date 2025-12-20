# 台灣股票即時監控系統 - 完整使用指南

> ⭐ **最新修復 (2025-01-13)**：新增股票不出現在 UI 中的問題已解決！新增股票後現在會立即顯示「載入中...」狀態，然後自動更新為實際資料。詳見 [FIX_COMPLETION_SUMMARY.md](./FIX_COMPLETION_SUMMARY.md)

## 📋 專案概述

這是一個基於 **Tkinter** 的台灣股市即時監控桌面應用程式，提供：
- ✅ 多支股票實時追蹤
- ✅ 異步並行爬取股票資訊
- ✅ 每分鐘自動更新
- ✅ 手動立即更新
- ✅ 股票代碼/名稱搜尋
- ✅ 觀察清單持久化（JSON）
- ✅ 16號字體大小（清晰易讀）

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
# 方式 1: 使用 uv
cd d:\Study\2025_Python_Crawel
uv sync

# 方式 2: 使用 pip
pip install crawl4ai twstock
```

### 2. 執行應用程式

```bash
cd lesson08_1
python main.py
```

應用程式視窗將立即打開！

---

## 📁 專案結構

```
lesson08_1/
├── main.py              # 主程式 - 整合爬蟲與 UI
├── stock_crawler.py     # 爬蟲模組 - 異步爬取股票資訊
├── data_manager.py      # 資料管理層 - 觀察清單與快取
├── ui_manager.py        # UI 模組 - Tkinter 介面
├── lesson8_1_1.py       # 參考實作 1
├── lesson8_1_2.py       # 參考實作 2
├── lesson8_1_3.py       # 參考實作 3（爬蟲邏輯）
├── stock_watchlist.json # 觀察清單資料（自動生成）
├── play.md              # 專案規劃文件
└── README.md            # 本文件
```

---

## 🎯 功能說明

### 左側面板：股票選擇區

#### 搜尋功能
- 在「搜尋股票:」欄位輸入
- 支援股票代碼搜尋（例如：2330）
- 支援股票名稱搜尋（例如：台積電）
- 即時篩選結果

#### 股票清單
- 顯示所有可選擇的台灣股票
- **雙擊** 股票名稱直接加入
- 或選擇後點擊「➕ 加入觀察清單」按鈕

### 右側面板：觀察清單

#### 股票資訊卡片
每支股票顯示：
- **股票代碼與名稱** （16號加粗字體）
- **即時價格** （16號，漲紅跌綠）
- **漲跌幅度與百分比** （16號，同漲跌顏色）
- **開盤價、最高價、最低價** （16號）
- **成交量** （16號）
- **前一日收盤價** （16號）
- **更新時間** （16號）
- **❌ 移除按鈕** - 點擊移除該股票

### 頂部工具欄

- **標題**：📈 台灣股票即時監控系統
- **🔄 手動更新按鈕**：立即刷新所有觀察股票
- **最後更新**：顯示上次更新時間戳記

---

## ⏱️ 自動更新機制

- **更新頻率**：每 60 秒自動更新一次
- **更新範圍**：僅更新觀察清單中的股票
- **更新方式**：在背景執行緒執行，不阻塞 UI
- **時間戳記**：自動顯示最後更新時間

---

## 💾 資料持久化

### stock_watchlist.json

應用程式會自動保存觀察清單到 `stock_watchlist.json`：

```json
{
  "watchlist": ["2330", "2317", "2454"],
  "last_updated": "2025-12-20T13:30:45.123456"
}
```

重啟應用程式時，自動加載上次保存的觀察清單。

---

## 🔧 技術架構

### 爬蟲模組 (stock_crawler.py)

```python
# 主要函數

async fetch_multiple_stocks(stock_codes, max_concurrent=5)
  ├─ 使用 crawl4ai AsyncWebCrawler
  ├─ 限制並行數量（避免過載）
  ├─ JSON CSS 提取策略
  └─ 返回: {stock_code: {success, data}}

get_mock_stock_data(stock_code)
  └─ 爬蟲失敗時的備用資料
```

### 資料管理層 (data_manager.py)

```python
# 主要類別

class StockDataManager
  ├─ add_to_watchlist(stock_code)      # 加入觀察清單
  ├─ remove_from_watchlist(stock_code) # 移除觀察清單
  ├─ update_stock_data(code, data)     # 更新資料快取
  ├─ get_last_update_time()            # 獲取更新時間
  └─ _save_watchlist()                 # 保存到 JSON

class StockListManager
  ├─ get_all_stocks()     # 取得所有股票
  ├─ search_stocks(keyword) # 搜尋股票
  └─ get_stock_name(code)  # 獲取股票名稱
```

### UI 模組 (ui_manager.py)

```python
class StockMonitorUI
  ├─ _create_toolbar()        # 頂部工具欄
  ├─ _create_left_panel()     # 左側股票選擇區
  ├─ _create_right_panel()    # 右側觀察清單
  ├─ _create_stock_card()     # 股票資訊卡片
  ├─ update_stock_list()      # 更新左側清單
  ├─ update_watchlist()       # 更新右側卡片
  └─ update_last_update_time()# 更新時間戳記
```

### 主應用程式 (main.py)

```python
class StockMonitorApp
  ├─ add_stock_to_watchlist()    # 加入股票
  ├─ remove_stock_from_watchlist()# 移除股票
  ├─ manual_update()              # 手動更新
  ├─ update_stock_data()          # 背景更新
  ├─ schedule_auto_update()       # 排定自動更新
  └─ process_queue()              # 處理爬蟲結果
```

### 執行流程

```
UI 操作 (add_stock)
   ↓
StockMonitorApp.add_stock_to_watchlist()
   ├─ DataManager.add_to_watchlist()
   ├─ 發起背景更新任務
   └─ 排隊更新結果
   ↓
背景執行緒 (_fetch_and_update)
   ├─ 調用 fetch_multiple_stocks()
   ├─ crawl4ai 爬蟲執行
   └─ 結果放入隊列
   ↓
主執行緒 (process_queue)
   ├─ 取出爬蟲結果
   ├─ DataManager.update_stock_data()
   ├─ UI.refresh_watchlist_display()
   └─ UI.update_last_update_time()
```

---

## 📊 股票資訊來源

- **URL**: `https://www.wantgoo.com/stock/{stock_code}/technical-chart`
- **提取方式**: CSS 選擇器 + JSON 提取
- **提取欄位**:
  - 股票號碼、名稱
  - 即時價格、漲跌、漲跌百分比
  - 開盤價、最高價、最低價
  - 成交量、前一日收盤價、更新時間

---

## 🎨 UI 特性

### 字體設定

- **標題**: 16 號加粗（微軟正黑體）
- **一般文字**: 16 號（微軟正黑體）
- **小文字**: 14 號（微軟正黑體）

### 顏色編碼

- **漲幅**：紅色 (#ff0000)
- **跌幅**：綠色 (#00aa00)
- **正常**：黑色 (#000000)
- **背景**：淺灰色 (#f0f0f0)

### 響應式設計

- 左右兩欄自動調整寬度
- 股票卡片自動換行
- 滾動條自動出現

---

## 🧪 測試

### 基礎功能測試

1. **啟動應用程式**
   ```bash
   python main.py
   ```

2. **搜尋股票**
   - 在搜尋框輸入「2330」或「台積電」
   - 驗證搜尋結果正確

3. **加入觀察清單**
   - 雙擊「2330 - 台積電」
   - 驗證股票卡片出現在右側

4. **檢查資料格式**
   - 驗證股票資訊正確顯示
   - 驗證漲跌顏色正確

5. **移除股票**
   - 點擊股票卡片上的「❌ 移除」按鈕
   - 驗證股票被移除

6. **手動更新**
   - 點擊「🔄 手動更新」
   - 驗證時間戳記更新

7. **自動更新**
   - 等待 60 秒
   - 驗證時間戳記自動更新

### 預期輸出

```
============================================================
📈 台灣股票即時監控系統
============================================================
⚠️  twstock 未安裝，使用預設股票清單
初始化應用程式...
觀察清單為空
[Tkinter 視窗打開]
```

---

## ⚠️ 常見問題

### Q: 應用程式無法啟動
**A**: 確保已安裝所有依賴
```bash
pip install crawl4ai
```

### Q: 爬蟲無法取得資料
**A**: 應用程式會自動使用模擬資料（MOCK_RATES），確保功能可用

### Q: UI 字體太小/太大
**A**: 編輯 `ui_manager.py` 中的字體設定：
```python
self.font_normal = ("微軟正黑體", 16)  # 改為所需大小
```

### Q: 觀察清單重啟後不見了
**A**: 檢查 `stock_watchlist.json` 檔案是否存在

---

## 🔄 後續改進建議

1. **更多股票來源**
   - 支援台灣證券交易所 API
   - 支援 YahooFinance 資料源

2. **數據分析**
   - 價格趨勢圖表
   - 漲跌統計
   - 成交量分析

3. **警報功能**
   - 價格達到閾值時通知
   - 漲跌百分比超過設定時提示

4. **進階功能**
   - 匯出觀察清單為 CSV/Excel
   - 多個觀察清單組
   - 自動交易提示

5. **效能優化**
   - 數據庫儲存（SQLite）
   - 資料快取層
   - 批次更新優化

---

## 📞 技術支援

如有問題，請檢查：

1. **Python 版本**: 需要 >= 3.10
2. **依賴安裝**: `pip list | grep crawl4ai`
3. **網路連線**: 確保可訪問 wantgoo.com
4. **終端日誌**: 查看啟動時的錯誤訊息
5. **JSON 檔案**: `stock_watchlist.json` 格式是否正確

---

## 📄 檔案說明

| 檔案 | 說明 |
|------|------|
| `main.py` | 主程式 - 應用邏輯整合 |
| `stock_crawler.py` | 爬蟲模組 - 網頁爬取與資料提取 |
| `data_manager.py` | 資料層 - 快取與持久化管理 |
| `ui_manager.py` | UI 模組 - Tkinter 介面實現 |
| `stock_watchlist.json` | 觀察清單（自動生成） |

---

## 📌 注意事項

1. **遵守服務條款**
   - 合理設定爬取頻率（目前為 1 分鐘）
   - 不對目標網站造成負擔

2. **市場時間**
   - 台灣股市交易時間：9:00-13:30
   - 可根據市場時間調整更新頻率

3. **效能**
   - 同時追蹤股票數建議不超過 50 支
   - 爬取超時時間設為 30 秒

4. **備用機制**
   - 爬蟲失敗時自動使用模擬資料
   - 確保應用程式穩定運行

---

**版本**: 1.0  
**最後更新**: 2025-12-20  
**開發環境**: Python 3.10+, Tkinter, crawl4ai 0.7.7  
**作者**: 台北市職能發展學院 - Python 爬蟲課程
