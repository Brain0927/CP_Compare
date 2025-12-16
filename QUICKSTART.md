# 項目配置 - 快速參考

## 文件結構

```
CP_Compare/
├── app.py                      # 🎯 Streamlit 主應用
├── test.py                     # 🧪 測試腳本
├── run.sh                      # ⚡ 快速啟動腳本
├── requirements.txt            # 📦 Python 依賴
├── .env.example               # 🔐 環境變數示例
├── .gitignore                 # 🚫 Git 忽略配置
├── README.md                  # 📖 專案文檔
├── GUIDE.md                   # 📚 使用指南
├── QUICKSTART.md              # 📋 本檔案
│
├── config/
│   ├── __init__.py
│   └── settings.py            # ⚙️  系統設定
│
├── utils/
│   ├── __init__.py
│   ├── scraper.py             # 🕷️  爬蟲模組
│   ├── data_cleaner.py        # 🧹 資料清洗
│   ├── nlp_analyzer.py        # 🧠 NLP 分析
│   └── cp_calculator.py       # 📊 CP值計算
│
├── src/
│   └── __init__.py            # 擴展源代碼
│
└── data/
    └── sample_products.py     # 📦 樣本資料
```

## 🚀 快速開始（3步）

### 1. 環境設置
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. 配置 API
```bash
cp .env.example .env
# 編輯 .env，填入 GEMINI_API_KEY
```

### 3. 啟動應用
```bash
streamlit run app.py
```

## 📋 功能清單

- ✅ BeautifulSoup + Selenium 爬蟲
- ✅ 自動資料清洗與標準化
- ✅ Gemini API 語意分析
- ✅ CP 值科學計算
- ✅ Streamlit 互動介面
- ✅ Matplotlib 視覺化
- ✅ 多商品對比
- ✅ AI 推薦理由

## 🔑 API 金鑰獲取

1. 訪問: https://makersuite.google.com/app/apikey
2. 點擊「Create API Key」
3. 複製金鑰到 `.env` 中
4. 保存並重啟應用

## 📊 CP 值公式

```
CP = Σ(Feature × Weight) / Price × (1 + Rating/5 × 0.2)
```

## 🆘 常見問題速解

| 問題 | 解決方案 |
|------|---------|
| API 錯誤 | 檢查 .env 中的 API 金鑰 |
| 爬蟲失敗 | 試試勾選「動態載入」 |
| 導入錯誤 | 執行 `python test.py` 診斷 |
| Streamlit 無法啟動 | 確認虛擬環境已激活 |

## 📚 詳細文檔

- 📖 **README.md** - 專案概述
- 📚 **GUIDE.md** - 完整使用指南
- 📋 **本檔案** - 快速參考

## 🎯 使用場景

- 💻 筆記型電腦對比
- 📱 智能手機對比
- 🎧 耳機對比
- 📷 相機對比
- 其他電子產品

## 📞 技術棧

| 層級 | 技術 |
|------|------|
| UI | Streamlit |
| 爬蟲 | BeautifulSoup, Selenium |
| NLP | Google Gemini API |
| 資料 | Pandas |
| 視覺化 | Matplotlib |
| 環境 | Python 3.8+ |

## ✅ 檢查清單

開始前請確認：

- [ ] Python 3.8+ 已安裝
- [ ] pip 可用
- [ ] 網路連線正常
- [ ] Gemini API 金鑰已申請
- [ ] 虛擬環境已建立
- [ ] 依賴已安裝

## 🎓 學習資源

- Streamlit 文檔: https://docs.streamlit.io
- BeautifulSoup 文檔: https://www.crummy.com/software/BeautifulSoup/
- Selenium 文檔: https://www.selenium.dev/documentation/
- Gemini API: https://ai.google.dev/

## 📝 下一步

1. ✅ 完成安裝
2. ✅ 執行 `test.py` 驗證
3. ✅ 啟動 `app.py`
4. ✅ 用樣本商品測試
5. ✅ 用實際商品對比

---

**準備好了？執行 `streamlit run app.py` 開始吧！** 🚀
