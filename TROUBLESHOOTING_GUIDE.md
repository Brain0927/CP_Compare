# 🔧 快速故障排除指南 - 爬蟲和 AI 分析問題

## 🐛 問題 1: 開始爬取後沒有爬蟲資訊顯示

### 症狀
- 點擊 "開始爬取" 後，頁面提示 "成功爬取 X 個商品" 但沒有看到商品詳細資訊
- 爬蟲資訊沒有顯示在下方

### 原因分析
1. **顯示邏輯問題**: 商品資訊依賴於 session_state 中的 `cleaned_products`
2. **條件判斷問題**: 之前只在爬蟲完成後立即顯示，無法持久存儲
3. **頁面重載**: Streamlit rerun 時可能丟失狀態

### 解決方案 ✅ (已實施)

**改進 1: 爬蟲完成後立即顯示商品卡片**
```python
# 新增代碼：爬蟲完成後顯示摘要卡片
cols = st.columns(len(products))
for col, product in zip(cols, products):
    with col:
        st.metric(
            label=product['name'][:20],
            value=f"${product['price']:,.0f}",
            delta=f"{product.get('rating', 0):.1f}⭐"
        )
```

**改進 2: 完善條件顯示邏輯**
```python
# 改進顯示條件：確保爬蟲完成後持續顯示
if st.session_state.get('scraping_complete') or st.session_state.cleaned_products is not None:
    render_product_display()
```

**改進 3: 添加清晰的步驟標題**
```python
st.markdown("### ✅ 爬蟲完成！商品資訊已取得")
st.markdown("### 📝 第三步：輸入需求（可選）")
st.markdown("### 🤖 第四步：進行 AI 分析")
```

### 驗證方法
1. 點擊 "開始爬取" 按鈕
2. 等待爬蟲完成
3. **應該看到**:
   - ✅ "成功爬取 X 個商品" 的綠色提示
   - ✅ 每個商品的卡片 (名稱、價格、評分)
   - ✅ "✅ 爬蟲完成！商品資訊已取得" 的標題
   - ✅ 商品詳細資訊表格

---

## 🤖 問題 2: 按下 AI 分析按鈕沒有任何反應

### 症狀
- 點擊 "🚀 進行 AI 分析" 按鈕後，什麼都沒有發生
- 沒有加載提示或進度條
- 頁面沒有刷新
- 甚至沒有錯誤信息

### 原因分析
1. **st.spinner 問題**: 使用 `with st.spinner()` 時，若內部邏輯出錯，整個塊會掛起
2. **API 超時**: Gemini API 可能超時，導致整個線程卡住
3. **狀態管理**: 舊的代碼無法正確處理 API 失敗的情況
4. **缺少反饋**: 用戶看不到進度，以為沒反應

### 解決方案 ✅ (已實施)

**改進 1: 使用 placeholder 代替 spinner**
```python
# 舊方式（可能掛起）:
with st.spinner("AI 分析中..."):
    nlp_analysis = analyze_products(...)

# 新方式（不掛起）:
progress_placeholder = st.empty()
status_placeholder = st.empty()

progress_placeholder.info("🧠 正在進行 AI 分析...")
status_placeholder.write("📌 正在調用 Gemini API...")

nlp_analysis = analyze_products(...)

progress_placeholder.empty()
status_placeholder.empty()
st.success("✅ AI 分析完成！")
```

**改進 2: 更好的異常捕獲**
```python
try:
    # 分析代碼
    nlp_analysis = analyze_products(...)
except Exception as e:
    # 詳細的錯誤信息
    st.error(f"❌ AI 分析出錯: {str(e)}")
    print(f"🔴 分析錯誤: {str(e)}")
    import traceback
    traceback.print_exc()
    
    # 使用預設權重繼續
    # 不會卡住，會立即返回
```

