import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from scipy.stats import gaussian_kde
import warnings


GOLD    = "#f0c040"
BLUE    = "#58a6ff"
DARK_BG = "#0f1722"
GRID    = "#1e2a3a"
TEXT    = "#e6edf3"
PLOT_LAYOUT = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#111827",
    font_color="#e6edf3",
    font_family="DM Sans",
    title_font_family="Syne",
    title_font_color="#f0c040",
    title_font_size=15,
    legend=dict(bgcolor="#161d2e", bordercolor="#1e2a3a", borderwidth=1),
    xaxis=dict(gridcolor="#1e2a3a", zerolinecolor="#1e2a3a"),
    yaxis=dict(gridcolor="#1e2a3a", zerolinecolor="#1e2a3a"),
)

def page_visualisations(df):
    """Visualisations page — two-stage flow:
       Stage 1: Brand selected -> model comparison boxplot
       Stage 2: Model selected ->full detailed charts
    """
    st.markdown("<div class='page-title'>📉 Vehicle Price Visualisations</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>First explore all models for a brand, then drill into a specific model.</div>", unsafe_allow_html=True)

    #Brand selection - Model Price Comparison

    st.markdown("""
    ## 🔎 Step 1: Select the Brand
    Choose a vehicle brand to explore model-level price analysis and market trends.
    """)

    brand_sel = st.selectbox("Select Brand", sorted(df["Brand"].unique()), key="viz_brand")
    brand_df  = df[df["Brand"] == brand_sel].copy()

    # Top models by listing count (cap at 15 for readability)
    top_models = brand_df["Model"].value_counts().head(15).index.tolist()
    brand_top  = brand_df[brand_df["Model"].isin(top_models)]

    st.markdown(f"<div class='insight-box'><strong>{brand_sel}</strong> has <strong>{brand_df['Model'].nunique()}</strong> models and <strong>{len(brand_df):,}</strong> listings. Showing top {len(top_models)} models by listing count below.</div>", unsafe_allow_html=True)

    #Model comparison boxplot
    model_order = (
        brand_top.groupby("Model")["Price"]
        .median()
        .sort_values(ascending=True)
        .index.tolist()
    )

    fig_compare = px.box(
        brand_top,
        x="Price", y="Model",
        orientation="h",
        color="Model",
        category_orders={"Model": model_order},
        color_discrete_sequence=px.colors.qualitative.Bold,
        template="plotly_dark",
        title=f"{brand_sel} — Price Distribution by Model (LKR Lakhs)",
        labels={"Price": "Price (LKR Lakhs)", "Model": ""}
    )
    fig_compare.update_layout(
        **PLOT_LAYOUT,
        height=max(400, len(top_models) * 38 + 80),
        showlegend=False,
        margin=dict(t=50, b=30, l=10, r=30)
    )
    #Short Overview Above Chart
    st.markdown("""
    ### 📊 Model Price Comparison
    This chart shows how prices are distributed across different models of the selected brand.
    Higher median positions indicate premium models, while wider boxes suggest greater price variation.
    """)

    st.plotly_chart(fig_compare, use_container_width=True)

    # Summary table
    model_summary = (
        brand_top.groupby("Model")["Price"]
        .agg(Listings="count", Median="median", Mean="mean", Min="min", Max="max")
        .round(2)
        .sort_values("Median", ascending=False)
        .reset_index()
    )
    with st.expander("📋 Model Price Summary Table"):
        st.dataframe(model_summary, use_container_width=True)

    

    # Model Median Interpretation


    if not model_summary.empty:

        highest_model = model_summary.iloc[0]
        lowest_model = model_summary.iloc[-1]

        highest_name = highest_model["Model"]
        highest_median = highest_model["Median"]

        lowest_name = lowest_model["Model"]
        lowest_median = lowest_model["Median"]

        median_gap = highest_median - lowest_median
        median_ratio = highest_median / lowest_median if lowest_median != 0 else 0

        with st.expander("📊 Click to View Model Price Interpretation", expanded=False):

            st.markdown(f"""
            <div class='insight-box'>

            🥇 <b>Highest Median Price Model:</b> <strong>{highest_name}</strong><br>
            • Median Price: <strong>{highest_median:,.2f} LKR Lakhs</strong><br><br>

            🥉 <b>Lowest Median Price Model:</b> <strong>{lowest_name}</strong><br>
            • Median Price: <strong>{lowest_median:,.2f} LKR Lakhs</strong><br><br>

            📈 <b>Price Gap:</b> {median_gap:,.2f} LKR Lakhs<br>
            📊 <b>Relative Difference:</b> {median_ratio:.2f}x<br><br>

            <b>🔎 Market Interpretation</b><br>
            • <strong>{highest_name}</strong> sits in the premium tier for this brand.<br>
            • <strong>{lowest_name}</strong> represents the budget segment.<br>
            • Ratio > 1.3x → strong segmentation within brand.<br>
            • Ratio ≈ 1.0x → models compete within similar price range.<br>

            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)
    
    # Model + Fuel + Gear - Detailed Charts
    
    st.markdown(f"""
    ## 🚗 Step 2:Select the Model
    Select a specific model to view price distribution and detailed market insights.

    ℹ️ *Fuel type and gear type options will update automatically based on the selected brand and model.*
                some models may offer multiple fuel or gear variants — 
                please select your preferred configuration for accurate analysis.
    """)

    col1, col2, col3 = st.columns(3)

    models_available = sorted(brand_df["Model"].unique())
    with col1:
        model_sel = st.selectbox("Select Model", models_available, key="viz_model")

    model_df = brand_df[brand_df["Model"] == model_sel]

    with col2:
        fuel_sel = st.selectbox("Fuel Type", sorted(model_df["Fuel Type"].unique()), key="viz_fuel")
    with col3:
        gear_sel = st.selectbox("Transmission", sorted(model_df["Gear"].unique()), key="viz_gear")

    filtered_df = model_df[
        (model_df["Fuel Type"] == fuel_sel) &
        (model_df["Gear"] == gear_sel)
    ].copy()

    data_count = len(filtered_df)
    st.markdown(
        f"<div class='insight-box'>Showing <strong>{data_count}</strong> listings for "
        f"<strong>{brand_sel} {model_sel}</strong> · {fuel_sel} · {gear_sel}</div>",
        unsafe_allow_html=True
    )

    if data_count == 0:
        st.error("No listings found for this combination. Try a different fuel or transmission.")
        return
    if data_count == 1:
        st.warning("Only ONE listing available — statistical plots are not meaningful.")
        st.dataframe(filtered_df)
        return
    if data_count < 5:
        st.warning("Very few data points — KDE and trendlines may be unreliable.")

    st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

    # Price Distribution
    st.markdown(
    f"## 📦 {brand_sel} {model_sel} Price Distribution "
    f"({fuel_sel} · {gear_sel})")

    st.markdown(f"""
    <div class='info-box'>
    This section analyzes the market price distribution of the selected configuration.
    The density curve shows overall pricing patterns, while the boxplot highlights
    price spread, median value, and potential outliers for selected configuration.
    </div>
    """, unsafe_allow_html=True)

    prices = filtered_df["Price"].dropna()
    colA, colB = st.columns(2)

    with colA:
        if len(prices) >= 5:
            kde     = gaussian_kde(prices)
            x_range = np.linspace(prices.min(), prices.max(), 500)

            fig_kde = go.Figure()

            # ── KDE Curve (Gold theme) ──
            fig_kde.add_trace(go.Scatter(
                x=x_range,
                y=kde(x_range),
                mode="lines",
                fill="tozeroy",
                fillcolor="rgba(240,192,64,0.30)",  # Soft gold fill
                line=dict(width=3, color=GOLD),
                hovertemplate="Price: %{x:,.2f}<br>Density: %{y:.4f}<extra></extra>"
            ))

            fig_kde.update_layout(
                title=dict(
                    text="Price Distribution",
                    x=0.5,
                    xanchor="center",
                    font=dict(color=GOLD, size=18)
                ),
                height=400,
                paper_bgcolor=DARK_BG,
                plot_bgcolor=DARK_BG,
                font=dict(color=TEXT),
                xaxis=dict(gridcolor=GRID, title="Price (LKR Lakhs)"),
                yaxis=dict(gridcolor=GRID, title="Density")
            )

            st.plotly_chart(fig_kde, use_container_width=True)


    with colB:
        fig_box = go.Figure()

        # Boxplot (Blue theme for contrast)
        fig_box.add_trace(go.Box(
            y=prices,
            boxmean=True,
            marker_color="#4DA3FF",  # Different blue shade
            line=dict(color="#4DA3FF", width=2),
            fillcolor="rgba(77,163,255,0.30)",
            hovertemplate="Price: %{y:,.2f}<extra></extra>"
        ))

        fig_box.update_layout(
            title=dict(
                text="Price Distribution",
                x=0.5,
                xanchor="center",
                font=dict(color=GOLD, size=18)  
            ),
            height=400,
            paper_bgcolor=DARK_BG,
            plot_bgcolor=DARK_BG,
            font=dict(color=TEXT),
            yaxis=dict(gridcolor=GRID, title="Price (LKR Lakhs)")
        )

        st.plotly_chart(fig_box, use_container_width=True)

    # Stats insight box
    from scipy.stats import skew as scipy_skew
    mean_price   = prices.mean()
    median_price = prices.median()
    std_price    = prices.std()
    skewness     = scipy_skew(prices)

    if skewness > 0.5:
        dist_type   = "Positively Skewed (Right-Skewed)"
        dist_interp = "Premium listings are pulling the distribution right."
    elif skewness < -0.5:
        dist_type   = "Negatively Skewed (Left-Skewed)"
        dist_interp = "Lower-priced listings dominate the market."
    else:
        dist_type   = "Approximately Normal"
        dist_interp = "Prices are evenly spread around the average."

    with st.expander("📊 Click to View Statistical Summary & Insight", expanded=False):

        st.markdown(f"""
        <div class='insight-box'>
        <strong>{brand_sel} {model_sel}</strong> ({fuel_sel} · {gear_sel})<br><br>

        <b>📊 Statistical Summary</b><br>
        • Mean: <strong>{mean_price:,.2f} LKR Lakhs</strong> &nbsp;|&nbsp;
        Median: <strong>{median_price:,.2f} LKR Lakhs</strong> &nbsp;|&nbsp;
        Std Dev: <strong>{std_price:,.2f}</strong><br>

        • Skewness: <strong>{skewness:.2f}</strong> → {dist_type}<br><br>

        <b>💡 Insight</b><br>
        {dist_interp} &nbsp;

        Pricing is {'<strong>volatile</strong>' if std_price > mean_price * 0.25 else '<strong>stable</strong>'} 
        for this segment.

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

    #Price by YOM 
    st.markdown(f"""
    ## 📅 Price by Year of Manufacture — {brand_sel} {model_sel} ({fuel_sel} · {gear_sel})
    Explore how market prices change across production years and identify 
    value retention patterns within this vehicle segment.
    """)

    
    fig_yom = px.box(
        filtered_df,
        x="YOM",
        y="Price",
        color="YOM",
        color_discrete_sequence=["#1e2a3a","#58a6ff","#f0c040","#2ea043","#d73a49","#8957e5"],
        template="plotly_dark",
        labels={"Price": "Price (LKR Lakhs)", "YOM": "Year of Manufacture"}
    )

    fig_yom.update_traces(
        marker_line_width=1.2,
        marker_line_color=GOLD
    )

    fig_yom.update_layout(
        title=dict(
            text=f"Price Distribution by Year of Manufacture",
            x=0.5,
            xanchor="center",
            font=dict(color=GOLD, size=18)
        ),
        height=420,
        paper_bgcolor=DARK_BG,
        plot_bgcolor=DARK_BG,
        font=dict(color=TEXT),
        xaxis=dict(gridcolor=GRID),
        yaxis=dict(gridcolor=GRID),
        showlegend=False
    )

    st.plotly_chart(fig_yom, use_container_width=True)

    yom_stats = (
        filtered_df.groupby("YOM")["Price"]
        .agg(median="median", mean="mean", count="count")
        .reset_index().sort_values("median", ascending=False)
    )
    if len(yom_stats) >= 2:
        highest = yom_stats.iloc[0]
        lowest  = yom_stats.iloc[-1]
        ratio   = highest["median"] / lowest["median"] if lowest["median"] != 0 else 0
    
    with st.expander("📊 View YOM Price Comparison Insight"):
        st.markdown(f"""
            <div class='insight-box'>
                <b>📊 YOM Price Comparison</b><br>
                • Highest median: <strong>{int(highest['YOM'])}</strong> at 
                <strong>{highest['median']:,.2f} LKR Lakhs</strong><br>
                • Lowest median: <strong>{int(lowest['YOM'])}</strong> at 
                <strong>{lowest['median']:,.2f} LKR Lakhs</strong><br>
                • Spread ratio: <strong>{ratio:.2f}x</strong> — price variation across years is 
                {'<strong>significant</strong>' if ratio > 1.2 else '<strong>moderate</strong>'}.
            </div>
            """, unsafe_allow_html=True)
        
    st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

# Price by Province 
    st.markdown(f"""
    ## 📍 Price by Province — {brand_sel} {model_sel} ({fuel_sel} · {gear_sel})

    This section compares price distributions across provinces to evaluate
    regional pricing differences and market variability.
    """)

    # Ensure Province column exists
    if "Province" in filtered_df.columns and filtered_df["Province"].nunique() > 0:

        # Remove missing provinces
        province_df = filtered_df.dropna(subset=["Province"]).copy()

        # Order provinces by median price
        province_order = (
            province_df.groupby("Province")["Price"]
            .median()
            .sort_values(ascending=True)
            .index.tolist()
        )

        fig_prov = px.box(
            province_df,
            x="Province",
            y="Price",
            color="Province",
            category_orders={"Province": province_order},
            template="plotly_dark",
            labels={"Price": "Price (LKR Lakhs)", "Province": "Province"}
        )

        fig_prov.update_traces(
            marker_line_width=1.2,
            marker_line_color=GOLD
        )

        fig_prov.update_layout(
            title=dict(
                text="Price Distribution by Province",
                x=0.5,
                xanchor="center",
                font=dict(color=GOLD, size=18)
            ),
            height=450,
            paper_bgcolor=DARK_BG,
            plot_bgcolor=DARK_BG,
            font=dict(color=TEXT),
            xaxis=dict(gridcolor=GRID),
            yaxis=dict(gridcolor=GRID),
            showlegend=False
        )

        st.plotly_chart(fig_prov, use_container_width=True)

        
        #Province Statistics (Hidden)

        prov_stats = (
            province_df.groupby("Province")["Price"]
            .agg(median="median", std="std", count="count")
            .reset_index()
        )

        with st.expander("📊 Click to View Provincial Statistics", expanded=False):
            st.dataframe(prov_stats.sort_values("median", ascending=False),
                        use_container_width=True)

        
        # Interpretation (Hidden)
        if len(prov_stats) >= 2:

            highest = prov_stats.sort_values("median", ascending=False).iloc[0]
            lowest  = prov_stats.sort_values("median", ascending=True).iloc[0]
            most_var = prov_stats.sort_values("std", ascending=False).iloc[0]

            with st.expander("🔎 Click to View Provincial Market Interpretation", expanded=False):

                st.markdown(f"""
                <div class='insight-box'>

                🥇 <b>Highest Median Price:</b> <strong>{highest['Province']}</strong><br>
                • Median: <strong>{highest['median']:,.2f} LKR Lakhs</strong><br><br>

                🥉 <b>Lowest Median Price:</b> <strong>{lowest['Province']}</strong><br>
                • Median: <strong>{lowest['median']:,.2f} LKR Lakhs</strong><br><br>

                📊 <b>Highest Price Variability:</b> <strong>{most_var['Province']}</strong><br>
                • Std Dev: <strong>{most_var['std']:,.2f}</strong><br><br>

                <b>📍 Regional Insight</b><br>
                • Higher median provinces indicate stronger premium demand.<br>
                • Lower median provinces reflect more budget-oriented markets.<br>
                • High variability suggests diverse listing conditions or trims.

                </div>
                """, unsafe_allow_html=True)

    else:
        st.warning("Province information is not available for this dataset.")
    st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)
  # ── . Sparse combinations ────────────────────────────
    st.markdown("## ⚠️ Sparse Brand–Model Combinations")

    st.markdown("""
    This section identifies brand–model combinations with very few listings.
    Low sample sizes may reduce statistical reliability and affect model interpretation.
    """)

    combo_counts = df.groupby(["Brand","Model"]).size().reset_index(name="Count")
    low_data = combo_counts[combo_counts["Count"] < 5].sort_values("Count")

    # Hide table inside expander
    with st.expander("🔍 Click to View Sparse Combinations", expanded=False):
        st.dataframe(low_data, use_container_width=True)
    
    st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)

     #EDA Limitations (Hidden Section) 

    st.markdown("## 🔒 Exploratory Data Analysis (EDA) Limitations")

    st.markdown("""
    Understanding limitations is essential for responsible interpretation 
    of analytical findings.
    """)

    with st.expander("⚠️ Click to View EDA Limitations", expanded=False):

        st.markdown("""
        <div class='insight-box'>

        <h4 style='color:#f0c040;'>Exploratory Data Analysis Limitations</h4>

        <ul>
            <li><b>Data Source Bias:</b> Listings may not represent the entire Sri Lankan car market.</li>
            <li><b>Missing Values:</b> Some vehicles may have incomplete province, fuel, or transmission information.</li>
            <li><b>Outliers:</b> Extremely high or low prices may distort distributions.</li>
            <li><b>Time Sensitivity:</b> Prices fluctuate due to import regulations, taxes, and exchange rates.</li>
            <li><b>Unobserved Factors:</b> Condition, accident history, and optional features are not captured.</li>
            <li><b>Causality Limitation:</b> EDA identifies patterns — not cause-and-effect relationships.</li>
        </ul>

        <p>
        ⚠️ These insights should be interpreted as descriptive market trends, 
        not definitive pricing rules.
        </p>

        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='gold-line'></div>", unsafe_allow_html=True)
