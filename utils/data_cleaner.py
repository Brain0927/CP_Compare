"""
資料清洗與標準化模組
"""
import re
from typing import Dict, List, Any


class DataCleaner:
    """資料清洗與標準化"""
    
    # 單位轉換對應表
    UNIT_CONVERSIONS = {
        # 容量轉 GB
        'GB': 1,
        'TB': 1024,
        'MB': 0.001,
        # 重量轉 kg
        'kg': 1,
        'g': 0.001,
        'lbs': 0.453592,
    }
    
    # 特徵名稱標準化
    FEATURE_MAPPING = {
        '處理器': 'CPU',
        'processor': 'CPU',
        'cpu': 'CPU',
        '記憶體': 'RAM',
        'memory': 'RAM',
        'ram': 'RAM',
        '儲存': 'Storage',
        'storage': 'Storage',
        '螢幕': 'Screen',
        'display': 'Screen',
        '電池': 'Battery',
        'battery': 'Battery',
        '重量': 'Weight',
        'weight': 'Weight',
        '品牌': 'Brand',
        'brand': 'Brand',
        '型號': 'Model',
        'model': 'Model',
    }
    
    @staticmethod
    def normalize_value(value: str) -> str:
        """清洗文字值"""
        if not isinstance(value, str):
            return str(value)
        
        # 移除多餘空格
        value = ' '.join(value.split())
        # 移除特殊字元（保留數字、字母、中文）
        value = re.sub(r'[^\w\s\u4e00-\u9fff\.\-]', '', value)
        
        return value.strip()
    
    @staticmethod
    def extract_numeric(value: str) -> float:
        """從文字中提取數值"""
        if isinstance(value, (int, float)):
            return float(value)
        
        # 提取數字部分
        numbers = re.findall(r'\d+\.?\d*', str(value))
        
        if numbers:
            return float(numbers[0])
        
        return 0.0
    
    @staticmethod
    def normalize_unit(value: str, target_unit: str = None) -> Dict[str, Any]:
        """
        標準化單位
        
        Returns:
            {'value': float, 'unit': str, 'normalized_value': float}
        """
        value_str = str(value).upper()
        numeric_value = DataCleaner.extract_numeric(value_str)
        
        # 偵測單位
        detected_unit = None
        for unit in DataCleaner.UNIT_CONVERSIONS.keys():
            if unit.upper() in value_str:
                detected_unit = unit.upper()
                break
        
        normalized_value = numeric_value
        if detected_unit and target_unit:
            conversion_factor = DataCleaner.UNIT_CONVERSIONS.get(detected_unit, 1) / \
                               DataCleaner.UNIT_CONVERSIONS.get(target_unit.upper(), 1)
            normalized_value = numeric_value * conversion_factor
        
        return {
            'value': numeric_value,
            'unit': detected_unit or 'unknown',
            'normalized_value': normalized_value
        }
    
    @staticmethod
    def normalize_feature_name(feature_name: str) -> str:
        """標準化特徵名稱"""
        feature_name = feature_name.lower().strip()
        
        # 查找對應的標準名稱
        for key, value in DataCleaner.FEATURE_MAPPING.items():
            if key.lower() in feature_name:
                return value
        
        return feature_name
    
    @staticmethod
    def clean_product(product: Dict[str, Any]) -> Dict[str, Any]:
        """
        清洗整個商品資訊
        
        Args:
            product: 原始商品資訊
        
        Returns:
            dict: 清洗後的商品資訊
        """
        cleaned = {
            'url': product.get('url', ''),
            'name': DataCleaner.normalize_value(product.get('name', '')),
            'price': DataCleaner.extract_numeric(product.get('price', 0)),
            'specs': {},
            'reviews': product.get('reviews', []),
            'rating': DataCleaner.extract_numeric(product.get('rating', 0)),
        }
        
        # 清洗規格
        for key, value in product.get('specs', {}).items():
            clean_key = DataCleaner.normalize_feature_name(key)
            clean_value = DataCleaner.normalize_value(value)
            cleaned['specs'][clean_key] = clean_value
        
        return cleaned
    
    @staticmethod
    def clean_products(products: List[Dict]) -> List[Dict]:
        """批次清洗商品資訊"""
        return [DataCleaner.clean_product(p) for p in products]
    
    @staticmethod
    def extract_common_features(products: List[Dict]) -> Dict[str, List]:
        """
        提取所有商品共通的特徵
        
        Returns:
            {'feature_name': ['value1', 'value2', ...], ...}
        """
        if not products:
            return {}
        
        # 收集所有特徵
        all_features = {}
        for product in products:
            for feature, value in product.get('specs', {}).items():
                if feature not in all_features:
                    all_features[feature] = []
                all_features[feature].append(value)
        
        # 篩選共通特徵（至少 80% 的商品都有）
        threshold = len(products) * 0.8
        common_features = {
            k: v for k, v in all_features.items() 
            if len(v) >= threshold
        }
        
        return common_features
