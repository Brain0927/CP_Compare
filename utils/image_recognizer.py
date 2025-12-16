"""
圖像識別模組 - 使用 Gemini Vision API 識別商品規格圖像
"""
import base64
import requests
from io import BytesIO
from PIL import Image
from typing import Dict, List, Optional
import google.generativeai as genai
from config.settings import GEMINI_API_KEY
import time


class ImageRecognizer:
    """圖像識別器 - 使用 Gemini Vision 識別規格圖像"""
    
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    @staticmethod
    def download_image(url: str) -> Optional[bytes]:
        """下載圖像為位元組"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=15, headers=headers)
            if response.status_code == 200:
                print(f"✅ 圖像下載成功: {url[:60]}...")
                return response.content
            else:
                print(f"❌ 圖像下載失敗 (HTTP {response.status_code}): {url}")
        except Exception as e:
            print(f"❌ 圖像下載失敗: {e} ({url})")
        return None
    
    def extract_specs_from_image_url(self, image_url: str) -> Dict[str, str]:
        """從圖像 URL 中提取規格資訊"""
        try:
            # 下載圖像
            image_data = self.download_image(image_url)
            if not image_data:
                return {}
            
            print(f"🖼️ 正在用 Gemini Vision 識別圖像規格...")
            
            # 使用 Gemini Vision 識別圖像中的規格
            prompt = """你是商品規格識別專家。請分析這張圖像中的商品規格信息。

**請務必提取以下信息（如果圖像中有的話）：**
1. 材質/材料
2. 尺寸/大小/長寬高
3. 重量
4. 顏色
5. 功能/特性
6. 型號
7. 保修/保固期限
8. 電源/電池
9. 規格/參數
10. 其他重要規格

