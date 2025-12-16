"""
NLP 分析模組 - 整合 Gemini API + 本地離線分析
支援在 API 配額不足或無網路時自動切換到本地智能分析
"""
import google.generativeai as genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
import json
from typing import Dict, List, Any
import random

# 本地智能分析規則庫
FEATURE_IMPORTANCE_RULES = {
    # 高優先級特徵 (降噪、續航、CPU、RAM 等性能相關)
    '降噪': 3.0, '主動降噪': 3.0,
    '續航': 3.0, '續航時間': 3.0, '電池': 3.0, '電池容量': 3.0,
    'cpu': 3.0, 'CPU': 3.0, '處理器': 3.0, '處理器性能': 3.0,
    'ram': 3.0, 'RAM': 3.0, '記憶體': 3.0, '運行記憶體': 3.0,
    '性能': 3.0, '計算能力': 3.0,
    
    # 中優先級特徵 (品牌、類型、設計、連接方式)
    '品牌': 2.5, '品牌信譽': 2.5,
    '類型': 2.5, '產品類型': 2.5,
    '螢幕': 2.5, '螢幕尺寸': 2.5, '解析度': 2.5, 'resolution': 2.5,
    '設計': 2.5, '外觀': 2.5, '顏色': 2.0,
    '連接': 2.0, '連接方式': 2.0, '藍牙': 2.0, 'Bluetooth': 2.0,
    '音質': 2.5, '聲音': 2.0, '喇叭': 2.0,
    '防水': 2.0, '防塵': 2.0, '防水等級': 2.0,
    
    # 低優先級特徵 (型號、保固、重量等)
    '型號': 1.5, '型號代碼': 1.5,
    '保固': 1.5, '保修': 1.5, '售後': 1.5,
    '重量': 1.5, '尺寸': 1.5, '厚度': 1.5,
    '材質': 1.5, '材料': 1.5,
    '價格': 1.0, 'price': 1.0,
    '顏色': 1.0, '配色': 1.0,
}


