# 🚀 Streamlit Cloud 應用配置指南

**應用 URL**: https://mag498qrjyhtyk5xgzbnhk.streamlit.app/

---

## ⚠️ 問題診斷

你的應用無法使用 API 的原因：

```
❌ .env 文件未上傳到 GitHub
❌ Streamlit Cloud 上未配置 API Key
❌ 應用無法讀取 GEMINI_API_KEY 環境變數
```

---

## ✅ 快速解決方案（2 分鐘）

### 步驟 1：訪問應用設置

1. 打開應用管理頁面：
   ```
   https://share.streamlit.io/
   ```

2. 找到你的應用 `CP_Compare`（或直接訪問應用 URL）

3. 點擊右上角菜單 ⋮ → `Settings`

### 步驟 2：進入 Secrets 管理

1. 左側菜單 → `Secrets`
2. 點擊 `Edit in Streamlit Cloud`

### 步驟 3：添加 API Key

在編輯框中粘貼你的 Gemini API Key：

```toml
# .streamlit/secrets.toml

GEMINI_API_KEY = "AIzaSyCyX0WKTyDq9ncOlNqLoL8S85ldgq8oEeg"
```

**將上面的 Key 替換為你的實際 API Key**

### 步驟 4：保存並重啟

1. 點擊 `Save`
2. 應用自動重啟（約 10 秒）
3. 刷新應用 → API 功能恢復 ✨

---

## 🔍 如何取得你的 Gemini API Key

如果你還沒有 API Key：

1. 訪問 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 點擊 `Create API Key`
3. 複製生成的 Key
4. 在上面的 Secrets 中粘貼

---

## 📝 正確的 Secrets 格式

**正確 ✅**：
```toml
GEMINI_API_KEY = "AIzaSy..."
```

**錯誤 ❌**：
```
GEMINI_API_KEY=AIzaSy...     # 缺少空格和引號
GEMINI_API_KEY: "AIzaSy..."  # 冒號語法錯誤
API_KEY = "AIzaSy..."        # 變數名錯誤
```

---

## 🧪 驗證 API 連接

設置完成後，應用會自動重啟。檢查以下方式驗證：

### 方法 1：直接使用應用

1. 訪問 https://mag498qrjyhtyk5xgzbnhk.streamlit.app/
2. 輸入產品 URL 或搜索查詢
3. 點擊分析按鈕
4. 檢查是否有 AI 分析結果

### 方法 2：查看應用日誌

1. 應用管理 → 你的應用
2. 右上角 ⋮ → `Settings`
3. 下方 `Logs` 部分
4. 查看是否有錯誤信息

**成功日誌示例**：
```
2025-12-16 10:30:45 streamlit run app.py
2025-12-16 10:30:48 Loading settings...
2025-12-16 10:30:50 Initializing NLP analyzer...
2025-12-16 10:30:52 Ready for requests
```

**錯誤日誌示例**：
```
KeyError: 'GEMINI_API_KEY'  ← 需要配置 Secrets
```

---

## 🔄 如果應用仍無法工作

### 檢查清單

1. **Secrets 是否保存？**
   ```bash
   # 應用管理 → Settings → Secrets
   # 應該看到 "GEMINI_API_KEY" 字段
   ```

2. **API Key 是否有效？**
   - 訪問 Google AI Studio 檢查
   - 或嘗試在本地運行測試

3. **應用是否已重啟？**
   - 等待 30 秒
   - 刷新瀏覽器
   - 清除快取 (Ctrl+Shift+Delete)

4. **代碼是否正確讀取？**
   - 檢查 `config/settings.py` 中是否有：
   ```python
   import streamlit as st
   
   GEMINI_API_KEY = st.secrets.get('GEMINI_API_KEY', '')
   ```

### 強制重啟應用

如果上述方法都不行：

1. 應用設置 → `Reboot app`
2. 或停止應用 → 等待 5 分鐘 → 訪問應用自動重啟

---

## 📊 三種環境的 API Key 來源

| 環境 | API Key 來源 | 位置 |
|------|-------------|------|
| **Streamlit Cloud ⭐** | Secrets 管理 | 應用設置 → Secrets |
| **本地開發** | `.env` 文件 | `/home/brain/CP_Compare/.env` |
| **Docker 服務器** | 環境變數 | `docker run -e GEMINI_API_KEY=...` |

---

## 🎯 Streamlit Secrets 的優勢

✅ **安全性高** - API Key 加密存儲  
✅ **方便管理** - 無需上傳 `.env` 文件  
✅ **動態更新** - 修改 Secrets 無需重新推送代碼  
✅ **多環境支援** - 開發、測試、生產可用不同 Key  

---

## 💡 最佳實踐

### 開發階段
```bash
# 本地使用 .env（在 .gitignore 中）
streamlit run app.py
```

### 生產部署
```
# Streamlit Cloud 使用 Secrets（不需要上傳敏感信息）
# GitHub 只上傳 .env.example（安全示例）
```

### 安全原則
```
✅ API Key 只在 Secrets 中存儲
❌ 永遠不要在 GitHub 上提交 .env
❌ 不要在代碼中硬編碼 API Key
```

---

## 🚀 現在就配置

**完整步驟（5 分鐘）：**

1. ⏱️ 1 分鐘 - 訪問 https://share.streamlit.io/
2. ⏱️ 1 分鐘 - 找到應用 → Settings → Secrets
3. ⏱️ 1 分鐘 - 粘貼 API Key 配置
4. ⏱️ 2 分鐘 - 等待應用重啟 → 刷新應用

**完成後 ✨**：
- 應用恢復功能
- API 分析正常工作
- 用戶可以爬蟲和分析產品

---

## 📞 如果還是不工作

**常見原因和解決方案：**

| 症狀 | 原因 | 解決方案 |
|------|------|--------|
| "GEMINI_API_KEY 未找到" | Secrets 未配置 | 進入 Settings → Secrets 配置 |
| "API 配額已用盡" (429 錯誤) | 免費額度用完 | 使用本地分析備用系統 |
| 應用崩潰 | 代碼錯誤 | 檢查日誌，查看錯誤詳情 |
| 應用卡住 | 超時或內存 | 強制重啟應用 |

---

**配置完成後，你的應用就能正常工作了！** 🎉

時間戳：2025年12月16日
