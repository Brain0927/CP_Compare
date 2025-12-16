#!/bin/bash
# 快速啟動腳本

echo "🚀 啟動 AI CP 值比較器..."

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo "📦 建立虛擬環境..."
    python3 -m venv venv
fi

# 啟動虛擬環境
source venv/bin/activate

# 安裝依賴
echo "📥 安裝依賴套件..."
pip install -r requirements.txt

# 檢查 .env 文件
if [ ! -f ".env" ]; then
    echo "⚠️  未發現 .env 檔案，正在建立..."
    cp .env.example .env
    echo "❌ 請在 .env 檔案中填入 GEMINI_API_KEY"
fi

# 啟動 Streamlit
echo "🎯 啟動 Streamlit..."
streamlit run app.py
