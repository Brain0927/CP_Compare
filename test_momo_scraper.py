#!/usr/bin/env python3
"""
測試 Momo 爬蟲是否正確提取價格和規格
"""
import sys
sys.path.insert(0, '/home/brain/CP_Compare')

from utils.scraper import ProductScraper
from utils.similar_finder import SimilarProductFinder

# 測試 URL
urls = [
    "https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=14243108&Area=search&mdiv=403&oid=1_21&cid=index&kw=%E8%80%B3%E6%A9%9F",
    "https://www.momoshop.com.tw/goods/GoodsDetail.jsp?i_code=10201991&mdiv=411412"
]

print("="*70)
print("🧪 Momo 商品爬蟲測試")
print("="*70)

scraper = ProductScraper()
finder = SimilarProductFinder()

for i, url in enumerate(urls, 1):
    print(f"\n【測試 {i}】")
    print(f"URL: {url[:80]}...")
    print("-"*70)
    
    # 使用爬蟲
    product = scraper.extract_product_info(url, is_dynamic=False)
    
    if product:
        print(f"✅ 爬蟲成功")
        print(f"   商品名稱: {product['name'][:60]}")
        print(f"   價格: ${product['price']:,.0f}")
        print(f"   評分: {product['rating']:.1f}/5.0")
        print(f"   規格數: {len(product['specs'])} 項")
        
        if product['specs']:
            print(f"   規格項目:")
            for key, value in list(product['specs'].items())[:5]:
                print(f"      • {key}: {value[:50]}")
    else:
        print(f"❌ 爬蟲失敗")
    
    # 使用 similar_finder
    print(f"\n   尋找相似商品...")
    similar = finder.extract_product_info_from_url(url)
    
    if similar:
        print(f"   ✅ Similar Finder 成功")
        print(f"      名稱: {similar['name'][:60]}")
        print(f"      價格: ${similar['price']:,.0f}")
        print(f"      類別: {similar['category']}")
        
        # 生成搜尋關鍵字
        search_queries = finder.generate_search_queries(similar)
        print(f"      建議搜尋關鍵字: {', '.join(search_queries[:3])}")

print("\n" + "="*70)
print("✅ 測試完成")
print("="*70)
