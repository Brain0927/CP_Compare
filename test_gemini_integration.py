#!/usr/bin/env python3
"""
測試 Gemini API 集成 - 診斷腳本
用於驗證商品名稱和規格是否正確傳遞給 Gemini
"""
import json
import sys
sys.path.insert(0, '/home/brain/CP_Compare')

from utils.scraper import scrape_products
from utils.data_cleaner import DataCleaner
from utils.nlp_analyzer import analyze_products, GeminiAnalyzer
from config.settings import GEMINI_API_KEY

print("=" * 80)
print("🔬 Gemini API 集成診斷測試")
print("=" * 80)

# 1. 檢查 API Key
print("\n1️⃣ 檢查 API Key...")
if GEMINI_API_KEY:
    print(f"✅ API Key 已配置: {GEMINI_API_KEY[:10]}...")
else:
    print("❌ 未找到 GEMINI_API_KEY，請設置環境變數")
    sys.exit(1)

# 2. 測試 Gemini 連接
print("\n2️⃣ 測試 Gemini API 連接...")
try:
    analyzer = GeminiAnalyzer()
    if analyzer.api_version:
        print(f"✅ Gemini API 初始化成功，版本: {analyzer.api_version}")
    else:
        print("❌ Gemini API 初始化失敗")
        sys.exit(1)
except Exception as e:
    print(f"❌ Gemini 初始化失敗: {e}")
    sys.exit(1)

# 3. 測試簡單的 Gemini 調用
print("\n3️⃣ 測試簡單的 Gemini 調用...")
try:
    test_prompt = "請簡單回答: 1+1 等於多少?"
    response = analyzer._call_gemini(test_prompt)
    if response:
        print(f"✅ Gemini API 調用成功")
        print(f"   回應: {response[:50]}...")
    else:
        print("❌ Gemini API 調用無響應")
except Exception as e:
    print(f"❌ Gemini 調用失敗: {e}")

# 4. 測試樣本商品數據
print("\n4️⃣ 構造樣本商品數據...")
sample_products = [
    {
        'url': 'https://example1.com',
        'name': 'Sony WH-1000XM5 無線藍牙降噪耳機',
        'price': 8990,
        'rating': 4.5,
        'reviews': ['很好用', '降噪效果很棒', '舒適度不錯'],
        'specs': {
            '型號': 'WH-1000XM5',
            '品牌': 'Sony',
            '類型': '無線藍牙',
            '降噪': '主動降噪',
            '續航時間': '30 小時',
            '重量': '250g',
            '連接方式': 'Bluetooth 5.3',
            '驅動單元': '40mm',
            '防水等級': 'IPX4'
        }
    },
    {
        'url': 'https://example2.com',
        'name': 'Apple AirPods Pro (第 2 代)',
        'price': 7990,
        'rating': 4.8,
        'reviews': ['與 Apple 裝置配對完美', '音質很好', '續航不錯'],
        'specs': {
            '型號': 'AirPods Pro (2nd generation)',
            '品牌': 'Apple',
            '類型': '真無線',
            '降噪': '主動降噪',
            '續航時間': '6 小時',
            '充電盒續航': '30 小時',
            '重量': '5.3g (單耳)',
            '連接方式': 'Bluetooth 5.3',
            '防水等級': 'IPX4'
        }
    }
]

print(f"✅ 創建 {len(sample_products)} 個樣本商品")
for i, p in enumerate(sample_products, 1):
    print(f"   商品 {i}: {p['name']}")
    print(f"     - 規格數: {len(p['specs'])}")
    print(f"     - 規格: {list(p['specs'].keys())}")

# 5. 測試 analyze_feature_importance
print("\n5️⃣ 測試 analyze_feature_importance...")
try:
    print("\n📤 傳遞給 Gemini 的數據結構:")
    test_data = []
    for product in sample_products:
        test_data.append({
            'name': product['name'],
            'price': product['price'],
            'rating': product.get('rating', 0),
            'specs': product.get('specs', {})
        })
    
    print(json.dumps(test_data, ensure_ascii=False, indent=2))
    
    print("\n🔄 正在調用 analyze_feature_importance...")
    weights = analyzer.analyze_feature_importance(sample_products)
    
    if weights:
        print("✅ 特徵重要性分析成功")
        print(f"   返回的權重: {json.dumps(weights, ensure_ascii=False, indent=2)}")
    else:
        print("❌ 無法獲得特徵權重")
except Exception as e:
    print(f"❌ 特徵分析失敗: {e}")
    import traceback
    traceback.print_exc()

# 6. 測試完整的 analyze_products
print("\n6️⃣ 測試完整的 analyze_products...")
try:
    print("🔄 正在調用 analyze_products...")
    result = analyze_products(sample_products, user_requirement="尋找高性能降噪耳機")
    
    print("✅ analyze_products 執行完成")
    print(f"   返回的鍵: {list(result.keys())}")
    
    if 'feature_weights' in result:
        print(f"\n   特徵權重: {json.dumps(result['feature_weights'], ensure_ascii=False, indent=2)}")
    
    if 'review_analysis' in result:
        print(f"\n   評論分析: {json.dumps(result['review_analysis'], ensure_ascii=False, indent=2)}")
    
    if 'pros_and_cons' in result:
        print(f"\n   優缺點分析:")
        for url, analysis in result['pros_and_cons'].items():
            print(f"     {url}: {json.dumps(analysis, ensure_ascii=False, indent=2)}")
    
except Exception as e:
    print(f"❌ analyze_products 失敗: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ 診斷測試完成")
print("=" * 80)
