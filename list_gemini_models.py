#!/usr/bin/env python3
"""
列出可用的 Gemini 模型
"""
import sys
sys.path.insert(0, '/home/brain/CP_Compare')

import google.generativeai as genai
from config.settings import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

print("可用的 Gemini 模型:")
print("=" * 80)

try:
    for model in genai.list_models():
        print(f"\n📱 模型: {model.name}")
        print(f"   版本: {model.version}")
        print(f"   支援方法: {model.supported_generation_methods}")
        if hasattr(model, 'display_name'):
            print(f"   顯示名稱: {model.display_name}")
except Exception as e:
    print(f"❌ 列出模型失敗: {e}")
