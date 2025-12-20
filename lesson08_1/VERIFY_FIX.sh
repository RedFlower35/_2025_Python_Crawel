#!/bin/bash
# 修復驗證清單 - 檢查是否正確應用了修復

echo "================================"
echo "✅ 股票監控應用 - 修復驗證清單"
echo "================================"
echo ""

# 1. 檢查代碼修改
echo "1️⃣ 檢查代碼修改..."
if grep -q "載入中" main.py; then
    echo "   ✅ 佔位符代碼已找到"
else
    echo "   ❌ 佔位符代碼未找到"
fi

# 2. 檢查語法
echo ""
echo "2️⃣ 檢查 Python 語法..."
if python -m py_compile main.py 2>/dev/null; then
    echo "   ✅ 代碼語法正確"
else
    echo "   ❌ 代碼語法錯誤"
fi

# 3. 檢查文檔
echo ""
echo "3️⃣ 檢查文檔..."
docs=("FIX_COMPLETION_SUMMARY.md" "UI_FIX_REPORT.md" "QUICK_TEST_GUIDE.md" "LATEST_FIX_SUMMARY.md")
for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "   ✅ $doc"
    else
        echo "   ❌ $doc 缺失"
    fi
done

# 4. 檢查測試
echo ""
echo "4️⃣ 檢查測試文件..."
if [ -f "test_add_watchlist.py" ]; then
    echo "   ✅ test_add_watchlist.py"
else
    echo "   ❌ test_add_watchlist.py 缺失"
fi

# 5. 檢查數據文件
echo ""
echo "5️⃣ 檢查數據文件..."
if [ -f "stock_watchlist.json" ]; then
    echo "   ✅ stock_watchlist.json (存在)"
else
    echo "   ℹ️  stock_watchlist.json (將在首次運行時創建)"
fi

echo ""
echo "================================"
echo "✨ 驗證完成！"
echo "================================"
echo ""
echo "📝 建議的下一步："
echo "1. 運行應用: python main.py"
echo "2. 按照 QUICK_TEST_GUIDE.md 中的步驟進行測試"
echo "3. 驗證新增股票功能是否正常工作"
echo ""
