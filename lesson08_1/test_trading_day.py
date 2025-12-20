#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
測試前一交易日計算邏輯
"""
from datetime import datetime, timedelta

def test_trading_day_calculation():
    """測試交易日計算"""
    today = datetime.now()
    print(f"📅 今日: {today.strftime('%Y-%m-%d %A')}")
    print()
    
    # 計算前一交易日
    for i in range(1, 4):
        prev_day = today - timedelta(days=i)
        weekday_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][prev_day.weekday()]
        is_trading = 'yes' if prev_day.weekday() < 5 else 'no'
        print(f"往前推 {i} 天: {prev_day.strftime('%Y-%m-%d')} ({weekday_name}) - 交易日: {is_trading}")
        if prev_day.weekday() < 5:
            print(f"\n✓ 前一交易日: {prev_day.strftime('%Y-%m-%d')}")
            break
    
    print("\n✅ 交易日計算邏輯驗證完成")

if __name__ == "__main__":
    test_trading_day_calculation()
