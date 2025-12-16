# ⚡ GitHub 部署快速指南 (5 分鐘完成)

## 🎯 3 步快速部署

### ✅ 步驟 1: 在 GitHub 建立倉庫 (1 分鐘)

1. 打開 https://github.com/new
2. 倉庫名稱：`CP_Compare`
3. 選擇 Public/Private
4. 點擊 "Create repository"

---

### ✅ 步驟 2: 上傳本地代碼到 GitHub (2 分鐘)

**複製下方命令執行：**

```bash
cd /home/brain/CP_Compare

# 1️⃣ 添加遠程倉庫 (替換 YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/CP_Compare.git

# 2️⃣ 重命名分支
git branch -M main

# 3️⃣ 推送代碼
git push -u origin main
```

**✅ 完成！代碼已上傳到 GitHub**

---

### ✅ 步驟 3: 部署應用 (選擇一個) (2 分鐘)

#### 選項 A：🎯 最簡單 - Streamlit Cloud (推薦)

1. 訪問 https://streamlit.io/cloud
2. 用 GitHub 帳號登入
3. 點擊 "New app"
4. 選擇倉庫：`CP_Compare`
5. 主文件：`app.py`
6. 點擊 "Deploy"

**🎉 完成！應用已上線**

訪問地址: `https://cp-compare-YOUR_USERNAME.streamlit.app`

---

#### 選項 B：🐳 Docker - 任何雲端平台

```bash
# 1️⃣ 構建 Docker 映像
docker build -t cp-compare .

# 2️⃣ 運行容器
docker run -e GEMINI_API_KEY="你的_API_KEY" \
  -p 8501:8501 \
  cp-compare

# 3️⃣ 訪問: http://localhost:8501
```

---

#### 選項 C：免費 - Heroku（即將停止免費層）

```bash
# 1️⃣ 安裝 Heroku CLI
npm install -g heroku

# 2️⃣ 登入
heroku login

# 3️⃣ 創建應用
heroku create cp-compare-YOUR_NAME

# 4️⃣ 設置 API Key
heroku config:set GEMINI_API_KEY="你的_API_KEY"

# 5️⃣ 推送部署
git push heroku main

# 6️⃣ 訪問
heroku open
```

---

#### 選項 D：AWS EC2 免費層

```bash
# 1️⃣ SSH 連接到實例
ssh -i your-key.pem ubuntu@your-instance-ip

# 2️⃣ 克隆倉庫
git clone https://github.com/YOUR_USERNAME/CP_Compare.git
cd CP_Compare

# 3️⃣ 安裝依賴
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4️⃣ 設置環境變數
export GEMINI_API_KEY="你的_API_KEY"

# 5️⃣ 運行應用
streamlit run --server.port 80 --server.address 0.0.0.0 app.py
```

---

## 🔑 環境變數設置

### Streamlit Cloud

1. 進入應用設置 → Secrets
2. 點擊 "Edit secrets"
3. 添加以下內容：

```toml
GEMINI_API_KEY = "你的_GEMINI_API_KEY"
```

### Docker / 本地運行

```bash
export GEMINI_API_KEY="你的_GEMINI_API_KEY"
```

---

## ✅ 測試清單

- [ ] GitHub 倉庫已建立
- [ ] 代碼已推送到 main 分支
- [ ] 選擇部署平台完成
- [ ] 環境變數已配置
- [ ] 應用正在線運行
- [ ] 訪問 URL 正常

---

## 🌍 訪問你的應用

| 平台 | URL 示例 |
|------|---------|
| **Streamlit Cloud** | `https://cp-compare-YOUR_USERNAME.streamlit.app/` |
| **Heroku** | `https://cp-compare-YOUR_NAME.herokuapp.com/` |
| **AWS EC2** | `http://your-instance-ip:80/` |
| **Docker** | `http://localhost:8501/` |

---

## 🐛 常見問題速查

### ❌ "fatal: 不是一個 git 版本庫"

```bash
cd /home/brain/CP_Compare
git init
```

### ❌ "Permission denied (publickey)"

使用 HTTPS 而非 SSH：
```bash
git remote set-url origin https://YOUR_USERNAME:YOUR_TOKEN@github.com/YOUR_USERNAME/CP_Compare.git
```

### ❌ 應用無法啟動

檢查依賴：
```bash
pip install -r requirements.txt
```

### ❌ API 配額錯誤

✅ 系統會自動使用本地分析，無需操作

---

## 📞 需要幫助？

- 查看完整指南：`GITHUB_DEPLOYMENT_GUIDE.md`
- GitHub 文檔：https://docs.github.com
- Streamlit 文檔：https://docs.streamlit.io
- Docker 文檔：https://docs.docker.com

---

## 🎉 恭喜！

你的 AI CP 值比較器已準備好部署！

**現在可以：**
- 🌐 與全世界分享你的應用
- 📊 收集用戶反饋並改進
- 🚀 持續更新和優化功能
- 💡 開源社區貢獻

**開始部署吧！** 🚀
