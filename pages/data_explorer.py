#s16798

#page_data_explorer(df) function

"""
This function is a fully interactive data exploration page in Streamlit for Sri Lankan used cars.
Users can filter, visualize, and understand both the dataset as a whole and drill down into brands/models.
All charts, tables, and metrics are dynamically updated based on user input.
"""


import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

#Shared Plotly layout applied to every chart for visual consistency
GOLD    = "#f0c040"
BLUE    = "#58a6ff"
DARK_BG = "#0f1722"
GRID    = "#1e2a3a"
TEXT    = "#ffffff"

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


#function definition

def page_data_explorer(df):

    
   #Page Header & Branding
   # # Displays the Car.LK logo title and subtitle at the top of the page

    st.markdown("""
    <div style="text-align:center; padding: 12px 0 10px 0;">
        <h1 style="font-family:'Syne',sans-serif;font-size:3.5rem;font-weight:900;color:#f0c040;margin-bottom:4px;">
        🚗 Car.LK</h1>
        <p style="font-family:'DM Sans',sans-serif;font-size:1rem;color:#c9d1d9;font-weight:50;margin-top:0;">
        Sri Lanka Used Car Market Explorer</p>
        <hr style="border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;">
    </div>""", unsafe_allow_html=True)

    #Dashboard Guide Box (Explains how to use the dashboard)
    ## Explains what each page in the sidebar does so users know where to navigate

    st.markdown("""
    <div style="
    background:#111827;
    border:1px solid #1e2a3a;
    border-radius:12px;
    padding:18px 22px;
    margin-bottom:20px;
    ">

    <div style="color:#ffffff;font-size:16px;font-weight:600;margin-bottom:10px;">
    📌 Dashboard Guide
    </div>

    <div style="color:#e6edf3;font-size:14px;margin-bottom:12px;">
    Use the navigation menu on the left sidebar to explore different sections of the dashboard.
    Each page focuses on a different type of analysis of the Sri Lankan car market dataset.
    </div>

    <div style="color:#7d8590;font-size:13px;line-height:1.8;">
    <b>📊 Data Explorer</b> – Explore the raw dataset, inspect variables, and understand the structure of the data.<br>
    <b>📉 Visualisations</b> – Interactive charts that reveal trends in price, mileage, engine capacity, and regional distribution.<br>
    <b>📈 Car Price Prediction</b> – Enter vehicle details and use a machine learning model to estimate the expected market price.<br>
    <b>🧪 Hypothesis Testing</b> – Statistical tests used to validate assumptions about the car market data.<br>
    <b>❓ Help</b> – Instructions on how to use the dashboard and interpret the results.
    </div>

    <div style="margin-top:10px;color:#7d8590;font-size:12px;">
    💡 Select a page from the sidebar to begin exploring the analysis.
    </div>

    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    # Page introduction section
    #text welcoming the user and describing the page purpose
    st.markdown("<div class='page-title'>🚘 Your Next Car Awaits</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Search, filter, and explore Sri Lanka's second-hand car market.</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-subtitle'>Find the perfect pre-owned vehicle that fits your budget and needs.</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    st.markdown("### 📊 Overview Metrics")
    st.markdown("These numbers give you a quick snapshot of the dataset: total listings, number of brands, average price, and year of manufacture range.")

    # Top Metrics
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Listings", f"{len(df):,}")
    c2.metric("Brands", df["Brand"].nunique())
    c3.metric("Avg Price (LKR M)", f"{df['Price'].mean():.1f}")
    c4.metric("YOM Range", f"{df['YOM'].min()}–{df['YOM'].max()}")

      # Filter instructions section

    st.markdown("""
    <div style="height:4px;background:linear-gradient(90deg,transparent,#d4af37,#f0c040,#d4af37,transparent);margin:40px 0;border-radius:5px;"></div>
    """, unsafe_allow_html=True)

    with st.expander("ℹ️ How to use the filters (click to expand)"):
        st.markdown(
            """
    - **Brand & Model:** Select one or multiple car brands and models. Check 'All Brands' or 'All Models' to include everything.  
    - **Fuel Type & Gear:** Choose fuel type and gear type. 'All' options include everything.  
    - **Price Range:** Set min and max prices in LKR Lakhs.  
    - **Year of Manufacture:** Select the range of vehicle years.  
    - **Engine Segment:** Vehicles are grouped by engine capacity:
        - Micro (<800cc)
        - Compact (800–1200cc)
        - Mid-Range (1200–1600cc)
        - Large (>1600cc)
        - Unknown (if missing)
    """
        )

    # Brand filter
    all_brands = sorted(df["Brand"].unique())
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sel_all_brands = st.checkbox("All Brands", value=False, key="de_all_brands")
        selected_brands = all_brands if sel_all_brands else [st.selectbox("Select Brand", all_brands, key="de_brand")]

    brand_df = df[df["Brand"].isin(selected_brands)]

    # Model filter
    all_models = sorted(brand_df["Model"].unique())
    with col2:
        sel_all_models = st.checkbox("All Models", value=False, key="de_all_models")
        selected_models = all_models if sel_all_models else [st.selectbox("Select Model", all_models, key="de_model")]

    model_df = brand_df[brand_df["Model"].isin(selected_models)]

     # Fuel filter
    all_fuels = sorted(model_df["Fuel Type"].unique())
    with col3:
        sel_all_fuels = st.checkbox("All Fuel Types", value=False, key="de_all_fuels")
        selected_fuels = all_fuels if sel_all_fuels else [st.selectbox("Select Fuel Type", all_fuels, key="de_fuel")]

    # Gear filter
    all_gears = sorted(model_df["Gear"].unique())
    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)
    with col4:
        sel_all_gears = st.checkbox("All Gear Types", value=False, key="de_all_gears")
        selected_gears = all_gears if sel_all_gears else [st.selectbox("Select Gear Type", all_gears, key="de_gear")]

    # Price range slider
    p_min, p_max = float(model_df["Price"].min()), float(model_df["Price"].max())
    if p_min == p_max:
        price_range = (p_min, p_max)
        st.write(f"Price: {p_min} LKR Lakhs")
    else:
        price_range = st.slider("Price Range (LKR Lakhs)", p_min, p_max, (p_min, p_max), key="de_price")
    
    
     # Year range slider
    y_min, y_max = int(model_df["YOM"].min()), int(model_df["YOM"].max())
    if y_min == y_max:
        year_range = (y_min, y_max)
        st.write(f"Year of Manufacture: {y_min}")
    else:
        year_range = st.slider("Year of Manufacture", y_min, y_max, (y_min, y_max), key="de_year")

     # Apply filters to dataset
    filtered = model_df[
        (model_df["Fuel Type"].isin(selected_fuels)) &
        (model_df["Gear"].isin(selected_gears)) &
        (model_df["Price"].between(*price_range)) &
        (model_df["YOM"].between(*year_range))
    ]

    st.markdown(f"<div class='insight-box'>Showing <strong>{len(filtered):,}</strong> listings matching your filters.</div>", unsafe_allow_html=True)
    show_cols = ["Brand","Model","YOM","Engine_Segment","Gear","Fuel Type","Millage(KM)","Province","Condition","Price"]
    st.dataframe(filtered[show_cols].sort_values(["Brand","Model"]).reset_index(drop=True), use_container_width=True, height=320)
    
    # Explain the summary section to users
    st.markdown("### 📊 Dataset Summary")
    st.markdown(
    "This section provides a quick overview of the selected dataset:\n\n"
    "- **Numerical Summary:** Shows statistics like mean, min, max, and quartiles for numerical columns such as Price, Mileage, Engine capacity, and Age.\n"
    "- **Categorical Distribution:** Shows the top 10 values for selected categorical columns and their counts, so you can see the most common brands, fuel types, gears, etc."
)

    col_a, col_b = st.columns(2)

    #Numerical Summary Table
    with col_a:
        st.markdown("<span style='color:#7d8590;font-size:0.82rem;text-transform:uppercase;'>Numerical Summary</span>", unsafe_allow_html=True)
        st.dataframe(filtered[["Price","Millage(KM)","Engine (cc)","Age"]].describe().round(2), use_container_width=True)

    #Categorical Distribution Chart
    with col_b:
        st.markdown("<span style='color:#7d8590;font-size:0.82rem;text-transform:uppercase;'>Categorical Distribution</span>", unsafe_allow_html=True)
        
        ## Dropdown to pick which categorical column to visualise
        cat_col = st.selectbox(
            "Select column", 
            ["Brand","Fuel Type","Gear","Engine (cc)","Condition","Province"], 
            key="de_cat_col"
        )

        st.markdown("<div style='margin-top:12px'></div>", unsafe_allow_html=True)
        
        ## Count top 10 values for the selected column and sort descending
        cat_counts = filtered[cat_col].value_counts().head(10).reset_index()
        cat_counts.columns = [cat_col, "Count"]
        cat_counts = cat_counts.sort_values("Count", ascending=False)
        
        layout_cat = PLOT_LAYOUT.copy()
        layout_cat['yaxis'] = dict(
            gridcolor="#1e2a3a", 
            zerolinecolor="#1e2a3a", 
            tickfont=dict(size=12)
        )
        
        # Add count labels on top
        fig_cat = px.bar(
            cat_counts, 
            x=cat_col, 
            y="Count", 
            color="Count",
            text="Count",  
            color_continuous_scale=[[0,"#1e2a3a"],[1,"#f0c040"]],
            template="plotly_dark"
        )
        fig_cat.update_traces(
            textposition="inside",  # Display on top of bars
            textfont=dict(color="#e6edf3", size=12)
        )
        fig_cat.update_yaxes(range=[0, cat_counts["Count"].max() * 1.2])
        fig_cat.update_layout(
            **layout_cat, 
            title=dict(
                text=f"Distribution by {cat_col}",
                font=dict(family="Syne", color="#f0c040", size=15),
                x=0,
                xanchor="left",
            ),
            showlegend=False, 
            height=280, 
            coloraxis_showscale=False, 
            margin=dict(t=60, b=40, l=10, r=10)
        )
        
        st.plotly_chart(fig_cat, use_container_width=True)
  
    # Brand & Model Explorer
  
    #Two chart types:
    #Bar chart - number of listings per model
    #Box chart - price distribution per model

    st.markdown("### Brand & Model Explorer")
    st.markdown("Select a Brand, Fuel Type, and Gear Type to explore the top models. You can view either the number of listings (bar chart) or price distribution (box chart) for the selected models.")

    bm_col1, bm_col2 = st.columns([1,2])


    #Brand/Fuel/Gear controls
    with bm_col1:
        selected_brand = st.selectbox(
            "Select a Brand",
            all_brands,
            index=all_brands.index("Toyota") if "Toyota" in all_brands else 0,
            key="de_bm_brand"
        )

        # Filter to selected brand; get available fuel and gear options
        bm_brand_df = df[df["Brand"] == selected_brand]
        brand_fuels = sorted(bm_brand_df["Fuel Type"].unique())
        brand_gears = sorted(bm_brand_df["Gear"].unique())

        #Fuel type toggle — all or specific
        sel_all_fuels2 = st.checkbox("All Fuel Types", value=True, key="de_bm_all_fuels")
        selected_fuel2 = brand_fuels if sel_all_fuels2 else [st.selectbox("Select Fuel Type", brand_fuels, key="de_bm_fuel")]

        # Gear type toggle — all or specific
        sel_all_gears2 = st.checkbox("All Gear Types", value=True, key="de_bm_all_gears")
        selected_gear2 = brand_gears if sel_all_gears2 else [st.selectbox("Select Gear Type", brand_gears, key="de_bm_gear")]

        #Radio button to switch between bar and box chart
        chart_type = st.radio("Chart Type", ["Bar – Listing Count", "Box – Price per Model"], key="de_bm_chart")

    bm_filtered = bm_brand_df[
        (bm_brand_df["Fuel Type"].isin(selected_fuel2)) &
        (bm_brand_df["Gear"].isin(selected_gear2))
    ]
    top_models = bm_filtered["Model"].value_counts().head(10).index.tolist()
    bm_filtered = bm_filtered[bm_filtered["Model"].isin(top_models)]

    #Brand/Model Chart
    with bm_col2:
        layout_bm = PLOT_LAYOUT.copy()
        layout_bm['yaxis'] = dict(gridcolor="#1e2a3a", zerolinecolor="#1e2a3a", tickfont=dict(size=12))
        
        if chart_type == "Bar – Listing Count":
            ## Horizontal bar chart — how many listings each model has
            bar_data = bm_filtered["Model"].value_counts().reset_index()
            bar_data.columns = ["Model","Listings"]
            bar_data = bar_data.sort_values("Listings", ascending=True)
            
            fig_bm = px.bar(
                bar_data,
                x="Listings",
                y="Model",
                orientation="h",
                title=f"{selected_brand} — Top {len(bar_data)} Models by Listings",
                template="plotly_dark",
                color="Listings",
                color_continuous_scale=[[0,"#0cc0ee"],[0.5,"#58a6ff"],[1,"#f0c040"]],
                text="Listings"  # Add labels on top of bars
            )
            fig_bm.update_traces(textposition="outside", textfont=dict(color="#e6edf3", size=12))
            fig_bm.update_layout(
                **layout_bm,
                height=max(350,len(bar_data)*32+80),
                coloraxis_showscale=False,
                margin=dict(t=40,b=20,l=10,r=60)
            )
            
        else:
            model_order = bm_filtered.groupby("Model")["Price"].median().sort_values(ascending=True).index.tolist()
            #Horizontal box plot — price spread per model, sorted by median price
            fig_bm = px.box(
                bm_filtered,
                x="Price",
                y="Model",
                orientation="h",
                title=f"{selected_brand} — Price Distribution for Top {len(model_order)} Models (LKR M)",
                template="plotly_dark",
                color="Model",
                color_discrete_sequence=px.colors.qualitative.Bold,
                category_orders={"Model": model_order}
            )
            fig_bm.update_layout(
                **layout_bm,
                height=max(350,len(model_order)*32+80),
                showlegend=False,
                margin=dict(t=40,b=20,l=10,r=20)
            )
        
        st.plotly_chart(fig_bm, use_container_width=True)

    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.metric(f"{selected_brand} Models", bm_filtered["Model"].nunique())
    sm2.metric("Total Listings", f"{len(bm_filtered):,}")
    sm3.metric("Avg Price (LKR Lakhs)", f"{bm_filtered['Price'].mean():.1f}" if len(bm_filtered) > 0 else "N/A")
    sm4.metric("Median Price (LKR Lakhs)", f"{bm_filtered['Price'].median():.1f}" if len(bm_filtered) > 0 else "N/A")


    # Limitations section
    st.markdown("""
    <div style="height:4px;background:linear-gradient(90deg,transparent,#d4af37,#f0c040,#d4af37,transparent);margin:40px 0;border-radius:5px;"></div>
    """, unsafe_allow_html=True)

    st.markdown("## ⚠️ Limitations")

    st.markdown("""
    <div style="background-color:#1f2937;padding:20px;border-radius:12px;border-left:6px solid #f0c040;color:#e6edf3;font-size:13px;">
    <ul>
    <li>Data is based on online listings and may not reflect final transaction prices(LKR Lakhs).</li>
    <li>Some provinces may have fewer listings, affecting median reliability.</li>
    <li>Market conditions (import bans, tax policies) may influence prices(LKR Lakhs).</li>
    <li><b>Vehicle prices displayed DO NOT include government taxes, registration fees, transfer costs, insurance, or other additional charges.</b></li>
    <li>Dataset may not include all vehicle brands available in Sri Lanka.</li>
    <li>Engine size is represented in CC (cubic centimeters).</li>
    <li>Mileage is represented in Kilometers (KM).</li>
    <li><b>Engine Segmentation:</b> Vehicles are categorized into fixed groups based on engine capacity (CC). Users cannot adjust these ranges in the current version of the app. The categories are: 
        <ul>
            <li><b>Micro:</b> Less than 800cc</li>
            <li><b>Compact:</b> 800cc to 1200cc</li>
            <li><b>Mid-Range:</b> 1200cc to 1600cc</li>
            <li><b>Large:</b> Greater than 1600cc</li>
            <li><b>Unknown:</b> Missing or unavailable engine capacity data</li>
        </ul>
    </li>
    <li>Some features like Air Conditioning, Power Steering, Power Mirrors, and Power Windows are marked as Available or Not Available. Data may not capture partially functional or missing features.</li>
    <li>Vehicle age is calculated as the difference between the current year (2026) and the Year of Manufacture (YOM). Some vehicles may have uncertain manufacturing dates.</li>
    <li>Data cleaning removed duplicates and rows with missing critical values; therefore, some listings may not be represented.</li>
    <li>All analysis assumes listed prices and features are accurate at the time of scraping.</li>
    <li>Some vehicle modifications, import histories, or accident records are not included in this dataset.</li>
    <li>The app does not account for seasonal demand fluctuations or dealer promotions which may affect prices.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)