**返回格式要求：**
- 每行一個規格，格式為「規格名稱: 規格值」
- 只返回規格信息，不需要其他說明
- 盡可能詳細準確"""
            
            # 將圖像發送給 Gemini Vision
            response = self.model.generate_content([
                prompt,
                Image.open(BytesIO(image_data))
            ])
            
            print(f"📝 Gemini 响应内容: {response.text[:100]}...")
            
            # 解析響應
            specs = self._parse_specs_response(response.text)
            print(f"✅ 成功識別到 {len(specs)} 個規格")
            
            return specs
            
        except Exception as e:
            print(f"❌ 圖像識別失敗: {str(e)}")
            import traceback
            traceback.print_exc()
            return {}
    
    def extract_specs_from_images(self, image_urls: List[str]) -> Dict[str, str]:
        """從多張圖像中提取規格資訊（合併所有規格）"""
        all_specs = {}
        
        print(f"📊 開始識別 {len(image_urls)} 張圖像...")
        
        for i, url in enumerate(image_urls, 1):
            print(f"\n【圖像 {i}/{len(image_urls)}】 {url[:50]}...")
            specs = self.extract_specs_from_image_url(url)
            
            if specs:
                all_specs.update(specs)
                print(f"  → 本張圖像識別結果: {len(specs)} 個規格")
            else:
                print(f"  → 本張圖像未識別到規格")
            
            # 避免 API 限流
            if i < len(image_urls):
                print("⏳ 等待中... (避免 API 限流)")
                time.sleep(2)
        
        print(f"\n📊 所有圖像識別完成，共 {len(all_specs)} 個規格")
        return all_specs
    
    @staticmethod
    def _parse_specs_response(response_text: str) -> Dict[str, str]:
        """解析 Gemini 的規格識別響應"""
        specs = {}
        
        print(f"📝 正在解析 Gemini 響應...")
        lines = response_text.split('\n')
        valid_count = 0
        
        for line in lines:
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            try:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    
                    # 清理 key（移除編號、括號等）
                    key = key.lstrip('0123456789.）)、 ')
                    
                    # 過濾掉無效值
                    if (key and value and 
                        len(key) > 1 and len(value) > 1 and
                        value.lower() not in ['', 'n/a', '無', '未找到', 'not found', '暫無']):
                        specs[key] = value
                        valid_count += 1
                        print(f"  ✓ {key}: {value}")
            except Exception as e:
                continue
        
        print(f"📊 本次識別結果: {valid_count} 個有效規格")
        return specs


class MomoImageExtractor:
    """MOMO 特定的圖像提取器"""
    
    @staticmethod
    def extract_spec_images_from_soup(soup) -> List[str]:
        """從 BeautifulSoup 對象中提取規格圖像 URL（MOMO 特定）"""
        image_urls = []
        
        try:
            print("🔍 正在搜尋 MOMO 規格圖像...")
            
            # 方法 1：查找規格圖像容器
            spec_section = soup.find('div', {'class': lambda x: x and 'spec' in x.lower()})
            
            if spec_section:
                images = spec_section.find_all('img')
                for img in images:
                    src = img.get('src', '') or img.get('data-src', '')
                    alt = img.get('alt', '')
                    
                    # 檢查是否是規格相關圖像
                    if src and ('spec' in alt.lower() or 'spec' in src.lower() or 'momo' in src.lower()):
                        if src.startswith('http') or src.startswith('//'):
                            image_urls.append(src if src.startswith('http') else 'https:' + src)
                            print(f"  ✓ 找到規格圖像: {src[:60]}...")
            
            # 方法 2：查找產品詳情區的所有圖像
            if not image_urls:
                print("  ⚠️ 規格容器搜尋未果，嘗試備選方案...")
                detail_sections = soup.find_all('div', {'class': lambda x: x and any(
                    kw in x.lower() for kw in ['detail', 'info', 'spec', 'product']
                )})
                
                for section in detail_sections[:3]:  # 最多查找 3 個區塊
                    images = section.find_all('img', limit=5)
                    for img in images:
                        src = img.get('src', '') or img.get('data-src', '')
                        if src and ('momo' in src.lower() or '.jpg' in src.lower() or '.png' in src.lower()):
                            if src.startswith('http') or src.startswith('//'):
                                full_url = src if src.startswith('http') else 'https:' + src
                                if full_url not in image_urls:
                                    image_urls.append(full_url)
                                    print(f"  ✓ 找到圖像: {src[:60]}...")
            
            # 方法 3：查找所有有效的產品圖像
            if not image_urls:
                print("  ⚠️ 嘗試最後備選方案...")
                all_imgs = soup.find_all('img', limit=20)
                for img in all_imgs:
                    src = img.get('src', '') or img.get('data-src', '')
                    if src and 'momo' in src.lower() and '.jpg' in src.lower():
                        full_url = src if src.startswith('http') else 'https:' + src
                        if full_url not in image_urls:
                            image_urls.append(full_url)
                            print(f"  ✓ 找到圖像: {src[:60]}...")
                            if len(image_urls) >= 5:
                                break
            
            print(f"✅ 共找到 {len(image_urls)} 張圖像")
            return image_urls[:5]  # 限制最多 5 張圖像
        
        except Exception as e:
            print(f"❌ 提取規格圖像失敗: {e}")
            import traceback
            traceback.print_exc()
        
        return image_urls


def extract_momo_specs_from_images(soup) -> Dict[str, str]:
    """從 MOMO 頁面規格圖像中提取資訊（主函數）"""
    try:
        print("\n" + "="*60)
        print("🖼️  開始 MOMO 商品規格圖像識別流程")
        print("="*60)
        
        # 提取圖像 URL
        extractor = MomoImageExtractor()
        image_urls = extractor.extract_spec_images_from_soup(soup)
        
        if not image_urls:
            print("⚠️  未找到規格圖像")
            return {}
        
        print(f"\n📝 找到 {len(image_urls)} 張規格圖像，開始識別...")
        
        # 使用圖像識別器提取規格
        recognizer = ImageRecognizer()
        specs = recognizer.extract_specs_from_images(image_urls)
        
        print("\n" + "="*60)
        print(f"✅ MOMO 規格圖像識別完成，共識別到 {len(specs)} 個規格")
        print("="*60 + "\n")
        
        return specs
        
    except Exception as e:
        print(f"\n❌ MOMO 規格圖像提取失敗: {e}")
        import traceback
        traceback.print_exc()
        return {}
