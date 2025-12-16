"""
爬蟲模組 - 使用 BeautifulSoup 與 Selenium
"""
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.settings import HEADERS, REQUEST_TIMEOUT, SELENIUM_WAIT_TIME
import time
import json

# 導入圖像識別模組
try:
    from utils.image_recognizer import extract_momo_specs_from_images
    IMAGE_RECOGNITION_AVAILABLE = True
except ImportError:
    IMAGE_RECOGNITION_AVAILABLE = False
    print("⚠️  圖像識別功能未安裝")


class ProductScraper:
    """商品爬蟲基類"""
    
    def __init__(self):
        self.headers = HEADERS
        self.timeout = REQUEST_TIMEOUT
    
    def scrape_static(self, url):
        """爬取靜態頁面 (BeautifulSoup)"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.encoding = 'utf-8'
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"❌ 靜態頁面爬取失敗: {e}")
            return None
    
    def scrape_dynamic(self, url):
        """爬取動態頁面 (Selenium)"""
        driver = None
        try:
            options = webdriver.ChromeOptions()
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--start-maximized')
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=options)
            
            # 添加 User-Agent
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            
            driver.get(url)
            
            # 等待頁面加載
            WebDriverWait(driver, SELENIUM_WAIT_TIME).until(
                EC.presence_of_all_elements_located((By.TAG_NAME, "body"))
            )
            
            time.sleep(3)  # 額外等待時間確保 JS 執行完成
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            return soup
            
        except Exception as e:
            print(f"❌ 動態頁面爬取失敗: {e}")
            return None
        finally:
            if driver:
                driver.quit()
    
    def extract_product_info(self, url, is_dynamic=False):
        """
        提取商品資訊
        
        Args:
            url: 商品連結
            is_dynamic: 是否為動態頁面
        
        Returns:
            dict: 商品資訊 {name, price, specs, reviews, url}
        """
        # Momo 商品自動使用動態爬取（因為價格通過 JS 載入）
        if 'momo.com.tw' in url.lower():
            is_dynamic = True
        
        # 先嘗試動態爬取
        soup = None
        if is_dynamic:
            soup = self.scrape_dynamic(url)
        
        # 如果動態爬取失敗，降級到靜態爬取
        if not soup:
            print(f"⚠️  動態爬取失敗，降級到靜態爬取...")
            soup = self.scrape_static(url)
        
        if not soup:
            return None
        
        # 通用爬取邏輯（簡化版，實際需根據各平台調整）
        product_info = {
            "url": url,
            "name": self._extract_name(soup),
            "price": self._extract_price(soup),
            "specs": self._extract_specs(soup),
            "reviews": self._extract_reviews(soup),
            "rating": self._extract_rating(soup)
        }
        
        return product_info
    
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
    
    def _extract_specs(self, soup):
        """提取規格資訊 - 支援 Momo 結構並使用圖像識別"""
        specs = {}
        
        # === Momo 規格表結構 ===
        # 嘗試找到規格容器
        spec_containers = soup.find_all(['dl', 'table', 'div'], class_=lambda x: x and any(
            keyword in x.lower() for keyword in ['spec', 'attribute', 'property', 'info', 'detail', '規格']
        ))
        
        # 嘗試 DL/DT/DD 結構
        for container in spec_containers:
            dts = container.find_all('dt') if container.find_all('dt') else []
            dds = container.find_all('dd') if container.find_all('dd') else []
            
            for dt, dd in zip(dts, dds):
                key = dt.get_text(strip=True)
                value = dd.get_text(strip=True)
                if key and value and len(key) < 50 and len(value) < 200:
                    specs[key] = value
        
        # 嘗試表格結構
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value and len(key) < 50 and len(value) < 200:
                        specs[key] = value
        
        # 嘗試 Div 結構（Momo 常用）
        if not specs:
            # 尋找包含「規格」或「特性」的 div
            spec_divs = soup.find_all('div', class_=lambda x: x and any(
                kw in x.lower() for kw in ['spec', 'detail', 'property', 'info']
            ))
            
            for div in spec_divs:
                # 尋找標籤和數值對
                labels = div.find_all(['label', 'strong', 'b'], limit=10)
                for label in labels:
                    label_text = label.get_text(strip=True)
                    # 找到緊鄰的值
                    next_elem = label.find_next('span', 'div', 'td', 'dd')
                    if next_elem:
                        value_text = next_elem.get_text(strip=True)
                        if label_text and value_text:
                            specs[label_text] = value_text
        
        # === MOMO 特定：使用圖像識別補充規格 ===
        if IMAGE_RECOGNITION_AVAILABLE:
            print("🖼️  嘗試從規格圖像中提取資訊...")
            try:
                image_specs = extract_momo_specs_from_images(soup)
                if image_specs:
                    print(f"✅ 從圖像中識別到 {len(image_specs)} 個規格")
                    specs.update(image_specs)
            except Exception as e:
                print(f"⚠️  圖像識別失敗 (非致命): {e}")
        
        return specs
    
    def _extract_reviews(self, soup):
        """提取評論與評價"""
        reviews = []
        review_elements = soup.find_all(['div', 'li'], class_=lambda x: x and 'review' in x.lower())
        
        for elem in review_elements[:5]:  # 限制5則評論
            review_text = elem.get_text(strip=True)
            if review_text:
                reviews.append(review_text)
        
        return reviews
    
    def _extract_rating(self, soup):
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


def scrape_products(urls, is_dynamic=False):
    """
    批次爬取多個商品
    
    Args:
        urls: 商品連結列表
        is_dynamic: 是否為動態頁面
    
    Returns:
        list: 商品資訊列表
    """
    scraper = ProductScraper()
    products = []
    
    for i, url in enumerate(urls, 1):
        print(f"⏳ 正在爬取第 {i}/{len(urls)} 個商品...")
        product = scraper.extract_product_info(url, is_dynamic)
        
        if product:
            products.append(product)
            print(f"✅ 成功爬取: {product['name'][:50]}")
        else:
            print(f"⚠️  爬取失敗: {url}")
        
        time.sleep(1)  # 避免過於頻繁的請求
    
    return products
