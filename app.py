"""
AI CP 值比較器 - Streamlit 主應用程式
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from typing import List, Dict
import time
from datetime import datetime
import os

# 設置頁面配置（必須在最前面）
st.set_page_config(
    page_title="AI CP值比較器",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 在這裡確保從 Streamlit Secrets 讀取 API Key
try:
    if "GEMINI_API_KEY" in st.secrets:
        os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# 導入自定義模組（此時環境變數已設置）
from utils.scraper import scrape_products
from utils.data_cleaner import DataCleaner
from utils.nlp_analyzer import analyze_products, GeminiAnalyzer
from utils.cp_calculator import CPCalculator
from utils.similar_finder import SimilarProductFinder
from config.settings import GEMINI_API_KEY

# 自定義 CSS - 購物車風格
st.markdown("""
    <style>
    /* 全局樣式 */
    * {
        margin: 0;
        padding: 0;
    }
    
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* 標題樣式 */
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px 20px;
        border-radius: 15px;
        margin-bottom: 30px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    
    .header-container h1 {
        font-size: 2.5em;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .header-container p {
        font-size: 1.1em;
        opacity: 0.9;
    }
    
    /* 購物車卡片 */
    .product-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }
    
    .product-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .product-card-title {
        font-size: 1.3em;
        font-weight: bold;
        color: #333;
        margin-bottom: 10px;
    }
    
    /* 價格標籤 */
    .price-tag {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.2em;
        display: inline-block;
    }
    
    .cp-value {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 10px 15px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.2em;
        display: inline-block;
    }
    
    .rating-tag {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-weight: bold;
        display: inline-block;
    }
    
    /* 推薦商品（購物車風格）*/
    .recommendation-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #ff6b6b;
        margin: 20px 0;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.2);
    }
    
    .recommendation-box h3 {
        color: #d32f2f;
        margin-bottom: 15px;
        font-size: 1.4em;
    }
    
    /* 步驟指示器 */
    .step-indicator {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 25px;
        border-radius: 10px;
        margin: 15px 0;
        font-weight: bold;
        font-size: 1.1em;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* 按鈕樣式 */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 30px !important;
        font-weight: bold !important;
        font-size: 1em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 8px 24px rgba(102, 126, 234, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    /* 表格樣式 */
    .dataframe {
        background: white !important;
        border-radius: 10px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* 指標卡片 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* 成功提示 */
    .stSuccess {
        background: linear-gradient(135deg, #00b894 0%, #00d2d3 100%) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(0, 185, 148, 0.2) !important;
    }
    
    /* 信息提示 */
    .stInfo {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(79, 172, 254, 0.2) !important;
    }
    
    /* 警告提示 */
    .stWarning {
        background: linear-gradient(135deg, #ffa502 0%, #ffcd3b 100%) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(255, 165, 2, 0.2) !important;
    }
    
    /* 錯誤提示 */
    .stError {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(255, 107, 107, 0.2) !important;
    }
    
    /* Tabs 樣式 */
    .stTabs [data-baseweb="tab-list"] button {
        background: white !important;
        border-radius: 10px 10px 0 0 !important;
        border: 1px solid #e0e0e0 !important;
        margin-right: 5px !important;
    }
    
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
    }
    
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """初始化 session state"""
    if 'products' not in st.session_state:
        st.session_state.products = None
    if 'cleaned_products' not in st.session_state:
        st.session_state.cleaned_products = None
    if 'scraping_complete' not in st.session_state:
        st.session_state.scraping_complete = False
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'feature_weights' not in st.session_state:
        st.session_state.feature_weights = None
    if 'cp_values' not in st.session_state:
        st.session_state.cp_values = None
    if 'nlp_analysis' not in st.session_state:
        st.session_state.nlp_analysis = None
    if 'comparison_list' not in st.session_state:
        st.session_state.comparison_list = []  # 比較清單


def render_header():
    """渲染標題區塊 - 購物車風格"""
    st.markdown("""
    <div class="header-container">
        <h1>🛒 智慧商品比價器</h1>
        <p>🤖 AI 驅動的 CP 值分析 | 📊 精準數據比較 | 🏆 推薦最佳選擇</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 功能說明卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2em; margin-bottom: 10px;">🕷️</div>
            <div><strong>自動爬蟲</strong></div>
            <div style="font-size: 0.9em;">快速獲取商品資訊</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2em; margin-bottom: 10px;">🧠</div>
            <div><strong>AI 分析</strong></div>
            <div style="font-size: 0.9em;">智慧特徵識別</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2em; margin-bottom: 10px;">📊</div>
            <div><strong>CP 計算</strong></div>
            <div style="font-size: 0.9em;">科學價值評估</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div style="font-size: 2em; margin-bottom: 10px;">🏆</div>
            <div><strong>推薦結果</strong></div>
            <div style="font-size: 0.9em;">最佳選擇推薦</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")


def render_input_section():
    """渲染輸入區塊 - 購物車風格"""
    st.markdown('<div class="step-indicator">📌 第一步：輸入商品連結（請貼上要比較的商品網址）</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        urls_text = st.text_area(
            "請在下方輸入要比較的商品連結：",
            height=120,
            placeholder="https://example.com/product1\nhttps://example.com/product2\nhttps://example.com/product3\n\n💡 支援 2-4 個商品比較",
            key="urls_input"
        )
    
    with col2:
        st.markdown("<h4 style='text-align: center; margin-top: 25px;'>⚙️ 爬蟲設定</h4>", unsafe_allow_html=True)
        is_dynamic = st.checkbox(
            "🔄 動態載入",
            value=False,
            help="如果頁面需要 JavaScript 渲染才能顯示內容，請勾選此選項"
        )
        st.markdown("")
        submit_button = st.button(
            "🕷️ 開始爬取商品",
            key="scrape_btn",
            use_container_width=True,
            type="primary"
        )
    
    return urls_text, is_dynamic, submit_button


def render_product_display():
    """渲染商品資訊展示"""
    if st.session_state.cleaned_products is None:
        st.info("⏳ 等待爬取商品資訊...")
        return
    
    st.markdown("### 📦 第二步：商品資訊預覽")
    
    # 建立表格
    products = st.session_state.cleaned_products
    
    display_data = []
    for i, product in enumerate(products, 1):
        display_data.append({
            '序號': i,
            '商品名稱': product['name'][:40],
            '價格': f"${product['price']:,.0f}",
            '評分': f"{product['rating']:.1f}⭐" if product['rating'] > 0 else "N/A",
            '特徵數': len(product['specs'])
        })
    
    st.dataframe(
        pd.DataFrame(display_data),
        use_container_width=True,
        hide_index=True
    )
    
    # 展開詳細資訊
    with st.expander("🔍 查看詳細規格"):
        for i, product in enumerate(products, 1):
            with st.container():
                st.markdown(f"#### {i}. {product['name']}")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown(f"**價格**: <span class='price-tag'>${product['price']:,.0f}</span>", unsafe_allow_html=True)
                with col2:
                    st.markdown(f"**評分**: {product['rating']:.1f}⭐" if product['rating'] > 0 else "N/A")
                with col3:
                    st.markdown(f"**評論**: {len(product['reviews'])} 則")
                
                # 規格表
                specs_df = pd.DataFrame([
                    {'特徵': k, '值': v} 
                    for k, v in product['specs'].items()
                ])
                
                st.dataframe(specs_df, use_container_width=True, hide_index=True)
                
                # 評論預覽
                if product['reviews']:
                    st.markdown("**評論預覽**:")
                    for review in product['reviews'][:2]:
                        st.caption(f"💬 {review[:100]}...")


def render_weight_adjustment():
    """渲染權重調整區塊"""
    if st.session_state.feature_weights is None or not st.session_state.feature_weights:
        st.info("⏳ 等待 NLP 分析特徵重要性...")
        # 返回預設權重避免後續錯誤
        if st.session_state.cleaned_products:
            default_weights = {}
            for product in st.session_state.cleaned_products:
                for feature in product.get('specs', {}).keys():
                    if feature not in default_weights:
                        default_weights[feature] = 1.0
            return default_weights
        return {}
    
    st.markdown("### ⚖️ 第三步：調整特徵權重")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("**自動分析的特徵重要性** (1-3 分)：")
        
        # 建立權重調整 slider
        adjusted_weights = {}
        
        for feature, weight in sorted(
            st.session_state.feature_weights.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            adjusted_weights[feature] = st.slider(
                f"**{feature}** (原始: {weight:.1f})",
                min_value=1.0,
                max_value=3.0,
                value=weight,
                step=0.1,
                key=f"weight_{feature}"
            )
    
    with col2:
        st.markdown("**權重說明**:")
        st.markdown("""
        - **1 分**: 不重要
        - **2 分**: 中等重要
        - **3 分**: 非常重要
        
        可手動調整以符合個人偏好。
        """)
    
    # 保存調整後的權重
    st.session_state.feature_weights = adjusted_weights
    
    return adjusted_weights


def render_comparison_results(feature_weights: Dict):
    """渲染比較結果"""
    st.markdown("### 📊 第四步：CP 值比較結果")
    
    # 檢查 feature_weights 是否有效
    if not feature_weights or not isinstance(feature_weights, dict):
        st.error("❌ 特徵權重無效，無法計算 CP 值")
        return None
    
    # 計算 CP 值
    products = st.session_state.cleaned_products
    
    with st.spinner("🔄 計算 CP 值中..."):
        cp_values = CPCalculator.calculate_all_cp_values(products, feature_weights)
        st.session_state.cp_values = cp_values
    
    # 建立比較表格
    comparison_df = CPCalculator.create_comparison_dataframe(
        products,
        feature_weights,
        cp_values
    )
    
    # === 標籤切換 ===
    comp_tab1, comp_tab2, comp_tab3, comp_tab4 = st.tabs(
        ["📋 比較表格", "📊 CP 值排行", "💡 詳細分析", "🎯 統計數據"]
    )
    
    with comp_tab1:
        st.markdown("#### 商品對比表")
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=False
        )
    
    # === 第二個標籤：CP 值排行榜 ===
    with comp_tab2:
        st.markdown("#### CP 值排行榜")
        
        # 找出最佳商品
        best_product_idx = max(range(len(products)), key=lambda i: cp_values.get(products[i]['url'], 0))
        best_product = products[best_product_idx]
        best_cp = cp_values.get(best_product['url'], 0)
        
        # 顯示最佳商品信息 - 加強視覺效果
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); 
                    padding: 25px; border-radius: 10px; border: 3px solid #FF8C00;">
            <div style="text-align: center; color: white; font-weight: bold;">
                <h2 style="margin: 0; font-size: 28px;">🏆 最佳 CP 值商品 🏆</h2>
                <p style="margin: 10px 0 0 0; font-size: 20px;">{best_product['name'][:60]}</p>
                <p style="margin: 5px 0; font-size: 24px; color: #FFE4B5;">
                    ⭐ CP 值: <span style="font-size: 32px;">{best_cp:.2f}</span>
                </p>
                <hr style="border: 1px solid white; margin: 10px 0;">
                <div style="display: flex; justify-content: space-around; font-size: 16px;">
                    <div>💰 <strong>${best_product['price']:,.0f}</strong></div>
                    <div>⭐ <strong>{best_product.get('rating', 0):.1f}/5</strong></div>
                    <div>📊 <strong>{len(best_product.get('specs', {}))} 特徵</strong></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**推薦理由:** 這個商品在同類商品中提供了最高的價值比。")
        
        st.markdown("---")
        
        # CP 值排行圖表
        fig, ax = plt.subplots(figsize=(12, 7))
        
        product_names = [p['name'][:25] for p in products]
        cp_vals = [cp_values.get(p['url'], 0) for p in products]
        
        # 根據排名設置顏色
        colors = []
        for i in range(len(cp_vals)):
            if i == best_product_idx:
                colors.append('#FFD700')  # 金色 - 最佳
            elif cp_vals[i] == sorted(cp_vals, reverse=True)[1]:
                colors.append('#C0C0C0')  # 銀色 - 次佳
            elif cp_vals[i] == sorted(cp_vals, reverse=True)[2] if len(cp_vals) > 2 else False:
                colors.append('#CD7F32')  # 銅色 - 第三
            else:
                colors.append('#a5d6ff')  # 藍色 - 其他
        
        bars = ax.barh(product_names, cp_vals, color=colors, edgecolor='black', linewidth=2)
        
        # 在柱子上顯示數值和排名標記
        for i, (bar, val) in enumerate(zip(bars, cp_vals)):
            label = f'{val:.2f}'
            if i == best_product_idx:
                label += ' 🏆'
            ax.text(val + 0.01, i, label, va='center', fontweight='bold', fontsize=11)
        
        ax.set_xlabel('CP 值 (越高越好)', fontsize=12, fontweight='bold')
        ax.set_title('商品 CP 值排行榜', fontsize=14, fontweight='bold')
        ax.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        st.pyplot(fig)
        
        # 顯示性價比分析圖
        st.markdown("#### 性價比分析（價格 vs CP 值）")
        
        st.write("💡 **說明:** X軸為價格，Y軸為CP值。右上方為最優選擇（高CP值低價格）")
        
        fig2, ax2 = plt.subplots(figsize=(11, 7))
        
        prices = [p['price'] for p in products]
        cp_vals = [cp_values.get(p['url'], 0) for p in products]
        
        # 散點顏色
        scatter_colors = [colors[i] for i in range(len(products))]
        scatter = ax2.scatter(prices, cp_vals, s=500, alpha=0.7, c=scatter_colors, edgecolors='black', linewidth=2)
        
        # 添加商品名稱和CP值標籤
        for i, name in enumerate(product_names):
            label = f"{name}\nCP:{cp_vals[i]:.2f}"
            if i == best_product_idx:
                ax2.annotate(label, (prices[i], cp_vals[i]), fontsize=10, ha='center', 
                            bbox=dict(boxstyle='round', facecolor='gold', alpha=0.7), fontweight='bold')
            else:
                ax2.annotate(label, (prices[i], cp_vals[i]), fontsize=9, ha='center')
        
        ax2.set_xlabel('價格 ($)', fontsize=12, fontweight='bold')
        ax2.set_ylabel('CP 值 (越高越好)', fontsize=12, fontweight='bold')
        ax2.set_title('性價比分析：價格 vs CP 值 (右上方最優)', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        # 添加象限線
        avg_price = sum(prices) / len(prices)
        avg_cp = sum(cp_vals) / len(cp_vals)
        ax2.axvline(avg_price, color='red', linestyle='--', alpha=0.3, label=f'平均價格: ${avg_price:,.0f}')
        ax2.axhline(avg_cp, color='green', linestyle='--', alpha=0.3, label=f'平均CP: {avg_cp:.2f}')
        ax2.legend()
        
        plt.tight_layout()
        st.pyplot(fig2)
    
    # === 第三個標籤：詳細分析 ===
    with comp_tab3:
        st.markdown("#### 詳細分數分解")
        
        # 計算共通特徵
        common_features = DataCleaner.extract_common_features(products)
        
        for i, product in enumerate(products, 1):
            with st.expander(f"📦 {product['name'][:50]} - CP 值: {cp_values.get(product['url'], 0):.2f}", expanded=(i==1)):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("💰 價格", f"${product['price']:,.0f}")
                
                with col2:
                    st.metric("⭐ 評分", f"{product.get('rating', 0):.1f}")
                
                with col3:
                    st.metric("🎯 CP 值", f"{cp_values.get(product['url'], 0):.2f}")
                
                with col4:
                    st.metric("📊 規格數", len(product['specs']))
                
                # 特徵分數分解
                breakdown = CPCalculator.calculate_score_breakdown(
                    product,
                    feature_weights,
                    common_features
                )
                
                st.markdown("**特徵分數分解:**")
                
                # 建立分數表
                score_data = []
                for feature, score in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
                    if score > 0:
                        score_data.append({
                            '特徵': feature,
                            '權重分數': f"{score:.3f}",
                            '原始值': product['specs'].get(feature, 'N/A')
                        })
                
                if score_data:
                    score_df = pd.DataFrame(score_data)
                    st.dataframe(score_df, use_container_width=True, hide_index=True)
                
                # 顯示計算公式
                st.markdown("**計算說明:**")
                st.caption(f"""
                CP 值計算: (加權特徵分數 / 總權重) / (價格/1000) × (1 + 評分/5 × 0.2)
                
                - 加權特徵分數: {sum(breakdown.values()):.3f}
                - 基礎 CP: {sum(breakdown.values()) / (sum(feature_weights.values()) or 1) / (product['price']/1000):.3f}
                - 評分加成: {1 + (product.get('rating', 0) / 5.0) * 0.2:.2f}x
                """)
    
    # === 第四個標籤：統計數據 ===
    with comp_tab4:
        st.markdown("#### 🎯 CP 值統計分析")
        
        cp_vals = [cp_values.get(p['url'], 0) for p in products]
        prices = [p['price'] for p in products]
        
        # 計算統計數據
        avg_cp = sum(cp_vals) / len(cp_vals) if cp_vals else 0
        max_cp = max(cp_vals) if cp_vals else 0
        min_cp = min(cp_vals) if cp_vals else 0
        
        avg_price = sum(prices) / len(prices) if prices else 0
        max_price = max(prices) if prices else 0
        min_price = min(prices) if prices else 0
        
        # 找到最佳 CP 值商品
        best_product_idx = max(range(len(products)), key=lambda i: cp_values.get(products[i]['url'], 0))
        best_value = cp_values.get(products[best_product_idx]['url'], 0)
        
        # 4 個指標卡
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📊 平均 CP 值",
                value=f"{avg_cp:.2f}",
                delta=f"最高: {max_cp:.2f}"
            )
        
        with col2:
            st.metric(
                label="💰 平均價格",
                value=f"${avg_price:,.0f}",
                delta=f"範圍: ${min_price:,.0f} - ${max_price:,.0f}"
            )
        
        with col3:
            st.metric(
                label="🏆 最佳 CP 值",
                value=f"{best_value:.2f}",
                delta=products[best_product_idx]['name'][:20] + "..."
            )
        
        with col4:
            cp_range = max_cp - min_cp
            st.metric(
                label="📈 CP 值差距",
                value=f"{cp_range:.2f}",
                delta=f"變異: {(cp_range/avg_cp*100):.1f}%" if avg_cp > 0 else "0%"
            )
        
        st.markdown("---")
        
        # 最佳性價比
        st.markdown("#### 🏆 推薦統計")
        
        col1, col2, col3 = st.columns(3)
        
        # 最佳性價比
        with col1:
            st.success(f"""
            **最佳性價比**
            
            📦 {products[best_product_idx]['name'][:40]}
            
            💰 ${prices[best_product_idx]:,.0f}
            
            🎯 CP: {best_value:.2f}
            """)
        
        # 最便宜
        cheapest_idx = min(range(len(products)), key=lambda i: prices[i])
        with col2:
            st.info(f"""
            **最便宜**
            
            📦 {products[cheapest_idx]['name'][:40]}
            
            💰 ${prices[cheapest_idx]:,.0f}
            
            ⭐ 評分: {products[cheapest_idx].get('rating', 0):.1f}
            """)
        
        # 最貴
        most_expensive_idx = max(range(len(products)), key=lambda i: prices[i])
        with col3:
            st.warning(f"""
            **最高價**
            
            📦 {products[most_expensive_idx]['name'][:40]}
            
            💰 ${prices[most_expensive_idx]:,.0f}
            
            🎯 CP: {cp_values.get(products[most_expensive_idx]['url'], 0):.2f}
            """)
        
        st.markdown("---")
        
        # 詳細統計表
        st.markdown("#### 📊 詳細商品統計")
        
        stats_data = []
        for i, product in enumerate(products):
            cp = cp_values.get(product['url'], 0)
            price = product['price']
            rating = product.get('rating', 0)
            
            # 計算排名
            rank = sorted(cp_vals, reverse=True).index(cp) + 1 if cp in cp_vals else len(cp_vals)
            
            # 計算性價比評級
            if cp >= max_cp * 0.9:
                rating_level = "🌟🌟🌟 優秀"
            elif cp >= max_cp * 0.75:
                rating_level = "🌟🌟 良好"
            elif cp >= max_cp * 0.6:
                rating_level = "🌟 一般"
            else:
                rating_level = "⭐ 不推薦"
            
            stats_data.append({
                "排名": f"#{rank}",
                "商品名稱": product['name'][:35],
                "價格": f"${price:,.0f}",
                "評分": f"{rating:.1f}/5",
                "CP 值": f"{cp:.2f}",
                "評級": rating_level
            })
        
        st.dataframe(
            stats_data,
            use_container_width=True,
            hide_index=True
        )
        
        st.markdown("---")
        
        # 預算建議
        st.markdown("#### 💡 根據預算的推薦")
        
        budget = st.slider(
            "選擇您的預算上限",
            min_value=int(min(prices)),
            max_value=int(max(prices)) + 1000,
            value=int(avg_price),
            step=100
        )
        
        budget_recs = CPCalculator.get_budget_recommendations(products, feature_weights, budget)
        
        if budget_recs:
            st.success(f"✅ 在 ${budget:,.0f} 預算內找到 {len(budget_recs)} 個商品:")
            
            for i, rec in enumerate(budget_recs, 1):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**{i}. {rec['product']['name'][:50]}**")
                        st.caption(f"💰 ${rec['product']['price']:,.0f} | 🎯 CP 值: {rec['cp_value']:.2f}")
                    
                    with col2:
                        if i == 1:
                            st.success("🥇 最推薦")
                        elif i == 2:
                            st.info("🥈 次選")
                        else:
                            st.warning("🥉 備選")
        else:
            st.error(f"❌ 未找到 ${budget:,.0f} 以內的商品")
    
    return comparison_df


def render_recommendation():
    """渲染推薦區塊"""
    st.markdown("### 🏆 第五步：推薦結果與原因")
    
    products = st.session_state.cleaned_products
    cp_values = st.session_state.cp_values
    
    if not products or not cp_values:
        st.warning("⏳ 請先完成比較步驟")
        return
    
    # 獲得推薦排名
    recommendations = CPCalculator.get_recommendation_ranking(
        products,
        st.session_state.feature_weights,
        cp_values,
        top_n=3
    )
    
    # 推薦標籤頁
    rec_tab1, rec_tab2, rec_tab3, rec_tab4 = st.tabs([
        "🤖 AI 推薦理由",
        "⚖️ 優缺點分析",
        "👥 用戶匹配度",
        "💎 價值主張"
    ])
    
    # === 標籤 1: AI 推薦理由 ===
    with rec_tab1:
        st.markdown("#### 推薦理由")
        
        try:
            nlp_analysis = st.session_state.get('nlp_analysis', {})
            if nlp_analysis and 'analyzer' in nlp_analysis:
                with st.spinner("✍️ 生成推薦理由中..."):
                    recommendation_text = nlp_analysis['analyzer'].generate_recommendation(
                        products,
                        cp_values,
                        top_n=3
                    )
                    st.markdown(recommendation_text)
            else:
                st.info("💡 AI 分析暫未進行，使用基礎推薦")
        except Exception as e:
            st.warning(f"⚠️ 無法生成 AI 推薦理由: {str(e)[:100]}")
        
        # 推薦排名卡片（始終顯示）
        st.markdown("#### 🎯 TOP 3 推薦排名")
        
        cols = st.columns(3)
        for i, (col, rec) in enumerate(zip(cols, recommendations)):
            with col:
                rank_emoji = ["🥇", "🥈", "🥉"][i]
                st.markdown(f"""
                <div style="border: 2px solid #51cf66; border-radius: 8px; padding: 15px; background-color: #f0f9ff;">
                    <h3 style="text-align: center; color: #51cf66;">{rank_emoji} 第 {rec['rank']} 名</h3>
                    <p><strong>{rec['name'][:30]}</strong></p>
                    <p>💰 價格: <strong>${rec['price']:,.0f}</strong></p>
                    <p style="font-size: 18px; font-weight: bold; color: #ff6b6b;">CP值: {rec['cp_value']:.2f}</p>
                    <p>⭐ 評分: {rec['rating']:.1f}/5</p>
                </div>
                """, unsafe_allow_html=True)
    
    # === 標籤 2: 優缺點分析 ===
    with rec_tab2:
        st.markdown("#### 詳細優缺點分析")
        
        nlp_analysis = st.session_state.get('nlp_analysis', {})
        pros_cons_available = 'pros_and_cons' in nlp_analysis and nlp_analysis.get('pros_and_cons')
        
        if pros_cons_available:
            analysis = st.session_state.nlp_analysis['pros_and_cons']
            
            for product in products:
                if product['url'] in analysis:
                    item_analysis = analysis[product['url']]
                    
                    with st.expander(f"📦 {product['name'][:50]}", expanded=False):
                        # 優點
                        if item_analysis.get('pros') and item_analysis['pros']:
                            st.success("**✅ 優點:**")
                            for pro in item_analysis['pros']:
                                st.write(f"• {pro}")
                        
                        # 缺點
                        if item_analysis.get('cons') and item_analysis['cons']:
                            st.error("**❌ 缺點:**")
                            for con in item_analysis['cons']:
                                st.write(f"• {con}")
                        
                        # 適用用戶
                        if item_analysis.get('target_users'):
                            st.info(f"**👥 適合用戶:** {item_analysis['target_users']}")
                        
                        # 價值評分
                        if 'value_rating' in item_analysis and item_analysis['value_rating']:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write("**價值評分:**")
                            with col2:
                                st.metric("", f"{item_analysis['value_rating']}/10")
        else:
            st.info("💡 優缺點分析暫未可用，使用基礎推薦結果")
    
    # === 標籤 3: 用戶匹配度 ===
    with rec_tab3:
        st.markdown("#### 用戶需求匹配度分析")
        
        nlp_analysis = st.session_state.get('nlp_analysis', {})
        match_scores_available = 'user_match_scores' in nlp_analysis and nlp_analysis.get('user_match_scores')
        
        if match_scores_available:
            match_scores = st.session_state.nlp_analysis['user_match_scores']
            
            # 繪製匹配度圖表
            match_data = []
            for product in products:
                if product['url'] in match_scores:
                    score_info = match_scores[product['url']]
                    match_score = score_info.get('match_score', 50) if isinstance(score_info, dict) else 50
                    match_data.append({
                        '商品': product['name'][:25],
                        '匹配度': match_score
                    })
            
            if match_data:
                match_df = pd.DataFrame(match_data)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                colors_match = ['#51cf66' if x > 70 else '#ffd43b' if x > 50 else '#ff6b6b' for x in match_df['匹配度']]
                bars = ax.barh(match_df['商品'], match_df['匹配度'], color=colors_match, edgecolor='black', linewidth=1.5)
                
                for i, (bar, val) in enumerate(zip(bars, match_df['匹配度'])):
                    ax.text(val + 1, i, f'{val:.1f}%', va='center', fontweight='bold')
                
                ax.set_xlabel('匹配度 (%)', fontsize=12, fontweight='bold')
                ax.set_title('用戶需求匹配度', fontsize=14, fontweight='bold')
                ax.set_xlim(0, 105)
                ax.grid(axis='x', alpha=0.3)
                
                plt.tight_layout()
                st.pyplot(fig)
            
            # 詳細說明
            for product in products:
                if product['url'] in match_scores:
                    score_info = match_scores[product['url']]
                    
                    if isinstance(score_info, dict):
                        match_pct = score_info.get('match_score', 0)
                        with st.expander(f"📊 {product['name'][:50]} - 匹配度 {match_pct:.1f}%"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if score_info.get('matching_factors'):
                                    st.success("**符合的需求:**")
                                    for factor in score_info['matching_factors']:
                                        st.write(f"✅ {factor}")
                            
                            with col2:
                                if score_info.get('not_matching_factors'):
                                    st.warning("**不符合的需求:**")
                                    for factor in score_info['not_matching_factors']:
                                        st.write(f"⚠️ {factor}")
                            
                            if score_info.get('recommendation'):
                                recommendation = score_info['recommendation']
                                if '推薦' in recommendation and '不' not in recommendation:
                                    st.success(f"**建議:** {recommendation}")
                                elif '謹慎' in recommendation or '不' in recommendation:
                                    st.warning(f"**建議:** {recommendation}")
                                else:
                                    st.info(f"**建議:** {recommendation}")
        else:
            st.info("💡 匹配度分析暫未可用")
    
    # === 標籤 4: 價值主張 ===
    with rec_tab4:
        st.markdown("#### 商品價值主張分析")
        
        nlp_analysis = st.session_state.get('nlp_analysis', {})
        propositions_available = 'value_propositions' in nlp_analysis and nlp_analysis.get('value_propositions')
        
        if propositions_available:
            propositions = st.session_state.nlp_analysis['value_propositions']
            
            for product in products:
                if product['url'] in propositions:
                    prop = propositions[product['url']]
                    
                    with st.expander(f"💎 {product['name'][:50]}", expanded=False):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            # 獨特賣點
                            if prop.get('unique_selling_points') and prop['unique_selling_points']:
                                st.success("**🌟 獨特賣點:**")
                                for usp in prop['unique_selling_points']:
                                    st.write(f"• {usp}")
                            
                            # 價格公平性
                            if prop.get('price_fairness'):
                                fairness = prop['price_fairness']
                                if fairness == 'fair':
                                    st.success(f"**💵 價格公平性:** ✅ 公平")
                                elif fairness == 'underpriced':
                                    st.success(f"**💵 價格公平性:** 🎉 超值！")
                                else:
                                    st.warning(f"**💵 價格公平性:** ⚠️ 偏貴")
                        
                        with col2:
                            # 市場定位
                            if prop.get('market_position'):
                                position = prop['market_position']
                                st.info(f"**📊 市場定位:** {position}")
                            
                            # 競爭優勢
                            if prop.get('competitive_advantages') and prop['competitive_advantages']:
                                st.success("**🚀 競爭優勢:**")
                                for adv in prop['competitive_advantages']:
                                    st.write(f"• {adv}")
                        
                        # 價值總結
                        if prop.get('value_summary'):
                            st.markdown(f"**📝 價值總結:**\n{prop['value_summary']}")
        else:
            st.info("💡 價值主張分析暫未可用")


def main():
    """主函數"""
    initialize_session_state()
    render_header()
    
    # 檢查 API 金鑰
    if not GEMINI_API_KEY:
        st.error("""
        ❌ 未設定 Gemini API 金鑰！

        **解決方法：**

        **本地開發環境：**
        1. 編輯 .env 檔案
        2. 添加：GEMINI_API_KEY=你的_API_Key
        3. 保存後重新運行

        **Streamlit Cloud 環境：**
        1. 訪問 https://share.streamlit.io/
        2. 應用菜單 ⋮ → Edit secrets
        3. 添加以下配置（TOML 格式）：
           ```
           GEMINI_API_KEY = "你的_API_Key"
           ```
        4. 點擊 Save → 應用自動重啟（30秒）
        5. 刷新頁面

        **獲取 API Key：**
        訪問 https://aistudio.google.com/app/apikey
        """)
        st.stop()
    
    # 使用 Tab 組織介面
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 完整流程", "🔍 單品分析", "📚 使用說明", "⚙️ 設定"])
    
    with tab1:
        st.markdown("## 🚀 完整流程 - AI CP值比較")
        
        # ====== STEP 1: 輸入商品連結 ======
        with st.container():
            st.markdown("### 📌 步驟 1：輸入需要比較的商品網址")
            urls_text, is_dynamic, submit_button = render_input_section()
        
        # 爬蟲處理
        if submit_button and urls_text.strip():
            urls = [url.strip() for url in urls_text.split('\n') if url.strip()]
            
            if len(urls) < 2:
                st.error("❌ 至少需要 2 個商品連結")
            else:
                # 爬取商品
                with st.spinner("🕷️ 正在爬取商品資訊..."):
                    start_time = time.time()
                    products = scrape_products(urls, is_dynamic=is_dynamic)
                    scrape_time = time.time() - start_time
                
                if not products:
                    st.error("❌ 爬取失敗，請檢查連結是否有效")
                else:
                    # 保存爬蟲結果
                    st.session_state.products = products
                    st.session_state.scraping_complete = True
                    
                    # 資料清洗
                    with st.spinner("🧹 清洗資料中..."):
                        cleaned_products = DataCleaner.clean_products(products)
                        st.session_state.cleaned_products = cleaned_products
                    
                    st.success(f"✅ 成功爬取 {len(products)} 個商品 (耗時 {scrape_time:.2f}s)")
                    st.balloons()
        
        # ====== STEP 2：顯示商品內容（持久顯示）======
        if st.session_state.scraping_complete and st.session_state.cleaned_products:
            st.markdown("---")
            st.markdown("### 📦 步驟 2：爬取的商品內容")
            
            products = st.session_state.products
            
            # 商品概覽卡片
            st.markdown("**📊 商品概覽**")
            cols = st.columns(len(products))
            for col, product in zip(cols, products):
                with col:
                    st.metric(
                        label=product['name'][:20],
                        value=f"${product['price']:,.0f}",
                        delta=f"{product.get('rating', 0):.1f}⭐"
                    )
            
            # 詳細商品表格
            st.markdown("**📋 商品詳細資訊**")
            
            display_data = []
            for i, product in enumerate(products, 1):
                display_data.append({
                    '序號': i,
                    '商品名稱': product['name'][:50],
                    '價格': f"${product['price']:,.0f}",
                    '評分': f"{product['rating']:.1f}⭐" if product['rating'] > 0 else "N/A",
                    '評論數': len(product.get('reviews', [])),
                    '特徵數': len(product.get('specs', {}))
                })
            
            st.dataframe(
                pd.DataFrame(display_data),
                use_container_width=True,
                hide_index=True
            )
            
            # 可展開的詳細規格
            with st.expander("🔍 查看詳細規格和評論"):
                for i, product in enumerate(products, 1):
                    with st.container():
                        st.markdown(f"#### 商品 {i}: {product['name']}")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("價格", f"${product['price']:,.0f}")
                        with col2:
                            st.metric("評分", f"{product['rating']:.1f}⭐" if product['rating'] > 0 else "N/A")
                        with col3:
                            st.metric("評論數", len(product.get('reviews', [])))
                        
                        if product.get('specs'):
                            st.markdown("**規格:**")
                            specs_df = pd.DataFrame([
                                {'特徵': k, '值': str(v)[:50]} 
                                for k, v in product['specs'].items()
                            ])
                            st.dataframe(specs_df, use_container_width=True, hide_index=True)
                        
                        if product.get('reviews'):
                            st.markdown("**評論預覽:**")
                            for review in product['reviews'][:3]:
                                st.caption(f"💬 {review[:120]}...")
                        
                        st.markdown("---")
            
            # ====== STEP 3：輸入需求並進行 AI 分析 ======
            st.markdown("---")
            st.markdown("### 🤖 步驟 3：輸入需求並進行 AI 分析")
            
            user_requirement = st.text_area(
                "💡 請描述你的需求（這會幫助 AI 更準確地分析）:",
                placeholder="例如：需要輕便好攜帶，續航力至少8小時，價格不超過5000元，散熱要好",
                key="user_requirement",
                height=100
            )
            
            st.info("💡 **需求說明：** 您的需求描述得越詳細，AI 的分析結果越準確。可以包含功能需求、性能指標、預算限制等。")
            
            # AI 分析按鈕 - 自動分析
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("")
            with col2:
                analyze_button = st.button(
                    "🚀 自動分析並比較",
                    key="analyze_btn",
                    use_container_width=True,
                    type="primary"
                )
            
            if analyze_button:
                try:
                    progress_placeholder = st.empty()
                    status_placeholder = st.empty()
                    
                    progress_placeholder.info("🧠 正在進行 AI 分析...\n⏳ 預計耗時 30-60 秒，請耐心等待...")
                    status_placeholder.write("📌 正在調用 Gemini API 進行智慧分析...")
                    
                    print("📌 開始執行 analyze_products...")
                    nlp_analysis = analyze_products(st.session_state.cleaned_products, user_requirement)
                    print(f"📌 analyze_products 完成，返回結果: {list(nlp_analysis.keys())}")
                    
                    st.session_state.nlp_analysis = nlp_analysis
                    st.session_state.feature_weights = nlp_analysis.get('feature_weights', {})
                    
                    # 清除進度提示
                    progress_placeholder.empty()
                    status_placeholder.empty()
                    
                    if st.session_state.feature_weights:
                        st.success("✅ AI 分析完成！")
                        st.balloons()
                    else:
                        st.warning("⚠️ 無法生成特徵權重，使用預設值")
                        st.session_state.feature_weights = {f: 1.0 for p in st.session_state.cleaned_products for f in p.get('specs', {}).keys()}
                        st.session_state.nlp_analysis = st.session_state.nlp_analysis or {}
                        st.session_state.nlp_analysis['feature_weights'] = st.session_state.feature_weights
                    
                    st.session_state.analysis_complete = True
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ AI 分析出錯: {str(e)}")
                    print(f"🔴 分析錯誤: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
                    # 使用預設權重繼續
                    st.info("💡 使用預設權重繼續分析")
                    default_weights = {f: 1.0 for p in st.session_state.cleaned_products for f in p.get('specs', {}).keys()}
                    st.session_state.feature_weights = default_weights
                    st.session_state.nlp_analysis = {
                        'feature_weights': default_weights,
                        'review_analysis': {'sentiment': 'neutral', 'score': 0.5},
                        'pros_and_cons': {},
                        'user_match_scores': {},
                        'value_propositions': {}
                    }
                    st.session_state.analysis_complete = True
                    st.rerun()
            st.markdown("---")
            st.markdown("### 🏆 步驟 3：AI 分析比較結果（最佳 CP 值商品）")
            
            # 權重調整
            adjusted_weights = render_weight_adjustment()
            
            st.markdown("---")
            
            # 比較結果
            comparison_df = render_comparison_results(adjusted_weights)
            
            st.markdown("---")
            
            # 推薦結果
            render_recommendation()
    
    with tab2:
        st.markdown("### 🔍 輸入單個商品連結進行智慧分析")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            single_url = st.text_input(
                "輸入商品連結",
                placeholder="https://example.com/product",
                key="single_product_url"
            )
        
        with col2:
            analyze_button = st.button("分析商品", key="analyze_single_btn", use_container_width=True)
        
        if analyze_button and single_url.strip():
            with st.spinner("📊 正在分析商品..."):
                finder = SimilarProductFinder()
                
                # 提取商品資訊
                product_info = finder.extract_product_info_from_url(single_url.strip())
                
                if product_info:
                    st.success("✅ 成功提取商品資訊")
                    
                    # 顯示商品基本資訊
                    st.markdown("#### 📦 商品基本資訊")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("商品名稱", product_info['name'][:30])
                    
                    with col2:
                        st.metric("價格", f"${product_info['price']:,.0f}")
                    
                    with col3:
                        st.metric("評分", f"{product_info['rating']:.1f}⭐" if product_info['rating'] > 0 else "N/A")
                    
                    # 商品類別
                    st.markdown(f"**類別**: {product_info['category']}")
                    
                    # 規格資訊 - 以表格形式展示（如附圖格式）
                    if product_info['specs']:
                        st.markdown("#### 📋 規格資訊 (詳細對比表)")
                        
                        # 建立更漂亮的規格表
                        specs_list = []
                        for k, v in product_info['specs'].items():
                            specs_list.append({
                                '規格項目': k,
                                '數值': v
                            })
                        
                        if specs_list:
                            specs_df = pd.DataFrame(specs_list)
                            st.dataframe(specs_df, use_container_width=True, hide_index=True)
                            
                            # 規格摘要
                            with st.expander("📊 規格摘要"):
                                st.markdown("""
                                | 項目 | 詳情 |
                                |------|------|
                                """ + "\n".join([f"| {item['規格項目']} | {item['數值']} |" for item in specs_list[:10]]))
                    else:
                        st.warning("⚠️ 未能抓到詳細規格資訊")
                    
                    # 評論預覽
                    if product_info['reviews']:
                        st.markdown("#### 💬 評論預覽")
                        for i, review in enumerate(product_info['reviews'][:3], 1):
                            st.caption(f"{i}. {review[:120]}...")
                    
                    # 顯示搜尋關鍵字和推薦
                    st.markdown("#### 🔎 推薦相似商品搜尋")
                    search_queries = finder.generate_search_queries(product_info)
                    
                    # 執行相似商品查找（獲得搜尋建議）
                    similar_results = finder.find_similar_products_on_same_platform(single_url.strip())
                    
                    st.markdown("**建議搜尋關鍵字:**")
                    for i, query in enumerate(search_queries[:5], 1):
                        st.markdown(f"- {query}")
                    
                    # 顯示搜尋 URL
                    with st.expander("🔗 直接搜尋連結"):
                        # 判斷平台
                        if 'momoshop' in single_url.strip():
                            platform = 'momo'
                            base_url = "https://www.momoshop.com.tw/search/searchShop.php?keyword="
                        elif 'pchome' in single_url.strip():
                            platform = 'pchome'
                            base_url = "https://www.pchome.com.tw/search/?q="
                        elif 'shopee' in single_url.strip():
                            platform = 'shopee'
                            base_url = "https://shopee.tw/search?keyword="
                        else:
                            base_url = None
                        
                        if base_url:
                            st.markdown(f"**在 {platform.upper()} 上搜尋相似商品：**")
                            for i, query in enumerate(search_queries[:3], 1):
                                search_url = base_url + query
                                st.markdown(f"[{i}. 搜尋 \"{query}\"]({search_url})")
                    
                    # 建議
                    st.markdown("#### 💡 AI 分析建議")
                    
                    suggestions = []
                    if product_info['price'] > 10000:
                        suggestions.append("💰 **高價位商品** - 建議尋找同類型的中低價替代品進行比較")
                    elif product_info['price'] > 5000:
                        suggestions.append("💸 **中高價位** - 建議多比較幾個同等級商品")
                    else:
                        suggestions.append("✅ **合理價位** - 適合與同類型商品比較")
                    
                    if len(product_info['specs']) < 3:
                        suggestions.append("ℹ️ **規格資訊不完整** - 建議在詳細頁面查看更多規格")
                    else:
                        suggestions.append(f"✅ **規格詳細** ({len(product_info['specs'])} 項) - 有充分資訊進行比較")
                    
                    if product_info['rating'] >= 4.5:
                        suggestions.append(f"⭐ **高評分 ({product_info['rating']:.1f}/5)** - 用戶滿意度高")
                    elif product_info['rating'] >= 3.5:
                        suggestions.append(f"⭐ **中等評分 ({product_info['rating']:.1f}/5)** - 建議閱讀評論了解詳情")
                    elif product_info['rating'] > 0:
                        suggestions.append(f"⚠️ **評分較低 ({product_info['rating']:.1f}/5)** - 建議比較其他商品")
                    else:
                        suggestions.append("ℹ️ **暫無評分** - 建議參考評論")
                    
                    for suggestion in suggestions:
                        st.info(suggestion)
                    
                    # 加入比較清單功能
                    st.markdown("#### 📋 加入比較")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("➕ 加入比較清單", key=f"add_to_compare_{len(st.session_state.comparison_list)}", use_container_width=True):
                            # 檢查是否已經在清單中
                            if product_info['url'] not in [p['url'] for p in st.session_state.comparison_list]:
                                st.session_state.comparison_list.append(product_info)
                                st.success(f"✅ 已加入比較清單！目前有 {len(st.session_state.comparison_list)} 個商品")
                            else:
                                st.warning("⚠️ 此商品已在比較清單中")
                    
                    with col2:
                        if st.button("🗑️ 清空比較清單", key="clear_compare_list", use_container_width=True):
                            st.session_state.comparison_list = []
                            st.success("✅ 已清空比較清單")
                    
                    with col3:
                        if len(st.session_state.comparison_list) > 0:
                            st.info(f"📊 比較清單: {len(st.session_state.comparison_list)} 個商品")
                    
                    # 顯示比較清單
                    if st.session_state.comparison_list:
                        st.markdown("#### 📊 當前比較清單")
                        comparison_data = []
                        for i, prod in enumerate(st.session_state.comparison_list, 1):
                            comparison_data.append({
                                '序號': i,
                                '商品名稱': prod['name'][:40],
                                '價格': f"${prod['price']:,.0f}",
                                '評分': f"{prod['rating']:.1f}⭐" if prod['rating'] > 0 else "N/A",
                                '類別': prod['category']
                            })
                        
                        st.dataframe(pd.DataFrame(comparison_data), use_container_width=True, hide_index=True)
                        
                        # 詳細規格對比表（如附圖筆記本對比）
                        with st.expander("📊 詳細規格對比"):
                            st.markdown("### 規格對比表")
                            
                            # 收集所有規格項目
                            all_specs = {}
                            for prod in st.session_state.comparison_list:
                                for spec_key, spec_value in prod.get('specs', {}).items():
                                    if spec_key not in all_specs:
                                        all_specs[spec_key] = {}
                                    all_specs[spec_key][prod['name'][:20]] = spec_value
                            
                            # 建立對比表
                            if all_specs:
                                comparison_table = []
                                for spec_item, values in list(all_specs.items())[:15]:  # 限制前 15 個規格
                                    row = {'規格項目': spec_item}
                                    for prod_name, spec_value in values.items():
                                        row[prod_name] = spec_value[:50]  # 限制長度
                                    comparison_table.append(row)
                                
                                if comparison_table:
                                    comp_df = pd.DataFrame(comparison_table)
                                    st.dataframe(comp_df, use_container_width=True, hide_index=True)
                        
                        # 開始比較按鈕
                        if len(st.session_state.comparison_list) >= 2:
                            if st.button("🚀 開始比較分析", key="start_comparison", use_container_width=True):
                                # 轉移到完整流程頁面並預填 URL
                                st.info("✅ 已將商品加入到比較清單。請切換到「🚀 完整流程」標籤開始分析。")
                                st.session_state.urls_text = '\n'.join([p['url'] for p in st.session_state.comparison_list])
                        else:
                            st.warning("⏳ 需要至少 2 個商品才能進行比較")
                    
                    # 下一步提示
                    st.markdown("#### 📋 下一步")
                    st.markdown("""
                    **方式 1：單品分析**
                    1. 分析多個商品（使用此頁面）
                    2. 分別「加入比較清單」
                    3. 點擊「開始比較分析」
                    
                    **方式 2：直接比較**
                    1. 切換到「🚀 完整流程」頁面
                    2. 輸入 2-4 個商品連結
                    3. 查看 CP 值排行和 AI 推薦
                    """)
                
                else:
                    st.error("❌ 無法提取商品資訊，請檢查URL是否有效")
    
    with tab3:
        st.markdown("""
        ## 📚 使用說明
        
        ### 1. 輸入商品連結
        - 複製商品頁面的完整 URL
        - 每行輸入一個連結
        - 支援 2-4 個商品比較
        
        ### 2. 選擇爬蟲模式
        - **靜態頁面** (預設): 適用於 PChome、蝦皮等
        - **動態頁面**: 適用於需要 JavaScript 載入的網站 (較慢)
        
        ### 3. AI 分析特徵
        - 系統自動使用 NLP 分析商品特徵重要性
        - 可選填個人需求以提升精準度
        
        ### 4. 調整權重
        - 根據需求調整各特徵的重要性
        - 1 分 = 不重要，3 分 = 非常重要
        
        ### 5. 查看結果
        - CP 值 = Σ(特徵分數 × 權重) / 價格
        - 排行榜展示最具性價比的商品
        - AI 推薦理由說明選擇原因
        
        ---
        
        ## 📊 CP 值計算公式
        
        $$CP = \\frac{\\sum(Feature \\times Weight)}{Price} \\times (1 + \\frac{Rating}{5} \\times 0.2)$$
        
        - **Feature**: 各特徵的歸一化分數 (0-1)
        - **Weight**: 特徵權重 (1-3)
        - **Price**: 商品價格
        - **Rating**: 商品評分加成
        """)
    
    with tab4:
        st.markdown("### ⚙️ 系統設定")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### API 設定")
            st.info(f"✅ Gemini API 已連接" if GEMINI_API_KEY else "❌ Gemini API 未設定")
        
        with col2:
            st.markdown("#### 爬蟲設定")
            st.markdown(f"- 請求逾時: 10 秒")
            st.markdown(f"- Selenium 等待: 10 秒")
        
        st.markdown("---")
        
        st.markdown("#### 支援的電商平台")
        platforms = ["Momo 購物", "PChome 24h", "Yahoo 購物", "蝦皮", "露天"]
        st.write("、".join(platforms))
        
        st.markdown("---")
        
        st.markdown("#### 版本資訊")
        st.write("v1.0.0 - 2024年")


if __name__ == "__main__":
    main()
