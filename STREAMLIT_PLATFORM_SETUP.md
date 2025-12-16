# 🔧 Streamlit Cloud 平台設置完整指南

**應用 URL**: https://mag498qrjyhtyk5xgzbnhk.streamlit.app/

---

## 📋 問題說明

**程式碼需要讀 .env 文件**，但在 Streamlit Cloud 上：
- ❌ 無法上傳 .env 文件（為了安全）
- ❌ 應用無法訪問本地 .env
- ✅ 需要使用 Streamlit Secrets 替代

---

## 🔑 Streamlit Cloud 設置步驟

### 步驟 1：訪問應用管理頁面

打開瀏覽器訪問：
```
https://share.streamlit.io/
```

你應該看到你的應用列表。

---

### 步驟 2：找到你的應用

尋找應用名稱：`CP_Compare` 或 `Brain0927/CP_Compare`

點擊應用卡片進入應用管理頁面。

---

### 步驟 3：進入應用設置

在應用頁面的右上角，找到 **⋮** (三點菜單)，點擊它。

選擇菜單中的選項：
- 如果看到 **"Edit secrets"** → 點擊它
- 或者進入 **Settings** → 左側 **Secrets** → 點擊編輯

---

### 步驟 4：添加 TOML 格式的 Secrets

在編輯器中粘貼以下內容：

```toml
GEMINI_API_KEY = "AIzaSyCyX0WKTyDq9ncOlNqLoL8S85ldgq8oEeg"
```

**✅ 重要注意**：
- 必須使用 TOML 格式（不是 .env 格式）
- TOML 格式必須有引號和等號：`KEY = "value"`
- 不能是 .env 格式：`KEY=value`（這樣會出錯）

**格式對比**：
```
❌ 錯誤 (.env 格式)
GEMINI_API_KEY=AIzaSyCyX0WKTyDq9ncOlNqLoL8S85ldgq8oEeg

✅ 正確 (TOML 格式)
GEMINI_API_KEY = "AIzaSyCyX0WKTyDq9ncOlNqLoL8S85ldgq8oEeg"
```

---

### 步驟 5：保存配置

1. 查找編輯框下方的按鈕
2. 點擊 **Save** 或 **Done** 按鈕
3. 你應該看到確認信息：
   ```
   Your secrets have been saved
   ```
   或
   ```
   Secrets saved successfully
   ```

---

### 步驟 6：等待應用重啟

- Streamlit Cloud 會自動重啟你的應用
- 等待時間：10-30 秒
- 你會看到應用重新加載

---

### 步驟 7：驗證成功

應用重啟後：

1. **刷新應用頁面** (F5 或 Ctrl+R)

2. **檢查右下角信息**
   - 應該顯示：**✅ Gemini API 已連接**
   - 或類似的成功信息

3. **測試功能**
   - 嘗試爬蟲功能
   - 輸入產品 URL 或搜索查詢
   - 檢查是否有 AI 分析結果

4. **查看日誌**（可選）
   - 應用菜單 → Logs
   - 應該看不到 "KeyError" 或 "GEMINI_API_KEY" 的錯誤

---

## 📱 如何在不同平台訪問設置

### 電腦版本

1. 訪問 https://share.streamlit.io/
2. 在應用卡片上找到 ⋮ 菜單
3. 或直接訪問應用，在應用頁面右上角找菜單

### 手機版本

1. 訪問 https://share.streamlit.io/
2. 可能需要點擊應用名稱進入應用頁面
3. 在頁面右上角找 ⋮ 菜單或 Settings

---

## 🔑 完整的 TOML Secrets 配置範例

如果需要添加更多配置，完整的文件應該是：

```toml
# Gemini API 配置
GEMINI_API_KEY = "AIzaSyCyX0WKTyDq9ncOlNqLoL8S85ldgq8oEeg"

# 可選：其他配置
# DEBUG = false
# REQUEST_TIMEOUT = 10
# SELENIUM_WAIT_TIME = 10
```

**注意**：
- 每行一個配置
- 格式必須是 `KEY = "value"`
- 字符串值必須用雙引號包圍
- 數字可以不用引號：`TIMEOUT = 30`

---

## 🆘 如果出錯了？

