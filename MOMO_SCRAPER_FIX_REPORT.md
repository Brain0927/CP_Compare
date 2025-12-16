# Momo 爬蟲修復報告

## 概述
本報告記錄了對 Momo 商品價格提取邏輯的改進嘗試。用戶要求優先提取促銷價（促銷價）而非市售價。

## 問題分析

### 用戶需求
- Momo 顯示兩種價格：市售價（市售價）和促銷價（促銷價）
- 應該優先使用促銷價，否則使用市售價
- 如果錯誤的價格會導致 CP 值計算不正確

### 發現的 HTML 結構
根據之前的 HTML 分析，確認了正確的選擇器：
```html
<!-- 促銷價（紅色顯示） -->
<span class="seoPrice">9,900</span>

<!-- 市售價（刪除線） -->
<del class="seoPrice">11,900</del>
```

## 實施的修改

### 1. 更新 `scraper.py` 中的 `_extract_price()` 方法
- **優先級 1**: `span.seoPrice` 選擇器（促銷價）
- **優先級 2**: `del.seoPrice` 選擇器（市售價）
- **備選選擇器**: 13+ 個其他選擇器用於不同平台

### 2. 同步更新 `similar_finder.py` 中的 `_extract_price()` 方法
- 保持相同的邏輯和優先級

### 3. 修正 URL 檢測
- 從 `'momoshop'` 改為 `'momo.com.tw'` 以正確識別 Momo URL

### 4. 改進 Selenium 配置
- 添加反爬蟲檢測繞過機制
- 增加等待時間
- 改進 User-Agent 配置
- 添加降級機制（動態爬取失敗→靜態爬取）

## 遇到的技術挑戰

### 主要問題：Momo 強力的反爬蟲機制
Momo 使用以下技術防止爬蟲訪問：

1. **完全的 JavaScript 動態載入**
   - 服務器返回的初始 HTML 不包含實際商品數據
   - 所有價格、名稱、規格等都通過 JavaScript 動態加載
   - 即使使用 Selenium，也無法正確載入內容

2. **請求檢測**
   - 儘管添加了正確的 User-Agent 和 headers，仍然返回最小化的 HTML
   - 可能使用基於 IP、時間戳或其他特徵的檢測

3. **頁面重定向**
   - 檢測到非移動客戶端後可能會重定向到移動版
   - 移動版頁面結構完全不同，沒有 seoPrice 元素

## 技術驗證結果

### ✅ 成功完成的部分
- ✅ 正確識別了 HTML 選擇器（`span.seoPrice` 和 `del.seoPrice`）
- ✅ 實施了價格優先級邏輯
- ✅ 更新了兩個爬蟲模塊
- ✅ 修正了 URL 檢測邏輯
- ✅ 添加了降級機制

### ⚠️ 無法克服的問題
- ⚠️ Momo 伺服器返回的 HTML 不包含價格數據
- ⚠️ Selenium 也無法完全載入 JavaScript 內容
- ⚠️ 可能需要更高級的工具（如 Puppeteer、Playwright）

## 測試結果

```
📍 URL: https://www.momo.com.tw/product/DgrailProduct/34500891?cid=DgrailProduct

✅ 請求成功 (狀態碼: 200)
❌ HTML 不包含 seoPrice 類
❌ 未找到價格文本 (9,900 或 11,900)
❌ Selenium 爬取後仍無法找到元素
```

## 建議的解決方案

### 短期方案
1. **使用 Playwright/Puppeteer**
   - 比 Selenium 更強大的 JavaScript 執行
   - 可能能夠繞過反爬蟲機制

2. **Momo 官方 API**
   - 如果存在，可以直接調用 API
   - 避免前端爬蟲問題

3. **Momo 搜尋結果頁面**
   - 搜尋結果可能包含部分結構化數據
   - 可作為備選方案

### 長期方案
1. **與 Momo 合作**
   - 申請官方數據訪問權限
   - 使用合法的数据接口

2. **監控 Momo API**
   - 使用瀏覽器開發者工具找到實際使用的 API
   - 直接調用 API 而非爬取 HTML

3. **用戶手動輸入**
   - 對於無法自動爬取的商品
   - 提供手動輸入價格的功能

## 代碼變更摘要

### 修改的文件
1. `/home/brain/CP_Compare/utils/scraper.py`
   - 更新了 `_extract_price()` 方法
   - 改進了 `scrape_dynamic()` 配置
   - 添加了降級機制

2. `/home/brain/CP_Compare/utils/similar_finder.py`
   - 更新了 `_extract_price()` 方法
   - 修正了 URL 檢測邏輯

### 關鍵代碼片段
```python
def _extract_price(self, soup):
    """提取價格 - 支援多個平台，優先提取促銷價"""
    
    # === Momo 特定邏輯：優先使用促銷價，否則使用市售價 ===
    # 促銷價 (紅色顯示的價格)
    promo_price = soup.find('span', class_='seoPrice')
    if promo_price:
        # ... 提取價格邏輯 ...
        return price
    
    # 市售價 (刪除線的價格)
    sale_price = soup.find('del', class_='seoPrice')
    if sale_price:
        # ... 提取價格邏輯 ...
        return price
    
    # ... 備選選擇器 ...
```

## 結論

雖然已經成功實施了用戶要求的價格優先級邏輯，但由於 Momo 採用的強力反爬蟲技術，無法通過傳統爬蟲獲取數據。

**建議下一步行動**：
1. 嘗試使用 Playwright 或其他更強大的自動化工具
2. 調查 Momo 是否提供 API
3. 考慮為用戶提供手動輸入選項

**當前狀態**：代碼已準備就緒，一旦能夠獲取 HTML，邏輯將正確運行。
