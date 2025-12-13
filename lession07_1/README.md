# 台幣匯率轉換系統 - 使用說明

## 📋 專案結構

```
lession7_1/
├── main.py              # Streamlit 主程式
├── crawler.py           # 匯率爬蟲模組
├── test_basic.py        # 基礎測試腳本
├── AGENTS.md            # 專案需求文件
└── README.md            # 本文件
```

## 🚀 快速啟動

### 1. 安裝依賴
```bash
# 使用 uv (推薦)
uv sync

# 或使用 pip
pip install streamlit crawl4ai pandas
```

### 2. 運行應用
```bash
# 進入專案目錄
cd lession7_1

# 執行 Streamlit
streamlit run main.py
```

應用將在瀏覽器打開: `http://localhost:8501`

## 📱 功能說明

### 左欄：匯率計算
- **輸入台幣金額**: 輸入要轉換的台幣金額
- **選擇目標貨幣**: 從下拉選單選擇要轉換的貨幣
- **自動計算**: 實時顯示轉換結果
- **邊界處理**: 
  - 金額為 0 時顯示提示
  - 無匯率資料時顯示「暫停交易」

### 右欄：匯率資料表格
- **匯率表格**: 顯示所有可交易貨幣的匯率資訊
- **統計資訊**: 
  - 可交易貨幣數
  - 總貨幣數
  - 自動更新間隔
- **轉換示例**: 每種貨幣顯示 1000 TWD 轉換後的金額

### 自動更新
- **時間間隔**: 每 10 分鐘自動更新一次匯率
- **時間戳記**: 顯示上次更新時間
- **降級機制**: 如果爬蟲失敗，自動使用測試匯率資料

### 手動更新
- **手動更新按鈕**: 點擊「🔄 手動更新」立即刷新匯率
- **設定按鈕**: 預留的設定選項按鈕

## 🔧 技術架構

### crawler.py 模組
```python
# 主要函數

fetch_exchange_rates()
  ↳ 使用 crawl4ai 爬取匯率資料
  ↳ 返回: {currency: {rate, status}}

_parse_exchange_rates(html)
  ↳ 解析 HTML 為匯率資料
  
_parse_exchange_rates_fallback(html)
  ↳ 備用解析方法（正則表達式）

get_exchange_rates()
  ↳ 同步包裝函數（供 Streamlit 使用）

get_mock_rates()
  ↳ 返回測試匯率資料
```

### main.py 邏輯流程
```
initialize_session_state()
    ↓
should_auto_update()
    ├─ YES → update_exchange_rates()
    └─ NO  → 使用現有資料
    ↓
render_left_column()
    └─ 匯率計算功能
    ↓
render_right_column()
    └─ 匯率表格和統計
```

## 📊 資料格式

### 匯率資料結構
```json
{
  "USD": {
    "rate": "31.50",
    "status": "交易中"
  },
  "JPY": {
    "rate": "0.21",
    "status": "交易中"
  }
}
```

### 表格格式
| 貨幣 | 匯率 | 狀態 | 轉換 1000 TWD |
|------|------|------|--------------|
| USD | 31.5000 | 交易中 | 31.75 |
| JPY | 0.2100 | 交易中 | 4761.90 |

## 🧪 測試

### 運行基礎測試
```bash
python test_basic.py
```

### 預期輸出
```
✅ crawler.py 導入成功
✅ 獲取模擬匯率資料: 10 種貨幣
  USD: 31.5
  JPY: 0.21
  EUR: 34.5

✅ 所有測試通過！
```

## 🌐 爬蟲來源

- **URL**: `https://rate.bot.com.tw/xrt?Lang=zh-TW`
- **方式**: 台灣銀行即時匯率
- **更新頻率**: 每 10 分鐘自動更新（可配置）

## 💾 測試資料

當爬蟲無法正常運作時，系統會自動使用以下測試匯率：

```python
MOCK_RATES = {
    'USD': 31.50,
    'JPY': 0.21,
    'EUR': 34.50,
    'GBP': 39.80,
    'AUD': 21.00,
    'CAD': 23.50,
    'SGD': 23.80,
    'HKD': 4.00,
    'CNY': 4.30,
    'KRW': 0.024,
}
```

## 🎨 UI 特性

- **響應式設計**: 左右兩欄自動調整寬度
- **顏色編碼**: 
  - 結果框使用藍色背景
  - 警告訊息使用紅色背景
  - 普通資訊使用灰色背景
- **圖示**: 使用 emoji 增強視覺效果
- **表格**: 支援排序和搜尋（Streamlit 內置）

## ⚙️ 配置

### 修改更新間隔
編輯 `main.py` 中的 `initialize_session_state()`:
```python
st.session_state.update_interval = 10  # 改為所需分鐘數
```

### 修改爬蟲 URL
編輯 `crawler.py` 中的 `fetch_exchange_rates()`:
```python
result = await crawler.arun(
    url='新的URL',
    config=run_config
)
```

## 🐛 疑難排除

### 問題: 「暫停交易」一直顯示
**解決**: 
1. 點擊「🔄 手動更新」
2. 檢查網路連線
3. 確認爬蟲 URL 是否仍然有效

### 問題: 找不到模組
**解決**:
```bash
pip install streamlit crawl4ai pandas
```

### 問題: 匯率資料為空
**解決**:
1. 爬蟲會自動降級到測試資料
2. 檢查 `test_basic.py` 是否運行正常
3. 查看終端日誌確認錯誤訊息

## 📝 需求實現檢查表

- [x] 使用 crawl4ai 爬蟲爬取匯率資料
- [x] 使用 Streamlit 套件
- [x] 版面分為 2 欄（左右）
- [x] 左邊欄位為計算匯率
- [x] 右邊為使用表格顯示匯率資料
- [x] 每隔 10 分鐘執行 1 次自動更新
- [x] 建立手動更新功能
- [x] 欄位為空時顯示「暫停交易」
- [x] 右邊欄位顯示台幣轉換為其他貨幣
- [x] 讓使用者輸入交易的金額
- [x] 無法交易的貨幣不顯示出來

## 🔄 後續改進建議

1. **資料庫支援**: 儲存歷史匯率以便分析
2. **多源爬蟲**: 同時爬取多個銀行的匯率進行比較
3. **警報功能**: 當匯率達到設定的閾值時發出通知
4. **圖表展示**: 顯示匯率走勢圖表
5. **匯出功能**: 支持將匯率資料匯出為 CSV/Excel

## 📄 檔案說明

| 檔案 | 說明 |
|------|------|
| `main.py` | Streamlit 主程式，提供 UI 和主要邏輯 |
| `crawler.py` | 爬蟲模組，負責網頁爬取和資料解析 |
| `test_basic.py` | 測試腳本，驗證爬蟲功能 |
| `AGENTS.md` | 原始需求文件 |

## 📞 技術支援

如有問題，請檢查:
1. Python 版本 >= 3.10
2. 所有依賴套件已安裝
3. 網路連線正常
4. 爬蟲源 URL 可訪問

---

**版本**: 1.0  
**最後更新**: 2025-12-13  
**作者**: 台北市職能發展學院 - Python 爬蟲課程
