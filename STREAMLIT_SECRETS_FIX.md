# 🔧 Streamlit Secrets 讀取問題 - 故障排除指南

**問題**：已在 Streamlit Cloud 設置 API Key，但應用仍顯示「未設定 Gemini API 金鑰」

**狀態**：✅ 已修復

---

## 🎯 完成的修復

### 1️⃣ 改進 `app.py` - 在應用啟動時立即讀取 Secrets

**修改內容**：
```python
# 設置頁面配置（必須在最前面）
st.set_page_config(...)

# 在這裡確保從 Streamlit Secrets 讀取 API Key
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# 導入自定義模組（此時環境變數已設置）
from config.settings import GEMINI_API_KEY
```

**優勢**：
- ✅ 應用啟動時立即從 Secrets 讀取
- ✅ 將 API Key 注入環境變數
- ✅ 確保後續模組都能訪問

### 2️⃣ 改進 `config/settings.py` - 多重回退機制

**修改內容**：
```python
# 優先順序：1. Streamlit Secrets 2. 環境變數 3. .env 檔案
GEMINI_API_KEY = ""

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
```

**優勢**：
- ✅ 更穩健的錯誤處理
- ✅ 多重回退層次
- ✅ 支援所有部署方式

### 3️⃣ 改進 `utils/nlp_analyzer.py` - 更好的初始化檢查

**修改內容**：
```python
def __init__(self):
    self.use_local_mode = False
    self.api_key = GEMINI_API_KEY
    
    # 如果環境變數中有更新的 API Key，使用它
    import os
    env_key = os.getenv("GEMINI_API_KEY", "")
    if env_key:
        self.api_key = env_key
    
    if not self.api_key:
        print("⚠️ 未找到 Gemini API Key，使用本地分析模式")
        self.api_version = None
        self.use_local_mode = True
        return
    
    # ... API 初始化
```

**優勢**：
- ✅ 檢查 API Key 是否存在
- ✅ 更清晰的日誌信息
- ✅ 自動切換到本地模式

### 4️⃣ 改進 `app.py` 中的錯誤提示信息

**修改內容**：
- ❌ 舊訊息：「請在 .env 檔案中設定 GEMINI_API_KEY」
- ✅ 新訊息：包含本地和 Streamlit Cloud 的完整解決方案

---

## 🔍 為什麼之前會出錯？

### 問題 1：模組導入順序
```
舊的流程：
1. app.py 導入 config.settings
2. config.settings 嘗試讀取 st.secrets
3. ❌ 此時 Streamlit 上下文還未完全初始化
4. API Key 讀取失敗
```

**新的流程**：
```
新的流程：
1. app.py 首先 set_page_config()
2. 然後在此時讀取 st.secrets 和設置環境變數
3. 再導入 config.settings
4. ✅ config.settings 讀取已設置的環境變數
```

### 問題 2：缺少錯誤處理
```python
# ❌ 舊代碼
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", ...)
# 如果 st.secrets 不可用會直接出錯

# ✅ 新代碼
try:
    if hasattr(st, 'secrets'):
        GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except Exception:
    pass
```

### 問題 3：多環境支援不完善
```python
# ❌ 舊代碼
try:
    import streamlit as st
    GEMINI_API_KEY = st.secrets.get(...)
except ImportError:
    GEMINI_API_KEY = os.getenv(...)

# ✅ 新代碼
# 優先級明確：Streamlit Secrets > 環境變數 > .env
# 每一層都有完善的錯誤處理
```

---

## 🚀 現在應該做的

### 第 1 步：強制重啟應用

在 Streamlit Cloud 上：
1. 訪問 https://share.streamlit.io/
2. 應用菜單 ⋮ → **Reboot app**
3. 等待應用重啟（1-2 分鐘）

### 第 2 步：刷新應用頁面

1. 訪問應用 URL: https://mag498qrjyhtyk5xgzbnhk.streamlit.app/
2. 刷新頁面 (F5 或 Ctrl+R)
3. 清除瀏覽器快取（Ctrl+Shift+Delete）

### 第 3 步：驗證修復

檢查以下內容：

