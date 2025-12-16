# 🚀 GitHub 部署指南

## 📋 部署步驟

### 1️⃣ 在 GitHub 上建立新倉庫

1. 登入 GitHub: https://github.com
2. 點擊右上角 `+` → `New repository`
3. 填寫倉庫信息：
   - **Repository name**: `CP_Compare` (或其他名稱)
   - **Description**: `AI 性價比比較器 - 自動爬蟲 + AI 智能分析`
   - **Public/Private**: 選擇公開或私有
   - 取消勾選 "Initialize with README" (我們已有)

4. 點擊 `Create repository`

---

### 2️⃣ 連接本地倉庫到 GitHub

在 `/home/brain/CP_Compare` 執行：

```bash
# 添加遠程倉庫
git remote add origin https://github.com/YOUR_USERNAME/CP_Compare.git

# 重命名分支為 main (GitHub 預設)
git branch -M main

# 推送到 GitHub
git push -u origin main
```

**替換 `YOUR_USERNAME` 為你的 GitHub 用戶名**

---

### 3️⃣ 設定 GitHub Token (推薦)

使用 Personal Access Token 代替密碼：

1. 登入 GitHub，進入 Settings
2. 左側選單 → Developer settings → Personal access tokens
3. 點擊 `Generate new token`
4. 勾選：`repo`, `admin:repo_hook`, `gist`
5. 生成 Token，複製保存

使用 Token：
```bash
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/CP_Compare.git
```

---

### 4️⃣ 部署到 Streamlit Cloud（免費部署）

#### 方式 A：Streamlit Cloud（推薦）

1. 訪問 https://streamlit.io/cloud
2. 用 GitHub 帳號登入
3. 點擊 `New app`
4. 選擇倉庫：`CP_Compare`
5. 選擇分支：`main`
6. 主文件路徑：`app.py`
7. 點擊 `Deploy`

**設置環境變數：**
- 進入應用設置 → Secrets
- 添加 `.streamlit/secrets.toml`：

```toml
GEMINI_API_KEY = "你的_API_KEY"
```

---

#### 方式 B：Heroku 部署

1. 安裝 Heroku CLI
2. 登入：`heroku login`
3. 創建應用：`heroku create cp-compare`
4. 設置環境變數：

```bash
heroku config:set GEMINI_API_KEY="你的_API_KEY"
```

5. 創建 `Procfile`：

```
web: streamlit run --server.port=$PORT --server.address=0.0.0.0 app.py
```

6. 推送：`git push heroku main`

---

### 5️⃣ 部署到 AWS/Azure/GCP

#### AWS EC2：

```bash
# 連接到實例
ssh -i your-key.pem ubuntu@your-instance-ip

# 安裝依賴
sudo apt update && sudo apt install python3-pip

# 克隆倉庫
git clone https://github.com/YOUR_USERNAME/CP_Compare.git
cd CP_Compare

# 設置虛擬環境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 設置環境變數
export GEMINI_API_KEY="你的_API_KEY"

# 運行 Streamlit
streamlit run --server.port 80 --server.address 0.0.0.0 app.py
```

#### Docker 部署（推薦）：

1. 創建 `Dockerfile`：

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV GEMINI_API_KEY=""
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--logger.level=error"]
```

2. 構建映像：
```bash
docker build -t cp-compare .
```

3. 運行容器：
```bash
docker run -e GEMINI_API_KEY="你的_API_KEY" -p 8501:8501 cp-compare
```

---

## 🔐 安全設置

### 環境變數管理

**❌ 不要提交 API Key！**

1. 在 `.env.example` 中示例：
```
GEMINI_API_KEY=your_api_key_here
```

2. 本地 `.env` 文件（不提交）
3. 在雲端平台設置環境變數

### GitHub Secrets（用於 CI/CD）

1. 倉庫設置 → Secrets and variables → Actions
2. 新增 Secret：`GEMINI_API_KEY`
3. 在 workflow 中使用：`${{ secrets.GEMINI_API_KEY }}`

---

## 📊 GitHub Actions CI/CD

創建 `.github/workflows/deploy.yml`：

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Streamlit
        env:
          STREAMLIT_CLOUD_TOKEN: ${{ secrets.STREAMLIT_CLOUD_TOKEN }}
        run: |
          echo "Deploying to Streamlit Cloud..."
          # 自動部署命令
```

---

## ✅ 驗證清單

- [ ] GitHub 倉庫已建立
- [ ] 本地倉庫已連接到 GitHub
- [ ] `git push` 成功上傳代碼
- [ ] `.gitignore` 已配置（不提交敏感信息）
- [ ] `.env.example` 已準備
- [ ] 選擇部署平台（Streamlit Cloud/Heroku/AWS 等）
- [ ] 環境變數已配置
- [ ] 應用在線訪問正常

---

## 🌐 部署後存取

### Streamlit Cloud
```
https://cp-compare-YOUR_USERNAME.streamlit.app/
```

### Heroku
```
https://cp-compare.herokuapp.com/
```

### AWS EC2
```
http://your-instance-ip:80/
```

---

## 🐛 常見問題

### 1. 推送被拒絕

```bash
# 更新遠程跟蹤
git fetch origin
git pull origin main

# 重新推送
git push -u origin main
```

### 2. 依賴安裝失敗

```bash
# 更新依賴
pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### 3. API 配額錯誤

系統會自動切換到本地分析模式，無需修改代碼

### 4. 部署後無法訪問

檢查防火牆規則，確保端口已開放：
- Streamlit Cloud: 自動配置
- Heroku: 自動配置
- AWS: 檢查安全組 (Security Group)

---

## 📚 資源連結

- GitHub: https://github.com
- Streamlit Cloud: https://streamlit.io/cloud
- Heroku: https://www.heroku.com
- AWS EC2: https://aws.amazon.com/ec2
- Docker: https://www.docker.com

---

## 🎯 下一步

1. **部署應用** - 選擇平台完成部署
2. **分享連結** - 與用戶分享應用 URL
3. **監控性能** - 檢查日誌和錯誤
4. **收集反饋** - 持續改進功能
5. **更新維護** - 定期推送更新

---

**修改日期：** 2025-12-16  
**版本：** 1.0
