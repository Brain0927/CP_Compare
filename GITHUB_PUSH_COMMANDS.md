# 🚀 GitHub 推送命令 - Brain0927

## ✨ 你的個性化部署指南

**GitHub 用戶名**: `Brain0927`  
**項目名稱**: `CP_Compare`  
**項目路徑**: `/home/brain/CP_Compare`

---

## 📋 執行步驟

### 第 1 步：建立 GitHub 倉庫 (2 分鐘)

訪問 **https://github.com/new** 並填寫：
- **Repository name**: `CP_Compare`
- **Description**: `AI 性價比比較器 - Momo、PChome 等平台`
- **Public**: ✅ 勾選（便於分享）
- 點擊 `Create repository`

---

### 第 2 步：執行推送命令 (1 分鐘)

**複製下方完整命令，直接粘貼到終端執行：**

```bash
cd /home/brain/CP_Compare && \
git remote add origin https://github.com/Brain0927/CP_Compare.git && \
git branch -M main && \
git push -u origin main
```

**或逐行執行：**

```bash
# 進入項目目錄
cd /home/brain/CP_Compare

# 添加 GitHub 遠程倉庫
git remote add origin https://github.com/Brain0927/CP_Compare.git

# 重命名分支為 main
git branch -M main

# 推送代碼到 GitHub
git push -u origin main
```

---

### 第 3 步：部署到 Streamlit Cloud (3 分鐘)

推送成功後 ✅，執行部署：

1. 訪問 **https://streamlit.io/cloud**
2. 用 GitHub 帳號登入（Brain0927）
3. 點擊 `New app`
4. 連接 GitHub 倉庫
5. 選擇：
   - **Repository**: `Brain0927/CP_Compare`
   - **Branch**: `main`
   - **Main file path**: `app.py`
6. 點擊 `Deploy`

---

### 第 4 步：設置 API Key (1 分鐘)

部署後，進入應用設置：

1. 點擊右上角 ⋮ → `Settings`
2. 左側 `Secrets` → 編輯 `secrets.toml`
3. 添加你的 Gemini API Key：

```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

4. 保存 → 應用自動重啟 ✨

---

## 📊 完成後的結果

**部署成功後，你的應用將在線上！** 🎉

| 項目 | 詳情 |
|------|------|
| **GitHub 倉庫** | https://github.com/Brain0927/CP_Compare |
| **應用 URL** | https://cp-compare-brain0927.streamlit.app |
| **應用狀態** | 實時在線 |
| **訪問權限** | 全球用戶可訪問 |

---

## 🔧 常見問題

### ❓ 推送時出現 "authentication failed"

**解決方案 1：使用 GitHub CLI**
```bash
gh auth login
# 按提示選擇 HTTPS，然後按回車
# 應用會提示你登入
```

**解決方案 2：使用 Personal Access Token**
```bash
# 到 https://github.com/settings/tokens 生成新 token
# 選擇 repo 和 admin:repo_hook 權限
git remote set-url origin https://YOUR_TOKEN@github.com/Brain0927/CP_Compare.git
```

---

### ❓ 推送後沒有看到文件

**檢查步驟：**
```bash
# 1. 驗證遠程倉庫配置
git remote -v
# 應該輸出：
# origin  https://github.com/Brain0927/CP_Compare.git (fetch)
# origin  https://github.com/Brain0927/CP_Compare.git (push)

# 2. 檢查分支
git branch -a
# 應該看到 main 分支

# 3. 查看最新提交
git log -1
```

---

### ❓ Streamlit 部署後無法訪問

**檢查清單：**
- ✅ API Key 已添加到 Secrets
- ✅ 倉庫是 Public 還是 Private？（如果 Private 需要給 Streamlit 授權）
- ✅ `app.py` 文件存在且可執行
- ✅ 所有依賴在 `requirements.txt` 中

**查看日誌：**
在 Streamlit Cloud 應用頁面右上角 → `Manage app` → `Logs`

---

## ✨ 成功標誌

當你看到這些時，部署完成了！ ✅

```
✅ GitHub 倉庫創建
✅ 本地代碼推送成功
✅ Streamlit 應用部署
✅ API Key 配置完成
✅ 應用在線可訪問
✅ 爬蟲功能正常運行
✅ AI 分析功能正常
```

---

## 🎯 下一步

部署完成後，你可以：

1. **分享應用** → 複製 URL 給朋友
2. **監控性能** → 在 Streamlit Cloud 檢查運行日誌
3. **持續改進** → 在本地修改代碼 → `git push` 自動更新
4. **收集反饋** → 在 GitHub Issues 收集用戶建議

---

## 📞 需要幫助？

- 🐛 Bug 報告：https://github.com/Brain0927/CP_Compare/issues
- 💬 討論：https://github.com/Brain0927/CP_Compare/discussions
- 📧 聯繫：GitHub 用戶名 Brain0927

---

**祝你部署順利！🚀**

時間戳：2025年12月16日  
準備狀態：✅ 完全準備好
