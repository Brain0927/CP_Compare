# 🔐 環境配置指南

## ✅ 安全狀態

- ✅ `.env` 已被 `.gitignore` 保護，**未推送到 GitHub**
- ✅ `.env.example` 已作為模板上傳（安全示例）
- ✅ 本地 `.env` 文件包含真實 API Key（僅本地）

---

## 📋 三種環境配置方法

### 方法 1️⃣：Streamlit Cloud (推薦 ⭐)

**最簡單，無需在服務器上配置**

#### 步驟：

1. **進入應用管理**
   - https://streamlit.io/cloud
   - 點擊你的應用
   - 右上角 ⋮ → `Settings`

2. **配置 Secrets**
   - 左側菜單 → `Secrets`
   - 點擊 `Edit`

3. **添加 API Key**
   ```toml
   # .streamlit/secrets.toml (在 Streamlit Cloud 上)
   GEMINI_API_KEY = "AIzaSyC_YOUR_ACTUAL_KEY_HERE"
   ```

4. **保存**
   - 應用自動重啟 ✨

**完成！無需手動配置 .env**

---

### 方法 2️⃣：Docker 部署 (自主服務器)

**如果使用 Docker 或自己的服務器**

#### 建立本地 `.env` 文件：

```bash
cp .env.example .env
```

#### 編輯 `.env`：

```dotenv
GEMINI_API_KEY=your_actual_api_key_here
```

#### 運行 Docker：

```bash
# 構建映像
docker build -t cp-compare .

# 運行容器（自動讀取 .env）
docker run -p 8501:8501 --env-file .env cp-compare
```

#### 或使用 docker-compose：

```bash
# 創建 docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
EOF

# 運行
docker-compose up
```

---

### 方法 3️⃣：直接運行 Streamlit (本地開發)

```bash
# 確保 .env 存在且包含 API Key
cat .env
# 輸出: GEMINI_API_KEY=AIzaSy...

# 運行應用
streamlit run app.py
```

應用會自動讀取 `.env` 文件中的 `GEMINI_API_KEY`

---

## 🔒 安全最佳實踐

| 場景 | 做法 | ✅/❌ |
|------|------|-------|
| 本地開發 | 使用 `.env` 文件 | ✅ 安全 |
| 推送到 GitHub | `.env` 在 `.gitignore` 中 | ✅ 必須 |
| Streamlit Cloud | 使用 Secrets 管理 | ✅ 最安全 |
| Docker 部署 | 使用 `--env-file` | ✅ 安全 |
| 在代碼中硬編碼 API Key | 從不這樣做！ | ❌ 極危險 |

---

## 📝 .env 文件結構

```dotenv
# 你的本地 .env 文件示例
# ⚠️ 永遠不要推送這個文件到 GitHub！

# Gemini API
GEMINI_API_KEY=AIzaSyC_YOUR_ACTUAL_API_KEY_

# 可選：其他配置
DEBUG=False
TIMEOUT=30
```

---

## 🚀 部署前檢查清單

### ✅ 推送前（本地）

```bash
# 1. 確認 .env 未被推送
git ls-files | grep "\.env"
# 輸出應該只有 .env.example

# 2. 確認 .env 在 .gitignore
cat .gitignore | grep "\.env"

# 3. 本地 .env 包含真實 API Key
cat .env
# 應該輸出：GEMINI_API_KEY=AIzaSy...
```

### ✅ Streamlit Cloud 部署

```bash
# 1. 應用已部署到 Streamlit Cloud
# 2. GitHub 倉庫已授權
# 3. API Key 已在 Streamlit Secrets 中配置
# 4. 重啟應用，測試功能
```

### ✅ Docker 部署

```bash
# 1. 本地 .env 存在
ls -la .env

# 2. Docker 映像已構建
docker images | grep cp-compare

# 3. 容器運行時使用 --env-file
docker run --env-file .env ...

# 4. 應用成功啟動
curl http://localhost:8501
```

---

## 🆘 常見問題

### ❓ API Key 顯示在日誌中

**解決：** Streamlit 自動隱藏 Secrets 中的值。Docker 和本地開發中，確保不要用 `echo` 或 `print` 輸出 API Key。

### ❓ 推送後發現 .env 在 GitHub 上了

**緊急步驟：**

```bash
# 1. 立即撤銷 API Key（在 Google Cloud Console）
# 2. 生成新 API Key
# 3. 從 Git 歷史刪除舊文件
git filter-branch --tree-filter 'rm -f .env' -- --all
git push --force-with-lease

# 4. 更新本地和雲端部署的 API Key
```

### ❓ Streamlit 應用報錯 "GEMINI_API_KEY not found"

**解決：**

```bash
# 1. 檢查 Streamlit Secrets 是否已設置
#    應用設置 → Secrets → 應該看到 GEMINI_API_KEY

# 2. 檢查代碼是否正確讀取
#    config/settings.py 應該有：
#    API_KEY = os.getenv('GEMINI_API_KEY')
#    或
#    API_KEY = st.secrets.get('GEMINI_API_KEY')

# 3. 重啟應用
```

---

## 📚 三個環境的 API Key 來源

| 環境 | API Key 來源 | 位置 |
|------|-------------|------|
| **本地開發** | `.env` 文件 | `/home/brain/CP_Compare/.env` |
| **Streamlit Cloud** | Streamlit Secrets | 應用設置 → Secrets |
| **Docker 自主服務器** | `.env` 文件 + `--env-file` | 容器啟動參數 |

---

## ✨ 現在的狀態

✅ `.env` 已安全保護，未推送到 GitHub  
✅ `.env.example` 作為模板已上傳到 GitHub  
✅ 應用代碼可以讀取環境變數  
✅ 準備好在任何平台部署

---

**下一步：選擇部署平台並配置 API Key！** 🚀

時間戳：2025年12月16日