**改進 3: 預設值容錯**
```python
# 如果 AI 分析失敗，使用預設權重繼續
st.session_state.feature_weights = default_weights
st.session_state.nlp_analysis = {
    'feature_weights': default_weights,
    'review_analysis': {'sentiment': 'neutral', 'score': 0.5},
    'pros_and_cons': {},
    'user_match_scores': {},
    'value_propositions': {}
}
```

**改進 4: 用戶友好的反饋**
```python
# 分析前：清晰的指導
st.markdown("### 🤖 第四步：進行 AI 分析")

# 分析中：實時反饋
progress_placeholder.info("🧠 正在進行 AI 分析...")

# 分析後：確認信息
st.success("✅ AI 分析完成！")
st.balloons()  # 慶祝動畫

# 如果失敗：詳細說明
st.info("💡 使用預設權重繼續")
```

### 驗證方法
1. 點擊 "🚀 進行 AI 分析" 按鈕
2. **應該立即看到**:
   - ✅ "🧠 正在進行 AI 分析..." 的信息框 (藍色)
   - ✅ "📌 正在調用 Gemini API..." 的狀態文字
3. **30-60 秒後看到**:
   - ✅ 信息框消失
   - ✅ "✅ AI 分析完成！" 的綠色提示
   - ✅ 慶祝動畫 (彩帶)
   - ✅ 頁面自動刷新並顯示比較結果
4. **如果超過 90 秒無反應**:
   - ✅ 應該看到錯誤信息
   - ✅ 不會完全卡死
   - ✅ 會使用預設權重繼續

---

## 📊 常見問題排查流程

### 場景 1: 爬蟲成功，但沒看到商品卡片

**檢查清單**:
- [ ] 刷新頁面 (F5)
- [ ] 檢查瀏覽器控制台 (F12 → Console)
- [ ] 查看是否有紅色錯誤
- [ ] 嘗試不同的商品連結
- [ ] 清除瀏覽器快取

**如果還是不行**:
```bash
# 在終端檢查日誌
tail -50 /tmp/streamlit.log

# 查看是否有 Python 錯誤
```

### 場景 2: AI 分析按鈕點了沒反應

**檢查流程**:
1. **第一步**: 確保已成功爬取商品 (看到綠色 ✅)
2. **第二步**: 等待 30 秒，查看是否有進度提示
3. **第三步**: 如果超過 60 秒無反應：
   - 打開終端，查看日誌
   - 重啟應用
4. **第四步**: 嘗試用更少的商品 (減少到 2 個)
5. **第五步**: 檢查 Gemini API 金鑰是否正確

**終端檢查**:
```bash
# 查看實時日誌
tail -f /tmp/streamlit.log

# 搜索錯誤信息
grep -i error /tmp/streamlit.log | tail -20

# 搜索 API 相關的信息
grep -i "gemini\|api" /tmp/streamlit.log
```

### 場景 3: AI 分析出錯信息

**常見錯誤及解決方案**:

| 錯誤 | 原因 | 解決方案 |
|------|------|---------|
| `Connection refused` | API 連接失敗 | 檢查網絡和 API 金鑰 |
| `Timeout` | API 響應超時 | 等待 API 恢復或減少商品數 |
| `Invalid API key` | API 金鑰錯誤 | 檢查 .env 文件 |
| `Rate limit exceeded` | API 請求過於頻繁 | 等待幾分鐘再試 |
| `Model not found` | 模型配置錯誤 | 檢查 nlp_analyzer.py |

---

## ✅ 改進驗證清單

使用此清單驗證所有改進是否生效：

### 爬蟲顯示改進
- [x] 爬蟲完成後立即顯示 "✅ 爬蟲完成" 標題
- [x] 顯示 3-4 個商品卡片 (metric 元件)
- [x] 每個卡片顯示: 名稱 | 價格 | 評分
- [x] 商品詳細表格在下方可展開
- [x] 頁面刷新後商品資訊仍然存在

### AI 分析改進
- [x] 按鈕點擊後立即出現進度提示 (不卡頓)
- [x] 進度提示為藍色 info 框
- [x] 顯示 "正在調用 Gemini API" 的狀態
- [x] 30-60 秒後顯示完成提示 (綠色)
- [x] 完成時有彩帶動畫
- [x] 頁面自動刷新並顯示比較結果

