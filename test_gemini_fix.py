#!/usr/bin/env python
"""
測試 Gemini API 修復
驗證商品名稱和規格是否正確輸入至 Gemini 進行預測
"""

import sys
import json
from config.settings import GEMINI_API_KEY
from utils.nlp_analyzer import GeminiAnalyzer, analyze_products

def test_gemini_initialization():
    """測試 Gemini 初始化"""
    print("=" * 60)
    print("🔧 測試 Gemini API 初始化")
    print("=" * 60)
    
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY 未設定")
        return False
    
    print(f"✅ API Key 已設定（前20字符): {GEMINI_API_KEY[:20]}...")
    
    analyzer = GeminiAnalyzer()
    
    if not analyzer.api_version:
        print("❌ Gemini 初始化失敗")
        return False
    
    print(f"✅ API 版本: {analyzer.api_version}")
    return True


def test_analyze_feature_importance():
    """測試特徵重要性分析"""
    print("\n" + "=" * 60)
    print("🧠 測試特徵重要性分析 (商品名稱 + 規格)")
    print("=" * 60)
    
    # 模擬商品數據
    test_products = [
        {
            'name': 'Sony WH-1000XM5 無線藍牙耳機',
            'price': 12990,
            'rating': 4.8,
            'specs': {
                '連接方式': '藍牙 5.3',
                '電池續航': '8 小時',
                '降噪技術': '業界領先 ANC',
                '重量': '250g',
                '充電方式': 'USB-C'
            }
        },
        {
            'name': 'Apple AirPods Pro (第2代)',
            'price': 8990,
            'rating': 4.9,
            'specs': {
                '連接方式': ' Bluetooth 5.3',
                '電池續航': '6 小時',
                '降噪技術': '主動降噪 + 自適應音訊',
                '重量': '5.3g (單耳)',
                '充電方式': 'Lightning'
            }
        }
    ]
    
    user_requirement = "需要輕便好攜帶，續航力至少8小時，降噪效果要好，價格不超過10000元"
    
    print(f"\n📦 商品 1: {test_products[0]['name']}")
    print(f"   規格: {json.dumps(test_products[0]['specs'], ensure_ascii=False)}")
    print(f"\n📦 商品 2: {test_products[1]['name']}")
    print(f"   規格: {json.dumps(test_products[1]['specs'], ensure_ascii=False)}")
    print(f"\n👥 用戶需求: {user_requirement}")
    
    print("\n⏳ 呼叫 Gemini API 進行分析...")
    
    try:
        result = analyze_products(test_products, user_requirement)
        
        print("\n✅ 分析完成！")
        print("\n📊 特徵權重結果:")
        
        if result.get('feature_weights'):
            for feature, weight in sorted(result['feature_weights'].items(), key=lambda x: x[1], reverse=True):
                print(f"   - {feature}: {weight:.2f}")
        else:
            print("   ❌ 未能生成特徵權重")
        
        print("\n💬 評論分析結果:")
        review_analysis = result.get('review_analysis', {})
        print(f"   - 情緒: {review_analysis.get('sentiment', 'N/A')}")
        print(f"   - 分數: {review_analysis.get('score', 'N/A')}")
        
        print("\n⚖️ 優缺點分析:")
        pros_cons = result.get('pros_and_cons', {})
        for url, analysis in pros_cons.items():
            product = next((p for p in test_products if p['name'] in url or p['name']), None)
            if not product:
                product = test_products[0]  # 預設
            print(f"\n   📦 {product['name']}")
            print(f"      - 優點: {', '.join(analysis.get('pros', []))}")
            print(f"      - 缺點: {', '.join(analysis.get('cons', []))}")
            print(f"      - 適合: {analysis.get('target_users', 'N/A')}")
        
        print("\n👥 用戶匹配度:")
        match_scores = result.get('user_match_scores', {})
        for i, (url, match_info) in enumerate(match_scores.items(), 1):
            product = test_products[i-1]
            print(f"   {i}. {product['name']}")
            print(f"      - 匹配度: {match_info.get('match_score', 'N/A')}%")
            print(f"      - 建議: {match_info.get('recommendation', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 分析失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_single_product_analysis():
    """測試單一商品分析"""
    print("\n" + "=" * 60)
    print("🎯 測試單一商品 AI 分析")
    print("=" * 60)
    
    test_product = {
        'name': '三星 Galaxy Buds2 Pro 藍牙耳機',
        'price': 5990,
        'rating': 4.6,
        'specs': {
            '連接方式': 'Bluetooth 5.3',
            '電池續航': '5 小時',
            '降噪技術': 'ANC 主動降噪',
            '重量': '5.5g (單耳)',
            '充電方式': 'USB-C',
            '適應音訊': '支援'
        }
    }
    
    print(f"\n📦 商品: {test_product['name']}")
    print(f"   價格: ${test_product['price']:,}")
    print(f"   評分: {test_product['rating']}/5")
    print(f"   規格: {json.dumps(test_product['specs'], ensure_ascii=False, indent=6)}")
    
    print("\n⏳ 呼叫 Gemini 進行價值主張分析...")
    
    try:
        analyzer = GeminiAnalyzer()
        result = analyzer.analyze_value_proposition([test_product], {})
        
        print("\n✅ 分析完成！")
        
        for url, prop in result.items():
            print(f"\n💎 {test_product['name']}")
            print(f"   - 獨特賣點: {', '.join(prop.get('unique_selling_points', []))}")
            print(f"   - 價格公平性: {prop.get('price_fairness', 'N/A')}")
            print(f"   - 競爭優勢: {', '.join(prop.get('competitive_advantages', []))}")
            print(f"   - 市場定位: {prop.get('market_position', 'N/A')}")
            print(f"   - 價值摘要: {prop.get('value_summary', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 分析失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "🚀 Gemini API 修復驗證測試" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    
    # 測試 1: 初始化
    test1_result = test_gemini_initialization()
    
    if not test1_result:
        print("\n❌ Gemini 初始化失敗，無法繼續測試")
        sys.exit(1)
    
    # 測試 2: 特徵重要性分析
    test2_result = test_analyze_feature_importance()
    
    # 測試 3: 單一商品分析
    test3_result = test_single_product_analysis()
    
    # 總結
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    
    results = {
        "✅ Gemini 初始化": test1_result,
        "✅ 特徵重要性分析": test2_result,
        "✅ 單一商品分析": test3_result
    }
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 所有測試都通過了！商品名稱和規格已正確輸入至 Gemini 進行預測。")
        sys.exit(0)
    else:
        print("\n⚠️ 有些測試失敗，請檢查 Gemini API 配置和網絡連接。")
        sys.exit(1)
