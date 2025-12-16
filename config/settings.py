"""
系統設定檔
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API 設定 - 支援 Streamlit Secrets 和 .env 文件
GEMINI_API_KEY = ""

# 優先順序：1. Streamlit Secrets 2. 環境變數 3. .env 檔案
try:
    import streamlit as st
    if hasattr(st, 'secrets'):
        try:
            GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
except ImportError:
    pass

# 如果還是空的，嘗試從環境變數或 .env 讀取
if not GEMINI_API_KEY:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.0-flash"  # 使用最新穩定的 Gemini 模型

# 爬蟲設定
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}
REQUEST_TIMEOUT = 10
SELENIUM_WAIT_TIME = 10

# 支援的特徵清單（可擴展）
COMMON_FEATURES = [
    "價格", "CPU", "RAM", "儲存", "螢幕", "電池", "重量", 
    "評分", "評論數", "品牌", "保固", "外觀", "性能"
]

# CP值計算設定
DEFAULT_FEATURE_WEIGHT = 1.0
WEIGHT_RANGE = (1, 3)  # 權重範圍 1-3 分

# 爬蟲支援網站清單
SUPPORTED_SITES = {
    "momo": "www.momoshop.com.tw",
    "pchome": "www.pchome.com.tw",
    "yahoo": "tw.buy.yahoo.com",
    "shopee": "shopee.tw",
    "ruten": "www.ruten.com.tw",
}