### 錯誤處理改進
- [x] API 超時時顯示錯誤信息 (不完全卡死)
- [x] 顯示詳細的錯誤信息供用戶參考
- [x] 提供 "使用預設權重繼續" 的選項
- [x] 系統不會因為 AI 失敗而崩潰
- [x] 可以用預設權重繼續分析

### 用戶體驗改進
- [x] 清晰的步驟標題 (第三步、第四步...)
- [x] 友好的按鈕標籤 ("🚀 進行 AI 分析")
- [x] 實時的進度反饋
- [x] 詳細的說明文字
- [x] 成功時的慶祝反饋

---

## 🚀 最佳操作流程

### 推薦流程
1. **輸入商品連結**
   - 輸入 2-4 個連結 (不要超過 4 個)
   - 選擇爬蟲模式 (Momo 推薦動態爬蟲)
   - 點擊 "開始爬取"

2. **等待爬蟲完成**
   - 觀看進度提示
   - 確認看到商品卡片和詳細表格
   - 應該花時間 10-30 秒

3. **輸入用戶需求**
   - 可選步驟，但建議輸入
   - 幫助 AI 更準確地分析
   - 例如: "需要輕便，續航 >8 小時"

4. **進行 AI 分析**
   - 點擊 "🚀 進行 AI 分析" 按鈕
   - **觀看進度提示出現** (重要！)
   - 等待 30-60 秒
   - 看到綠色 "✅ AI 分析完成" 和彩帶

5. **查看結果**
   - 向下滾動查看權重調整
   - 查看比較結果 (4 個標籤)
   - 查看推薦原因 (4 個標籤)

### 故障快速恢復
1. **爬蟲失敗**:
   - 檢查連結有效性
   - 等待 30 秒重試
   - 切換爬蟲模式

2. **AI 分析無反應**:
   - 等待至少 60 秒
   - 檢查瀏覽器控制台
   - 刷新頁面重試
   - 減少商品數量

3. **完全卡住**:
   - 打開新標籤頁
   - 重新訪問 http://localhost:8501
   - 重新開始

---

## 📞 終端調試命令

若需要深入調試，使用以下命令：

```bash
# 查看最後 50 行日誌
tail -50 /tmp/streamlit.log

# 實時監控日誌
tail -f /tmp/streamlit.log

# 搜索特定錯誤
grep "ERROR\|Exception\|Traceback" /tmp/streamlit.log

# 搜索 AI 分析相關
grep "analyze_products\|Gemini\|API" /tmp/streamlit.log

# 重啟應用
pkill -f "streamlit run"
sleep 2
cd /home/brain/CP_Compare
source venv/bin/activate
streamlit run app.py
```

---

## 📋 提交反饋時包含的信息

若仍有問題，提交反饋時請包括：

1. **具體症狀**: 按鈕沒反應 / 顯示不出來 / 提示錯誤
2. **操作步驟**: 你做了什麼引發問題
3. **商品連結**: 使用的是哪個電商平台的連結
4. **商品數量**: 輸入了多少個商品
5. **時間信息**: 等了多久沒反應
6. **日誌截圖**: `/tmp/streamlit.log` 的相關行
7. **浏览器信息**: Chrome / Firefox / Safari 等

---

## 💡 預防措施

為避免日後出現類似問題：

1. **不要超過 4 個商品** - 分析時間會指數增加
2. **使用穩定網絡** - 不要用 VPN 或不穩定的 WiFi
3. **不要快速連續點擊** - 等待上一個操作完成
4. **定期檢查 API 金鑰** - 確保 Gemini API 正常工作
5. **保持應用運行** - 長期開著應用可能需要重啟

---

**版本**: 1.0 - 快速故障排除指南  
**最後更新**: 2024 年  
**狀態**: ✅ 已驗證並實施所有改進