### 錯誤 1：TOML 格式錯誤

**症狀**：
```
Error: Invalid TOML format
```

**解決**：
- 檢查是否使用了 .env 格式（`KEY=value`）
- 改為 TOML 格式：`KEY = "value"`
- 檢查引號是否正確（需要雙引號）

### 錯誤 2：KeyError: 'GEMINI_API_KEY'

**症狀**：
```
KeyError: 'GEMINI_API_KEY'
```

**解決**：
- Secrets 未正確保存
- 重新進入 Settings → Secrets
- 確認配置已保存（應該看到「Secrets saved」提示）
- 強制重啟應用

### 錯誤 3：應用卡住或無法重啟

**症狀**：
- 應用頁面一直顯示「Launching...」
- 或應用無響應

**解決**：
1. 等待 5 分鐘
2. 在應用菜單中找 **Reboot app** 或 **Restart**
3. 或訪問 https://share.streamlit.io/ → 重新點擊應用

---

## 📝 程式碼如何讀取 Secrets？

**你的代碼已經支援！** (`config/settings.py`)

```python
try:
    import streamlit as st
    # Streamlit Cloud 環境 → 讀取 Secrets
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY", ""))
except (ImportError, AttributeError):
    # 本地開發環境 → 讀取 .env
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
```

**工作流程**：
1. ✅ Streamlit Cloud 環境 → 自動讀取 Secrets 中的 `GEMINI_API_KEY`
2. ✅ 本地開發環境 → 讀取 `.env` 文件中的 `GEMINI_API_KEY`
3. ✅ 其他環境 → 讀取系統環境變數中的 `GEMINI_API_KEY`

---

## 🎯 完整的工作流程

```
┌─────────────────────────────────────────────────────────┐
│ 1. 本地開發 (你的電腦)                                 │
├─────────────────────────────────────────────────────────┤
│ 程式碼讀取 .env 文件                                   │
│ .env 包含：GEMINI_API_KEY=AIzaSy...                   │
│ .env 被 .gitignore 保護，不推送到 GitHub              │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 推送到 GitHub                                       │
├─────────────────────────────────────────────────────────┤
│ 只推送 .env.example（安全示例）                        │
│ 不推送 .env（保護真實 API Key）                        │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Streamlit Cloud 部署                                │
├─────────────────────────────────────────────────────────┤
│ 從 GitHub 克隆代碼（無 .env 文件）                     │
│ 在 Secrets 中手動配置 API Key                          │
│ 程式碼自動讀取 st.secrets.get("GEMINI_API_KEY")       │
│ 應用正常運行                                           │
└─────────────────────────────────────────────────────────┘
```

---

## ✅ 檢查清單

配置前檢查：
- [ ] 訪問 https://share.streamlit.io/ 能訪問
- [ ] 看到你的應用列表
- [ ] 能進入應用管理頁面

配置中檢查：
- [ ] 找到 Settings 或 Edit secrets 選項
- [ ] 看到 TOML 格式的編輯器
- [ ] 粘貼了正確的 TOML 配置

配置後檢查：
- [ ] 看到「Secrets saved」確認信息
- [ ] 應用重啟完成（等待 10-30 秒）
- [ ] 應用右下角顯示「✅ Gemini API 已連接」
- [ ] 功能測試成功

---

## 📞 快速參考

| 場景 | 做法 |
|------|------|
| **本地開發** | 使用 `.env` 文件 |
| **Streamlit Cloud** | 使用 Secrets (TOML 格式) |
| **Docker 部署** | 使用 `docker run -e GEMINI_API_KEY=...` |
| **其他服務器** | 使用環境變數或 `.env` |

---

## 🎉 預期結果

配置完成後，你的應用將能夠：

```
✨ 自動讀取 Streamlit Secrets
✨ 連接 Gemini API
✨ 進行產品爬蟲和 AI 分析
✨ 生成 CP 值報告
✨ 在 https://mag498qrjyhtyk5xgzbnhk.streamlit.app/ 正常運行
```

---

**現在就按照上面的步驟配置吧！** 🚀

時間戳：2025年12月16日  
難度等級：⭐ 簡單（只需複製粘貼）  
預計耗時：3 分鐘
