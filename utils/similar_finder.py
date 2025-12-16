"""
相似商品搜尋模組 - 自動找出相似商品
"""
import requests
from bs4 import BeautifulSoup
from config.settings import HEADERS, REQUEST_TIMEOUT
import re
from typing import List, Dict


class SimilarProductFinder:
    """尋找相似商品"""
    
    def __init__(self):
        self.headers = HEADERS
        self.timeout = REQUEST_TIMEOUT
    
    def extract_product_info_from_url(self, url: str) -> Dict:
        """
        從URL提取商品資訊
        
        Returns:
            {
                'name': str,
                'price': float,
                'category': str,
                'specs': dict,
                'url': str
            }
        """
        try:
            # Momo 商品自動使用動態爬取
            is_dynamic = 'momo.com.tw' in url.lower()
            
            if is_dynamic:
                from selenium import webdriver
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                import time
                
                driver = None
                try:
                    options = webdriver.ChromeOptions()
                    options.add_argument('--no-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--start-maximized')
                    
                    driver = webdriver.Chrome(options=options)
                    driver.get(url)
                    
                    # 等待價格元素載入
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "money"))
                    )
                    time.sleep(2)
                    
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                except:
                    # Selenium 失敗，回退到靜態爬取
                    response = requests.get(url, headers=self.headers, timeout=self.timeout)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.content, 'html.parser')
                finally:
                    if driver:
                        driver.quit()
            else:
                response = requests.get(url, headers=self.headers, timeout=self.timeout)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取基本資訊
            product_info = {
                'name': self._extract_name(soup),
                'price': self._extract_price(soup),
                'category': self._extract_category(soup, url),
                'specs': self._extract_specs(soup),
                'url': url,
                'reviews': self._extract_reviews(soup),
                'rating': self._extract_rating(soup)
            }
            
            return product_info
            
        except Exception as e:
            print(f"❌ 提取失敗: {e}")
            return None
    
    def _extract_name(self, soup):
        """提取商品名稱"""
        # Momo 特定選擇器
        momo_selectors = [
            'h1.title',
            'h1[class*="title"]',
            'div.goods-name',
            'span.goods-title',
            'div[data-testid*="name"]'
        ]
        
        # 通用選擇器
        general_selectors = ['h1', '.product-title', '[data-name]', '.title', 'h2']
        
        all_selectors = momo_selectors + general_selectors
        
        for selector in all_selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    name = elem.get_text(strip=True)
                    if name and len(name) > 3:  # 確保不是太短的文本
                        return name
            except:
                continue
        
        return "未知商品"
    
    def _extract_price(self, soup):
        """提取價格 - 支援多個平台，優先提取促銷價"""
        
        # === Momo 特定邏輯：優先使用促銷價，否則使用市售價 ===
        # 促銷價 (紅色顯示的價格)
        promo_price = soup.find('span', class_='seoPrice')
        if promo_price:
            text = promo_price.get_text(strip=True)
            price_str = ''.join(c for c in text if c.isdigit() or c in '.,')
            price_str = price_str.replace(',', '')
            try:
                price = float(price_str)
                if price > 0:
                    return price
            except:
                pass
        
        # 市售價 (刪除線的價格)
        sale_price = soup.find('del', class_='seoPrice')
        if sale_price:
            text = sale_price.get_text(strip=True)
            price_str = ''.join(c for c in text if c.isdigit() or c in '.,')
            price_str = price_str.replace(',', '')
            try:
                price = float(price_str)
                if price > 0:
                    return price
            except:
                pass
        
        # === 備用選擇器（其他平台或結構） ===
        momo_selectors = [
            'span.money',                      # Momo 主要價格
            'p.current-price span.money',      # Momo 完整路徑
            'span[class*="money"]',            # Momo 模糊匹配
            'div.goods-price',
            'strong.price',
            'em.price',
            'span[class*="salesprice"]',
            'span[class*="sale-price"]',
        ]
        
        # 通用選擇器（備用）
        general_selectors = [
            '.price', '[data-price]', '.product-price', '.sale-price', 
            '.final-price', '.current-price', '.priceText'
        ]
        
        all_selectors = momo_selectors + general_selectors
        
        for selector in all_selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    # 嘗試從 data 屬性中獲取
                    if elem.get('data-price'):
                        try:
                            return float(elem.get('data-price'))
                        except:
                            pass
                    
                    # 從文本內容中提取
                    text = elem.get_text(strip=True)
                    if text:
                        # 移除非數字字元（保留小數點和逗號）
                        price_str = ''.join(c for c in text if c.isdigit() or c in '.,')
                        
                        # 移除逗號（千位分隔符）
                        price_str = price_str.replace(',', '')
                        
                        # 移除多個小數點，只保留最後一個
                        if price_str.count('.') > 1:
                            parts = price_str.split('.')
                            price_str = '.'.join([parts[0], parts[-1]])
                        
                        if price_str and price_str != '.':
                            try:
                                price = float(price_str)
                                if price > 0:  # 確保價格有效
                                    return price
                            except ValueError:
                                continue
            except:
                continue
        
        return 0
    
    def _extract_category(self, soup, url: str) -> str:
        """提取商品類別"""
        # 嘗試從麵包屑導航提取
        breadcrumb = soup.select_one('.breadcrumb, .breadcrumbs')
        if breadcrumb:
            items = breadcrumb.find_all(['li', 'a'])
            if len(items) >= 2:
                return items[-2].get_text(strip=True)
        
        # 從URL提取
        if 'phone' in url or 'iphone' in url or 'samsung' in url:
            return '手機'
        elif 'laptop' in url or 'notebook' in url or 'macbook' in url:
            return '筆電'
        elif 'headphone' in url or 'earphone' in url or 'earbud' in url:
            return '耳機'
        elif 'watch' in url:
            return '智能手錶'
        elif 'tablet' in url or 'ipad' in url:
            return '平板'
        
        return '電子產品'
    
    def _extract_specs(self, soup) -> dict:
        """提取規格"""
        specs = {}
        
        # 尋找規格表
        spec_sections = soup.find_all(['dl', '.specs', '[data-specs]'])
        
        for section in spec_sections:
            dts = section.find_all('dt')
            dds = section.find_all('dd')
            
            for dt, dd in zip(dts, dds):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                if key and value:
                    specs[key] = value
        
        return specs
    
    def _extract_reviews(self, soup) -> list:
        """提取評論"""
        reviews = []
        review_elements = soup.find_all(['div', 'li'], class_=lambda x: x and 'review' in x.lower())
        
        for elem in review_elements[:5]:
            review_text = elem.get_text(strip=True)
            if review_text:
                reviews.append(review_text)
        
        return reviews
    
    def _extract_rating(self, soup) -> float:
        """提取評分"""
        # Momo 特定選擇器
        momo_selectors = [
            'span.rating-score',
            'div[class*="rating"]',
            'span[class*="score"]',
            'div.star-score',
            'span[class*="mrate"]',        # Momo 評分
            'div[data-testid*="rating"]'
        ]
        
        # 通用選擇器
        general_selectors = ['.rating', '[data-rating]', '.star', '.score', '.rate']
        
        all_selectors = momo_selectors + general_selectors
        
        for selector in all_selectors:
            try:
                elem = soup.select_one(selector)
                if elem:
                    text = elem.get_text(strip=True)
                    # 提取數字部分
                    numbers = [c for c in text if c.isdigit() or c == '.']
                    if numbers:
                        rating_str = ''.join(numbers)
                        try:
                            rating = float(rating_str)
                            if 0 <= rating <= 5.0:  # 確保評分在有效範圍
                                return rating
                        except ValueError:
                            continue
            except:
                continue
        
        return 0
    
    def generate_search_queries(self, product_info: Dict) -> List[str]:
        """
        生成搜尋查詢
        
        基於商品名稱、類別生成搜尋關鍵字
        """
        queries = []
        
        # 基於品牌
        name_parts = product_info['name'].split()
        if name_parts:
            brand = name_parts[0]
            queries.append(brand)
        
        # 基於類別
        category = product_info.get('category', '電子產品')
        if category != '電子產品':
            queries.append(category)
        
        # 基於完整名稱
        queries.append(product_info['name'])
        
        # 基於規格
        for spec_name in product_info['specs'].keys():
            queries.append(spec_name)
        
        return list(set(queries))  # 移除重複
    
    def build_search_urls(self, product_info: Dict, platform: str = 'momo') -> List[str]:
        """
        建立搜尋URL
        
        根據不同平台構建搜尋連結
        """
        queries = self.generate_search_queries(product_info)
        search_urls = []
        
        if platform == 'momo':
            base_url = "https://www.momoshop.com.tw/search/searchShop.php?keyword="
            for query in queries[:3]:
                search_urls.append(base_url + query)
        
        elif platform == 'pchome':
            base_url = "https://www.pchome.com.tw/search/?q="
            for query in queries[:3]:
                search_urls.append(base_url + query)
        
        elif platform == 'shopee':
            base_url = "https://shopee.tw/search?keyword="
            for query in queries[:3]:
                search_urls.append(base_url + query)
        
        return search_urls
    
    def find_similar_products_on_same_platform(self, product_url: str, max_results: int = 3) -> List[Dict]:
        """
        在同一平台上尋找相似商品
        
        Returns:
            List[Dict]: 包含原商品和相似商品的列表
        """
        # 提取原商品資訊
        product_info = self.extract_product_info_from_url(product_url)
        
        if not product_info:
            return []
        
        # 判斷平台
        if 'momo.com.tw' in product_url:
            platform = 'momo'
        elif 'pchome' in product_url:
            platform = 'pchome'
        elif 'shopee' in product_url:
            platform = 'shopee'
        else:
            platform = 'momo'  # 預設
        
        print(f"\n{'='*60}")
        print(f"🔍 尋找相似商品...")
        print(f"{'='*60}")
        print(f"🏷️  原商品: {product_info['name']}")
        print(f"💰 原價格: ${product_info['price']:,.0f}")
        print(f"📂 類別: {product_info['category']}")
        print(f"⭐ 評分: {product_info['rating']:.1f}/5.0")
        
        # 生成搜尋關鍵字
        search_queries = self.generate_search_queries(product_info)
        
        print(f"🔎 搜尋關鍵字: {', '.join(search_queries[:3])}")
        print(f"{'='*60}\n")
        
        similar_products = [product_info]  # 包含原商品
        
        # 為每個搜尋關鍵字建立搜尋 URL
        search_urls = self.build_search_urls(product_info, platform)
        
        print(f"📌 推薦搜尋方式:")
        print(f"   1. 訪問 {platform.upper()} 平台")
        print(f"   2. 搜尋以下關鍵字:")
        for i, query in enumerate(search_queries[:3], 1):
            print(f"      {i}. {query}")
        print(f"   3. 篩選相似規格的商品進行比較\n")
        
        return similar_products


def get_similar_products(product_url: str) -> List[Dict]:
    """
    主函數：取得相似商品
    
    Args:
        product_url: 商品連結
    
    Returns:
        list: 相似商品列表
    """
    finder = SimilarProductFinder()
    similar_products = finder.find_similar_products_on_same_platform(product_url, max_results=3)
    
    return similar_products