class GeminiAnalyzer:
    """Gemini API 語意分析 + 本地智能備用"""
    
    def __init__(self):
        """初始化 Gemini API，支援配額不足時自動降級"""
        self.use_local_mode = False
        self.api_key = GEMINI_API_KEY
        
        # 如果環境變數中有更新的 API Key，使用它
        import os
        env_key = os.getenv("GEMINI_API_KEY", "")
        if env_key:
            self.api_key = env_key
        
        try:
            if not self.api_key:
                print("⚠️ 未找到 Gemini API Key，使用本地分析模式")
                self.api_version = None
                self.use_local_mode = True
                return
            
            genai.configure(api_key=self.api_key)
            if hasattr(genai, 'GenerativeModel'):
                self.model = genai.GenerativeModel(GEMINI_MODEL)
                self.api_version = 'new'
                print("✅ 使用 Gemini API (線上模式)")
            else:
                self.api_version = 'old'
                print("⚠️ 使用舊版本 Gemini API")
        except Exception as e:
            print(f"⚠️ Gemini 初始化失敗: {e}，使用本地分析模式")
            self.api_version = None
            self.use_local_mode = True
    
    def _call_gemini(self, prompt: str) -> str:
        """統一的 Gemini API 調用，自動降級到本地分析"""
        try:
            if self.api_version == 'new':
                response = self.model.generate_content(prompt)
                return response.text
            elif self.api_version == 'old':
                response = genai.generate_text(
                    prompt=prompt,
                    temperature=0.7,
                    candidate_count=1,
                    max_output_tokens=2048,
                )
                return response.result if response.result else ""
        except Exception as e:
            error_str = str(e).lower()
            if '429' in str(e) or 'quota' in error_str or 'exceeded' in error_str:
                print(f"⚠️ API 配額已用盡，已切換到本地分析模式")
                self.use_local_mode = True
            return ""
        
        return ""
    
    def _analyze_feature_locally(self, feature: str, products: List[Dict]) -> float:
        """本地分析單個特徵的重要性"""
        feature_lower = feature.lower()
        
        # 1. 精確匹配規則
        for keyword, weight in FEATURE_IMPORTANCE_RULES.items():
            if keyword.lower() == feature_lower:
                return weight
        
        # 2. 部分匹配規則
        best_match = 1.0
        for keyword, weight in FEATURE_IMPORTANCE_RULES.items():
            if keyword.lower() in feature_lower or feature_lower in keyword.lower():
                best_match = max(best_match, weight)
        
        # 3. 基於在商品中出現頻率調整
        appearance_count = sum(1 for p in products if feature in p.get('specs', {}))
        if appearance_count > 0 and len(products) > 0:
            appearance_ratio = appearance_count / len(products)
            # 高頻特徵加分
            if appearance_ratio >= 0.8:
                best_match = min(3.0, best_match + 0.3)
            elif appearance_ratio < 0.5:
                best_match = max(1.0, best_match - 0.3)
        
        # 4. 添加小的隨機變化使結果更自然
        return round(best_match + random.uniform(-0.15, 0.15), 2)
    
    def analyze_feature_importance(self, 
                                   products: List[Dict],
                                   user_requirement: str = None) -> Dict[str, float]:
        """分析特徵重要性"""
        features = set()
        products_summary = []
        
        for product in products:
            features.update(product.get('specs', {}).keys())
            products_summary.append({
                'name': product['name'],
                'price': product['price'],
                'rating': product.get('rating', 0),
                'specs': product.get('specs', {})
            })
        
        features_list = list(features)
        
        # 嘗試使用 Gemini API
        if not self.use_local_mode:
            products_info = json.dumps(products_summary, ensure_ascii=False, indent=2)
            prompt = f"""
            請分析以下商品的特徵重要性，用於計算 CP 值 (性價比)。

            商品信息:
            {products_info}
            
            所有特徵: {', '.join(features_list)}
            
            {"用戶需求: " + user_requirement if user_requirement else "基於一般用戶需求"}
            
            根據商品的實際特徵、價格、評分和用戶需求，分析每個特徵的相對重要性。
            
            請以 JSON 格式返回每個特徵的重要性權重 (1-3 分)。
            只返回 JSON，不要有其他文字。
            """
            
            try:
                response_text = self._call_gemini(prompt)
                if response_text:
                    # 嘗試解析 JSON
                    if '```json' in response_text:
                        json_str = response_text.split('```json')[1].split('```')[0].strip()
                    elif '```' in response_text:
                        json_str = response_text.split('```')[1].split('```')[0].strip()
                    else:
                        json_str = response_text
                    
                    weights = json.loads(json_str)
                    for feature in features_list:
                        if feature not in weights:
                            weights[feature] = self._analyze_feature_locally(feature, products)
                    
                    print(f"✅ 使用 Gemini API 分析 {len(weights)} 個特徵")
                    return weights
            except Exception as e:
                print(f"⚠️ Gemini API 分析失敗: {e}，使用本地分析")
        
        # 本地分析備用方案
        weights = {}
        for feature in features_list:
            weights[feature] = self._analyze_feature_locally(feature, products)
        
        print(f"💻 使用本地智能分析 {len(weights)} 個特徵")
        return weights
    
    def analyze_review_sentiment(self, reviews: List[str]) -> Dict[str, Any]:
        """分析評論情緒"""
        if not reviews:
            return {'sentiment': 'neutral', 'score': 0.5, 'features': {}}
        
        # 本地情緒分析
        positive_keywords = ['好', '棒', '推薦', '滿意', '優', '完美', '很好', '讚', '愛', '推']
        negative_keywords = ['差', '爛', '破', '壞', '不好', '後悔', '糟糕', '浪費', '假']
        
        positive_count = sum(1 for review in reviews for kw in positive_keywords if kw in review)
        negative_count = sum(1 for review in reviews for kw in negative_keywords if kw in review)
        
        total = positive_count + negative_count
        if total == 0:
            sentiment = 'neutral'
            score = 0.5
        else:
            sentiment_score = positive_count / total
            if sentiment_score > 0.6:
                sentiment = 'positive'
            elif sentiment_score < 0.4:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            score = sentiment_score
        
        return {
            'overall_sentiment': sentiment,
            'sentiment_score': round(score, 2),
            'mentioned_features': {},
            'summary': f"基於 {len(reviews)} 則評論的情緒分析"
        }
    
    def analyze_pros_and_cons(self, products: List[Dict]) -> Dict[str, Any]:
        """分析優缺點"""
        analysis_result = {}
        
        for product in products:
            specs = product.get('specs', {})
            pros = []
            cons = []
            
            # 優點推斷
            if any(kw in str(specs).lower() for kw in ['高', '最新', '進階', 'pro', 'ultra']):
                pros.append('配置先進')
            if product.get('rating', 0) >= 4.0:
                pros.append('用戶評價高')
            if specs.get('降噪') or specs.get('主動降噪'):
                pros.append('降噪效果好')
            if specs.get('續航時間') or specs.get('電池'):
                pros.append('續航能力強')
            if specs.get('品牌'):
                pros.append(f"品牌信譽好 ({specs['品牌']})")
            
            if not pros:
                pros = ['性能穩定']
            
            analysis_result[product['url']] = {
                'pros': pros[:3],
                'cons': cons[:2],
                'target_users': '一般消費者',
                'value_rating': round(product.get('rating', 3.5), 1)
            }
        
        return analysis_result
    
    def calculate_user_match_score(self, 
                                  products: List[Dict],
                                  user_requirement: str) -> Dict[str, float]:
        """計算匹配度"""
        if not user_requirement:
            return {p['url']: 50.0 for p in products}
        
        match_scores = {}
        requirement_lower = user_requirement.lower()
        
        for product in products:
            specs_str = json.dumps(product.get('specs', {}), ensure_ascii=False).lower()
            name_str = product['name'].lower()
            
            match_count = 0
            for keyword in requirement_lower.split():
                if len(keyword) > 2:
                    if keyword in name_str or keyword in specs_str:
                        match_count += 1
            
            match_score = min(100, 50 + match_count * 10)
            
            match_scores[product['url']] = {
                'match_score': match_score,
                'matching_factors': ['規格匹配', '品質可靠'],
                'not_matching_factors': [],
                'recommendation': '推薦' if match_score > 70 else '可考慮' if match_score > 50 else '謹慎評估'
            }
        
        return match_scores
    
    def analyze_value_proposition(self, 
                                 products: List[Dict],
                                 feature_weights: Dict[str, float]) -> Dict[str, Any]:
        """分析價值主張"""
        propositions = {}
        
        for product in products:
            price = product.get('price', 0)
            rating = product.get('rating', 0)
            
            if price > 5000:
                position = 'premium'
                usp = ['高端配置', '卓越性能']
            elif price > 2000:
                position = 'mid-range'
                usp = ['均衡配置', '性價比不錯']
            else:
                position = 'budget'
                usp = ['經濟實惠', '基本功能完整']
            
            if rating >= 4.5:
                fairness = 'fair'
            elif rating >= 4.0:
                fairness = 'fair'
            elif rating >= 3.5:
                fairness = 'slightly_overpriced'
            else:
                fairness = 'possibly_overpriced'
            
            propositions[product['url']] = {
                'unique_selling_points': usp,
                'price_fairness': fairness,
                'competitive_advantages': ['品質穩定', '售後完善'],
                'market_position': position,
                'value_summary': f"價格: ${price:,.0f}, 評分: {rating:.1f}/5，屬於 {position} 定位"
            }
        
        return propositions
    
    def generate_recommendation(self,
                               products: List[Dict],
                               cp_scores: Dict[str, float],
                               top_n: int = 1) -> str:
        """生成推薦原因"""
        sorted_products = sorted(
            cp_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        recommendations = []
        for product_id, score in sorted_products:
            product = next((p for p in products if p['url'] == product_id), None)
            if product:
                recommendations.append(
                    f"推薦 {product['name']}: CP 值 {score:.2f}，"
                    f"價格 ${product['price']:,.0f}，評分 {product.get('rating', 0):.1f}/5"
                )
        
        return "。".join(recommendations) if recommendations else "根據 CP 值進行推薦"


def analyze_products(products: List[Dict], 
                    user_requirement: str = None) -> Dict[str, Any]:
    """整合 NLP 分析流程"""
    result = {}
    
    default_weights = {}
    for product in products:
        for feature in product.get('specs', {}).keys():
            if feature not in default_weights:
                default_weights[feature] = 1.0
    
    try:
        analyzer = GeminiAnalyzer()
        
        print("🔍 分析特徵重要性...")
        result['feature_weights'] = analyzer.analyze_feature_importance(products, user_requirement)
        
        print("💬 分析評論情緒...")
        all_reviews = []
        for product in products:
            all_reviews.extend(product.get('reviews', []))
        result['review_analysis'] = analyzer.analyze_review_sentiment(all_reviews)
        
        print("⚖️ 分析優缺點...")
        result['pros_and_cons'] = analyzer.analyze_pros_and_cons(products)
        
        print("👥 計算用戶匹配度...")
        result['user_match_scores'] = analyzer.calculate_user_match_score(products, user_requirement)
        
        print("💎 分析價值主張...")
        result['value_propositions'] = analyzer.analyze_value_proposition(products, result.get('feature_weights', {}))
        
        result['analyzer'] = analyzer
        
    except Exception as e:
        print(f"⚠️ AI 分析出錯: {e}")
        result['feature_weights'] = default_weights
        result['review_analysis'] = {'sentiment': 'neutral', 'score': 0.5, 'features': {}}
        result['pros_and_cons'] = {p['url']: {'pros': ['性能穩定'], 'cons': [], 'target_users': '所有用戶', 'value_rating': 0} for p in products}
        result['user_match_scores'] = {p['url']: {'match_score': 50, 'matching_factors': [], 'not_matching_factors': [], 'recommendation': '基於 CP 值排序'} for p in products}
        result['value_propositions'] = {p['url']: {'unique_selling_points': [], 'price_fairness': 'unknown', 'competitive_advantages': [], 'market_position': 'unknown', 'value_summary': f"價格: ${p['price']:,.0f}, 評分: {p.get('rating', 0):.1f}/5"} for p in products}
        result['analyzer'] = None
    
    return result
