#!/usr/bin/env python3
"""
快速測試腳本 - 驗證所有模組是否正常
"""
import sys
import os

# 添加專案路徑
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """測試所有模組導入"""
    print("=" * 50)
    print("🧪 測試模組導入...")
    print("=" * 50)
    
    try:
        print("✅ 導入 config.settings...")
        from config.settings import GEMINI_API_KEY, COMMON_FEATURES
        print(f"   - API 金鑰: {'已設定' if GEMINI_API_KEY else '❌ 未設定'}")
        print(f"   - 支援特徵數: {len(COMMON_FEATURES)}")
        
        print("✅ 導入 utils.scraper...")
        from utils.scraper import ProductScraper
        
        print("✅ 導入 utils.data_cleaner...")
        from utils.data_cleaner import DataCleaner
        
        print("✅ 導入 utils.nlp_analyzer...")
        from utils.nlp_analyzer import GeminiAnalyzer
        
        print("✅ 導入 utils.cp_calculator...")
        from utils.cp_calculator import CPCalculator
        
        print("\n✅ 所有模組導入成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 模組導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_cleaner():
    """測試資料清洗功能"""
    print("\n" + "=" * 50)
    print("🧪 測試資料清洗...")
    print("=" * 50)
    
    from utils.data_cleaner import DataCleaner
    
    # 測試數值提取
    test_value = "記憶體: 16GB"
    extracted = DataCleaner.extract_numeric(test_value)
    print(f"✅ 數值提取: '{test_value}' → {extracted}")
    
    # 測試單位標準化
    test_unit = "8GB"
    normalized = DataCleaner.normalize_unit(test_unit, "GB")
    print(f"✅ 單位標準化: '{test_unit}' → {normalized}")
    
    # 測試特徵名稱標準化
    feature_names = ["處理器", "CPU", "cpu", "記憶體", "RAM"]
    for fname in feature_names:
        standard = DataCleaner.normalize_feature_name(fname)
        print(f"✅ 特徵標準化: '{fname}' → '{standard}'")
    
    # 測試商品清洗
    sample_product = {
        "name": "  MacBook Pro  ",
        "price": "$39,900",
        "specs": {"CPU": "Apple M3", "RAM": "8 GB"},
        "reviews": [],
        "rating": "4.8"
    }
    
    cleaned = DataCleaner.clean_product(sample_product)
    print(f"\n✅ 商品清洗:")
    print(f"   - 名稱: '{cleaned['name']}'")
    print(f"   - 價格: {cleaned['price']}")
    print(f"   - 規格: {cleaned['specs']}")


def test_cp_calculator():
    """測試 CP 值計算"""
    print("\n" + "=" * 50)
    print("🧪 測試 CP 值計算...")
    print("=" * 50)
    
    from utils.cp_calculator import CPCalculator
    
    # 建立測試商品
    products = [
        {
            "name": "商品 A",
            "price": 10000,
            "rating": 4.5,
            "specs": {
                "CPU": "高效能",
                "RAM": "16GB",
            }
        },
        {
            "name": "商品 B",
            "price": 15000,
            "rating": 4.0,
            "specs": {
                "CPU": "標準",
                "RAM": "8GB",
            }
        }
    ]
    
    # 測試特徵分數
    score = CPCalculator.calculate_feature_score("16", 16, is_numeric=True)
    print(f"✅ 特徵分數計算: 16/16 → {score}")
    
    # 測試 CP 值計算
    feature_weights = {"CPU": 2, "RAM": 3}
    common_features = {
        "CPU": ["高效能", "標準"],
        "RAM": ["16GB", "8GB"]
    }
    
    cp_value = CPCalculator.calculate_cp_value(
        products[0],
        feature_weights,
        common_features
    )
    print(f"✅ CP 值計算: {cp_value:.4f}")
    
    # 測試批次計算
    cp_values = CPCalculator.calculate_all_cp_values(products, feature_weights)
    print(f"✅ 批次 CP 值計算完成:")
    for url, value in cp_values.items():
        print(f"   - {value:.4f}")


def test_sample_data():
    """測試樣本資料"""
    print("\n" + "=" * 50)
    print("🧪 測試樣本資料...")
    print("=" * 50)
    
    from data.sample_products import SAMPLE_PRODUCTS
    
    print(f"✅ 載入 {len(SAMPLE_PRODUCTS)} 個樣本商品")
    
    for i, product in enumerate(SAMPLE_PRODUCTS, 1):
        print(f"\n   {i}. {product['name']}")
        print(f"      價格: ${product['price']:,}")
        print(f"      規格: {len(product['specs'])} 個特徵")
        print(f"      評論: {len(product['reviews'])} 則")
        print(f"      評分: {product['rating']}⭐")


def main():
    """主函數"""
    print("\n")
    print("🚀" * 25)
    print("AI CP 值比較器 - 快速測試")
    print("🚀" * 25)
    
    # 執行測試
    success = True
    
    if not test_imports():
        success = False
    
    try:
        test_data_cleaner()
    except Exception as e:
        print(f"\n❌ 資料清洗測試失敗: {e}")
        success = False
    
    try:
        test_cp_calculator()
    except Exception as e:
        print(f"\n❌ CP值計算測試失敗: {e}")
        success = False
    
    try:
        test_sample_data()
    except Exception as e:
        print(f"\n❌ 樣本資料測試失敗: {e}")
        success = False
    
    # 總結
    print("\n" + "=" * 50)
    if success:
        print("✅ 所有測試通過！系統可以開始使用。")
        print("\n下一步:")
        print("1. 設定 .env 檔案中的 GEMINI_API_KEY")
        print("2. 執行: streamlit run app.py")
    else:
        print("❌ 部分測試失敗，請檢查錯誤訊息。")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