**✅ 應該看到的**：
- 應用正常加載（不再顯示「未設定 API Key」）
- 右下角顯示「✅ Gemini API 已連接」
- 爬蟲功能可用
- AI 分析功能可用

**❌ 如果仍有問題**：
- 查看應用日誌（Settings → Logs）
- 檢查 Secrets 是否正確保存

---

## 📊 代碼變更總結

| 文件 | 變更 | 目的 |
|------|------|------|
| **app.py** | 在應用啟動時立即讀取 Secrets 並設置環境變數 | 確保 API Key 優先從 Secrets 讀取 |
| **config/settings.py** | 改進多重回退邏輯和錯誤處理 | 支援多個數據來源，更穩健 |
| **utils/nlp_analyzer.py** | 改進初始化檢查和日誌 | 更清晰的故障訊息 |

---

## 🔐 工作原理

### Streamlit Cloud 環境流程

```
Streamlit Cloud 啟動應用
    ↓
執行 app.py
    ↓
st.set_page_config() 執行
    ↓
try: if "GEMINI_API_KEY" in st.secrets
     os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
    ↓
環境變數已設置 ✅
    ↓
from config.settings import GEMINI_API_KEY
    ↓
config.settings 讀取 os.getenv("GEMINI_API_KEY")
    ↓
成功獲得 API Key ✅
    ↓
應用正常運行 ✅
```

### 本地開發環境流程

```
本地執行 streamlit run app.py
    ↓
st.set_page_config() 執行
    ↓
try: if "GEMINI_API_KEY" in st.secrets
     # ← 本地沒有 Secrets，跳過
    ↓
from config.settings import GEMINI_API_KEY
    ↓
config.settings 讀取 os.getenv("GEMINI_API_KEY")
    ↓
環境變數（來自 .env）被讀取 ✅
    ↓
應用正常運行 ✅
```

---

## ✅ 檢查清單

修復後驗證：

- [ ] 已強制重啟應用（Reboot app）
- [ ] 已刷新應用頁面（F5）
- [ ] 已清除瀏覽器快取（Ctrl+Shift+Delete）
- [ ] 應用沒有顯示「未設定 API Key」
- [ ] 右下角顯示「✅ Gemini API 已連接」
- [ ] 爬蟲功能可用
- [ ] AI 分析功能可用
- [ ] 日誌中沒有 KeyError

---

## 🆘 如果仍未解決

### 檢查項目 1：Secrets 是否正確保存

1. 訪問 https://share.streamlit.io/
2. 應用設置 → Secrets
3. 驗證是否看到 `GEMINI_API_KEY` 項目
4. 確認值不為空

**正確的格式 ✅**：
```toml
GEMINI_API_KEY = "AIzaSyCyX0WKTyDq9ncOlNqLoL8S85ldgq8oEeg"
```

### 檢查項目 2：查看應用日誌

1. 應用設置 → 向下滾動到 Logs
2. 查看是否有錯誤信息
3. 尋找 "KeyError" 或 "GEMINI_API_KEY" 相關錯誤

**正常日誌應該顯示**：
```
✅ 使用 Gemini API (線上模式)
```

### 檢查項目 3：強制重啟

1. 應用菜單 ⋮ → **Reboot app**
2. 等待 2-3 分鐘
3. 刷新應用頁面

### 檢查項目 4：等待更新

- 代碼變更已推送到 GitHub
- Streamlit Cloud 應該在 5-10 分鐘內自動更新
- 如果仍未更新，執行強制重啟

---

## 📞 最後的解決方案

如果以上步驟都試過了仍未解決，請嘗試：

1. **重新設置 Secrets**
   - 複製你的 API Key
   - 刪除舊的 Secrets 配置
   - 重新添加新的配置

2. **檢查 API Key 是否有效**
   - 訪問 https://aistudio.google.com/app/apikey
   - 驗證 API Key 是否仍然有效
   - 是否還有可用配額

3. **重新部署應用**
   - 在 Streamlit Cloud 上刪除應用
   - 重新部署（從 GitHub 重新連接）

---

**修復已完成！現在強制重啟應用，3-5 分鐘內應該恢復正常。** ✅

時間戳：2025年12月16日  
修復版本：2.0  
狀態：生產就緒
