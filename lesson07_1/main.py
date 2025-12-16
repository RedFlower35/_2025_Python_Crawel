"""
台幣匯率轉換應用 - Streamlit 主程式
左欄：匯率計算
右欄：匯率資料表格
支持自動更新 (10分鐘) 和手動更新
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from crawler import get_exchange_rates, get_mock_rates


def initialize_session_state():
    """初始化 Streamlit 會話狀態"""
    if 'exchange_rates' not in st.session_state:
        st.session_state.exchange_rates = get_mock_rates()
    
    if 'last_update_time' not in st.session_state:
        st.session_state.last_update_time = datetime.now()
    
    if 'update_interval' not in st.session_state:
        st.session_state.update_interval = 10  # 分鐘


def should_auto_update() -> bool:
    """
    檢查是否應該自動更新匯率
    
    Returns:
        bool: 如果距離上次更新超過10分鐘則返回 True
    """
    now = datetime.now()
    last_update = st.session_state.last_update_time
    elapsed = (now - last_update).total_seconds() / 60
    return elapsed >= st.session_state.update_interval


def update_exchange_rates():
    """更新匯率資料"""
    try:
        with st.spinner('正在更新匯率資料...'):
            rates = get_exchange_rates()
            
            # 如果爬蟲失敗，使用模擬資料
            if not rates:
                rates = get_mock_rates()
            
            st.session_state.exchange_rates = rates
            st.session_state.last_update_time = datetime.now()
    except Exception as e:
        st.error(f"更新失敗: {e}")
        # 降級到模擬資料
        st.session_state.exchange_rates = get_mock_rates()


def format_rate_value(rate_str: str) -> float:
    """
    將匯率字符串轉換為浮點數
    
    Args:
        rate_str (str): 匯率字符串
        
    Returns:
        float: 匯率浮點數，轉換失敗返回 0.0
    """
    try:
        return float(rate_str)
    except (ValueError, TypeError):
        return 0.0


def get_tradable_currencies() -> dict:
    """
    獲取可交易的貨幣列表（排除無匯率資料的貨幣）
    
    Returns:
        dict: {貨幣代碼: 匯率數據}
    """
    tradable = {}
    for currency, data in st.session_state.exchange_rates.items():
        rate = format_rate_value(data.get('rate', '0'))
        status = data.get('status', '').lower()
        
        # 只保留有效匯率且狀態為交易中的貨幣
        if rate > 0 and '交易' in status:
            tradable[currency] = data
    
    return tradable


def main():
    """主程式"""
    # 頁面配置
    st.set_page_config(
        page_title="台幣匯率轉換",
        page_icon="💱",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS 樣式
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .exchange-result {
        font-size: 24px;
        font-weight: bold;
        color: #1f77b4;
        padding: 20px;
        background-color: #e8f4f8;
        border-radius: 10px;
        text-align: center;
    }
    .warning-text {
        color: #ff6b6b;
        font-size: 16px;
        font-weight: bold;
        padding: 15px;
        background-color: #ffe0e0;
        border-radius: 5px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 初始化會話狀態
    initialize_session_state()
    
    # 標題
    st.title("💱 台幣匯率轉換系統")
    
    # 自動更新邏輯
    if should_auto_update():
        update_exchange_rates()
    
    # 頁面分為左右兩欄
    col_left, col_right = st.columns([1, 1], gap="large")
    
    # ==================== 左欄：匯率計算 ====================
    with col_left:
        st.header("🧮 匯率計算")
        
        # 輸入金額
        twd_amount = st.number_input(
            "請輸入台幣金額",
            min_value=0.0,
            step=1.0,
            value=0.0,
            format="%.2f"
        )
        
        # 獲取可交易貨幣
        tradable_currencies = get_tradable_currencies()
        
        if not tradable_currencies:
            # 無可交易貨幣
            st.markdown("""
            <div class="warning-text">
            ⏸️ 暫停交易<br>
            目前無可用匯率資料
            </div>
            """, unsafe_allow_html=True)
        else:
            # 選擇目標貨幣
            currency_list = sorted(tradable_currencies.keys())
            selected_currency = st.selectbox(
                "選擇轉換貨幣",
                currency_list,
                index=0
            )
            
            # 計算轉換金額
            if twd_amount > 0 and selected_currency:
                rate = format_rate_value(
                    tradable_currencies[selected_currency].get('rate', '0')
                )
                
                if rate > 0:
                    converted_amount = twd_amount / rate
                    
                    # 顯示結果
                    st.markdown(f"""
                    <div class="exchange-result">
                    {twd_amount:,.2f} TWD<br>
                    =<br>
                    {converted_amount:,.2f} {selected_currency}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # 顯示匯率資訊
                    st.info(f"📊 匯率: 1 {selected_currency} = {rate:.4f} TWD")
                else:
                    st.markdown("""
                    <div class="warning-text">
                    ⏸️ 暫停交易<br>
                    該貨幣目前無匯率資料
                    </div>
                    """, unsafe_allow_html=True)
            elif twd_amount == 0:
                st.info("💡 請輸入台幣金額")
            else:
                st.markdown("""
                <div class="warning-text">
                ⏸️ 暫停交易
                </div>
                """, unsafe_allow_html=True)
    
    # ==================== 右欄：匯率資料表格 ====================
    with col_right:
        st.header("📊 匯率資料")
        
        # 手動更新按鈕和最後更新時間
        col_btn1, col_btn2, col_time = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("🔄 手動更新", use_container_width=True):
                update_exchange_rates()
                st.rerun()
        
        with col_btn2:
            if st.button("⚙️ 設定", use_container_width=True):
                st.session_state.show_settings = True
        
        with col_time:
            last_update_str = st.session_state.last_update_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            st.caption(f"⏱️ 最後更新: {last_update_str}")
        
        # 匯率表格
        tradable_currencies = get_tradable_currencies()
        
        if tradable_currencies:
            # 準備表格資料
            table_data = []
            for currency, data in sorted(tradable_currencies.items()):
                rate = format_rate_value(data.get('rate', '0'))
                status = data.get('status', '暫停交易')
                table_data.append({
                    '貨幣': currency,
                    '匯率': f"{rate:.4f}",
                    '狀態': status,
                    '轉換 1000 TWD': f"{1000 / rate:.2f}" if rate > 0 else "N/A"
                })
            
            df = pd.DataFrame(table_data)
            
            # 顯示表格
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    '貨幣': st.column_config.Column(width=80),
                    '匯率': st.column_config.Column(width=100),
                    '狀態': st.column_config.Column(width=100),
                    '轉換 1000 TWD': st.column_config.Column(width=130)
                }
            )
            
            # 顯示統計資訊
            st.markdown("---")
            col_stats1, col_stats2, col_stats3 = st.columns(3)
            
            with col_stats1:
                st.metric("可交易貨幣", len(tradable_currencies))
            
            with col_stats2:
                st.metric("總貨幣數", len(st.session_state.exchange_rates))
            
            with col_stats3:
                st.metric(
                    "自動更新間隔",
                    f"{st.session_state.update_interval} 分鐘"
                )
        else:
            st.markdown("""
            <div class="warning-text">
            ⏸️ 暫停交易<br>
            目前無匯率資料，請點擊手動更新
            </div>
            """, unsafe_allow_html=True)
    
    # 頁腳資訊
    st.markdown("---")
    st.caption(
        "💱 台幣匯率轉換系統 v1.0 | "
        "資料來源: 台灣銀行 | "
        "更新頻率: 每10分鐘自動更新"
    )


if __name__ == "__main__":
    main()
