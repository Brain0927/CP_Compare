"""
CP 值計算模組
"""
from typing import Dict, List, Any
import pandas as pd
from utils.data_cleaner import DataCleaner


class CPCalculator:
    """CP 值 (性價比) 計算"""
    
    @staticmethod
    def calculate_feature_score(value: str, max_value: float, is_numeric: bool = True) -> float:
        """
        計算單一特徵的分數 (0-1)
        
        Args:
            value: 特徵值
            max_value: 該特徵的最大值（用於歸一化）
            is_numeric: 是否為數值類型
        
        Returns:
            float: 分數 0-1
        """
        if not is_numeric or max_value == 0:
            return 0.5  # 非數值特徵預設 0.5
        
        numeric_value = DataCleaner.extract_numeric(value)
        
        # 歸一化到 0-1
        if max_value > 0:
            score = numeric_value / max_value
        else:
            score = 0
        
        return min(max(score, 0), 1)  # 限制在 0-1 之間
    
    @staticmethod
    def calculate_cp_value(product: Dict[str, Any],
                          feature_weights: Dict[str, float],
                          common_features: Dict[str, List]) -> float:
        """
        計算單一商品的 CP 值
        
        公式: CP = Σ(Feature_Score × Weight) / Price
        
        Args:
            product: 商品資訊
            feature_weights: 特徵權重字典 {feature: weight}
            common_features: 共通特徵與所有值 {feature: [values]}
        
        Returns:
            float: CP 值 (越高越好)
        """
        if product['price'] <= 0:
            return 0
        
        # 計算加權特徵分數
        weighted_score = 0
        total_weight = 0
        
        for feature, weight in feature_weights.items():
            if feature not in product['specs']:
                continue
            
            # 計算該特徵的分數
            feature_value = product['specs'][feature]
            
            # 找該特徵的最大值
            if feature in common_features:
                max_value = max([
                    DataCleaner.extract_numeric(v) 
                    for v in common_features[feature]
                ])
            else:
                max_value = DataCleaner.extract_numeric(feature_value)
            
            # 計算特徵分數
            feature_score = CPCalculator.calculate_feature_score(
                feature_value, 
                max_value,
                is_numeric=True
            )
            
            # 加入加權
            weighted_score += feature_score * weight
            total_weight += weight
        
        # 避免除以零
        if total_weight == 0:
            total_weight = 1
        
        # 計算 CP 值 (考慮評分加成)
        base_cp = (weighted_score / total_weight) / (product['price'] / 1000)
        
        # 評分加成 (評分越高加成越多)
        rating_bonus = 1 + (product.get('rating', 0) / 5.0) * 0.2
        
        final_cp = base_cp * rating_bonus
        
        return round(final_cp, 4)
    
    @staticmethod
    def calculate_all_cp_values(products: List[Dict],
                               feature_weights: Dict[str, float]) -> Dict[str, float]:
        """
        計算所有商品的 CP 值
        
        Returns:
            {product_url: cp_value, ...}
        """
        # 提取共通特徵
        common_features = DataCleaner.extract_common_features(products)
        
        cp_values = {}
        
        for product in products:
            cp_value = CPCalculator.calculate_cp_value(
                product,
                feature_weights,
                common_features
            )
            cp_values[product['url']] = cp_value
        
        return cp_values
    
    @staticmethod
    def create_comparison_dataframe(products: List[Dict],
                                   feature_weights: Dict[str, float],
                                   cp_values: Dict[str, float]) -> pd.DataFrame:
        """
        建立比較表格
        
        Returns:
            DataFrame with columns: 商品名稱, 價格, CP值, [各特徵]...
        """
        data = []
        
        for product in products:
            row = {
                '商品名稱': product['name'][:40],
                '價格': f"${product['price']:,.0f}",
                'CP值': cp_values.get(product['url'], 0),
                '評分': product.get('rating', 0),
            }
            
            # 加入各特徵
            for feature in feature_weights.keys():
                if feature in product['specs']:
                    row[feature] = product['specs'][feature]
                else:
                    row[feature] = 'N/A'
            
            data.append(row)
        
        df = pd.DataFrame(data)
        # 按 CP 值排序 (降序)
        df = df.sort_values('CP值', ascending=False).reset_index(drop=True)
        
        return df
    
    @staticmethod
    def get_recommendation_ranking(products: List[Dict],
                                  feature_weights: Dict[str, float],
                                  cp_values: Dict[str, float],
                                  top_n: int = 3) -> List[Dict]:
        """
        獲得推薦排名
        
        Returns:
            [{
                'rank': 1,
                'name': '商品名稱',
                'cp_value': xx.xx,
                'price': xxxx,
                'reason': '推薦原因'
            }, ...]
        """
        # 排序商品
        sorted_products = sorted(
            [(p, cp_values.get(p['url'], 0)) for p in products],
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        recommendations = []
        for rank, (product, cp_value) in enumerate(sorted_products, 1):
            recommendation = {
                'rank': rank,
                'name': product['name'],
                'cp_value': cp_value,
                'price': product['price'],
                'rating': product.get('rating', 0),
                'specs': product['specs'],
                'url': product['url']
            }
            recommendations.append(recommendation)
        
        return recommendations
    
    @staticmethod
    def calculate_score_breakdown(product: Dict[str, Any],
                                 feature_weights: Dict[str, float],
                                 common_features: Dict[str, List]) -> Dict[str, float]:
        """
        計算每個特徵的詳細分數
        
        Returns:
            {feature: score, ...}
        """
        breakdown = {}
        
        for feature, weight in feature_weights.items():
            if feature not in product['specs']:
                breakdown[feature] = 0
                continue
            
            feature_value = product['specs'][feature]
            
            if feature in common_features:
                max_value = max([
                    DataCleaner.extract_numeric(v) 
                    for v in common_features[feature]
                ])
            else:
                max_value = DataCleaner.extract_numeric(feature_value)
            
            feature_score = CPCalculator.calculate_feature_score(
                feature_value, 
                max_value,
                is_numeric=True
            )
            
            breakdown[feature] = feature_score * weight
        
        return breakdown
    
    @staticmethod
    def get_budget_recommendations(products: List[Dict],
                                  feature_weights: Dict[str, float],
                                  budget: float) -> List[Dict]:
        """
        根據預算進行推薦
        
        Args:
            budget: 預算上限
            
        Returns:
            適合預算的商品列表 (按 CP 值排序)
        """
        # 篩選符合預算的商品
        affordable = [p for p in products if p['price'] <= budget]
        
        if not affordable:
            return []
        
        # 計算 CP 值
        common_features = DataCleaner.extract_common_features(affordable)
        cp_values = {}
        
        for product in affordable:
            cp = CPCalculator.calculate_cp_value(
                product,
                feature_weights,
                common_features
            )
            cp_values[product['url']] = cp
        
        # 排序
        sorted_products = sorted(
            [(p, cp_values.get(p['url'], 0)) for p in affordable],
            key=lambda x: x[1],
            reverse=True
        )
        
        return [{'product': p, 'cp_value': cp} for p, cp in sorted_products]
    
    @staticmethod
    def get_price_performance_stats(products: List[Dict],
                                   cp_values: Dict[str, float]) -> Dict[str, Any]:
        """
        計算性價比統計數據
        
        Returns:
            {
                'avg_price': xxx,
                'avg_cp': xxx,
                'best_value': {...},
                'most_expensive': {...},
                'cheapest': {...}
            }
        """
        if not products:
            return {}
        
        prices = [p['price'] for p in products]
        cp_vals = list(cp_values.values())
        
        best_value_product = max(products, key=lambda p: cp_values.get(p['url'], 0))
        most_expensive = max(products, key=lambda p: p['price'])
        cheapest = min(products, key=lambda p: p['price'])
        
        return {
            'avg_price': sum(prices) / len(prices),
            'avg_cp': sum(cp_vals) / len(cp_vals),
            'price_range': (min(prices), max(prices)),
            'best_value': {
                'name': best_value_product['name'],
                'cp': cp_values.get(best_value_product['url'], 0),
                'price': best_value_product['price']
            },
            'most_expensive': {
                'name': most_expensive['name'],
                'price': most_expensive['price']
            },
            'cheapest': {
                'name': cheapest['name'],
                'price': cheapest['price']
            }
        }
