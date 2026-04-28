#s16798
#price prediction function
#Cluster Analysis Section 


import os
import pickle
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

#File paths for model and diagnostic pickle files
_ROOT            = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH       = os.path.join(_ROOT, "best_model.pkl")
DIAGNOSTICS_PATH = os.path.join(_ROOT, "model_diagnostics.pkl")
FACTOR_PATH      = os.path.join(_ROOT, "factor_analysis_results.pkl")

#Shared Plotly layout applied to every chart for visual consistency
GOLD = "#f0c040"
BLUE = "#58a6ff"
PLOT_LAYOUT = dict(
    paper_bgcolor="#0d1117",
    plot_bgcolor="#111827",
    font_color="#e6edf3",
    font_family="DM Sans",
    title_font_color="#f0c040",
    title_font_size=14,
    legend=dict(bgcolor="#161d2e", bordercolor="#1e2a3a", borderwidth=1),
    xaxis=dict(gridcolor="#1e2a3a", zerolinecolor="#1e2a3a"),
    yaxis=dict(gridcolor="#1e2a3a", zerolinecolor="#1e2a3a"),
)

#Cached loaders — only read from disk once per session
#Streamlit loads the file once on first run, stores it in memory, and reuses it every time after

#Loads the trained best model from disk; returns None if file missing
@st.cache_resource
def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)

#Loads model diagnostics (metrics, residuals, SHAP); returns None if missing
@st.cache_resource
def load_diagnostics():
    if not os.path.exists(DIAGNOSTICS_PATH):
        return None
    with open(DIAGNOSTICS_PATH, "rb") as f:
        return pickle.load(f)

## Loads FAMD + K-Means cluster analysis results; returns None if missing
@st.cache_data
def load_factor_results():
    if not os.path.exists(FACTOR_PATH):
        return None
    with open(FACTOR_PATH, "rb") as f:
        return pickle.load(f)

#function definition
def page_regression(df):
    st.markdown("<div class='page-title'>📈 Car Price Prediction</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Enter vehicle details to get an instant price estimate.</div>",
        unsafe_allow_html=True,
    )

    #Load model & diagnostics
    model       = load_model()
    diagnostics = load_diagnostics()

    if model is None:
        st.error(
            "⚠️ `best_model.pkl` not found.\n\n"
            "Run training first:\n"
            "```bash\n"
            "python train_model.py\n"
            "```"
        )
        return

    #Rare-category grouping — must match train_model.py exactly
    # Categories with fewer than 20 listings are collapsed into "Other"
    # to match how the model was trained and avoid unseen-category errors

    THRESHOLD = 20
    df = df.copy()

    brand_counts    = df["Brand"].value_counts()
    df["Brand"]     = df["Brand"].where(
        df["Brand"].isin(brand_counts[brand_counts >= THRESHOLD].index), other="Other")

    model_counts    = df["Model"].value_counts()
    df["Model"]     = df["Model"].where(
        df["Model"].isin(model_counts[model_counts >= THRESHOLD].index), other="Other")

    fuel_counts     = df["Fuel Type"].value_counts()
    df["Fuel Type"] = df["Fuel Type"].where(
        df["Fuel Type"].isin(fuel_counts[fuel_counts >= THRESHOLD].index), other="Other")

    #Vehicle Selection Process banner
    st.markdown(
        f"""
        <div style="
            background:#111827;
            border:1px solid #1e2a3a;
            border-radius:12px;
            padding:18px 22px;
            margin-bottom:20px;
        ">
            <div style="color:{GOLD};font-size:16px;font-weight:600;margin-bottom:10px;">
                🔎 Vehicle Selection Process
            </div>
            <div style="color:#e6edf3;font-size:14px;margin-bottom:12px;">
                The selection fields follow a <b>step-by-step filtering system</b> to ensure
                only valid vehicle configurations are displayed.
            </div>
            <div style="
                display:flex;
                justify-content:space-between;
                align-items:center;
                text-align:center;
                font-size:13px;
                margin-top:10px;
            ">
                <div>
                    <div style="color:{GOLD};font-weight:600;">1️⃣ Brand</div>
                    <div style="color:#7d8590;">Select a car brand</div>
                </div>
                <div style="color:{BLUE};font-size:18px;">&#10132;</div>
                <div>
                    <div style="color:{GOLD};font-weight:600;">2️⃣ Model</div>
                    <div style="color:#7d8590;">Models filtered by brand</div>
                </div>
                <div style="color:{BLUE};font-size:18px;">&#10132;</div>
                <div>
                    <div style="color:{GOLD};font-weight:600;">3️⃣ Fuel &amp; Gear</div>
                    <div style="color:#7d8590;">Options filtered by model</div>
                </div>
                <div style="color:{BLUE};font-size:18px;">&#10132;</div>
                <div>
                    <div style="color:{GOLD};font-weight:600;">4️⃣ Vehicle Details</div>
                    <div style="color:#7d8590;">Mileage, Engine, Features</div>
                </div>
                <div style="color:{BLUE};font-size:18px;">&#10132;</div>
                <div>
                    <div style="color:{GOLD};font-weight:600;">5️⃣ Price Prediction</div>
                    <div style="color:#7d8590;">ML model estimates price</div>
                </div>
            </div>
            <div style="margin-top:12px;color:#7d8590;font-size:12px;">
                This prevents impossible combinations such as selecting a fuel type or
                transmission that does not exist for the selected vehicle model.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    #User Inputs
    col1, col2, col3 = st.columns(3)

    with col1:

        #Brand dropdown - drives model filter below
        brand_list = sorted(df["Brand"].dropna().unique())
        p_brand    = st.selectbox("Brand", brand_list, key="reg_brand")
        brand_df   = df[df["Brand"] == p_brand]

        model_list = sorted(brand_df["Model"].dropna().unique())
        p_model    = st.selectbox("Model", model_list, key="reg_model")

        p_yom    = st.number_input("Year of Manufacture", min_value=2000, max_value=2026, value=2018, key="reg_yom")
        p_engine = st.number_input("Engine (cc)",         min_value=600,  max_value=5000, value=1500, key="reg_engine")

    with col2:
        #Fuel and gear dropdowns - filtered by selected brand and model
        model_df   = brand_df[brand_df["Model"] == p_model]

        fuel_list  = sorted(model_df["Fuel Type"].dropna().unique())
        p_fuel     = st.selectbox("Fuel Type",    fuel_list, key="reg_fuel")

        gear_list  = sorted(model_df["Gear"].dropna().unique())
        p_gear     = st.selectbox("Transmission", gear_list, key="reg_gear")

        p_mileage  = st.number_input("Mileage (KM)", min_value=0, max_value=500_000, value=80_000, key="reg_mileage")

        prov_list  = sorted(df["Province"].dropna().unique())
        p_province = st.selectbox("Province", prov_list, key="reg_province")

    with col3:
        # Condition, leasing, and binary feature checkboxes

        p_leasing   = st.selectbox("Leasing",   ["Yes", "No Leasing"],  key="reg_leasing")
        p_condition = st.selectbox("Condition", ["NEW", "Used"],         key="reg_condition")
        p_ac = st.checkbox("AIR CONDITION",  value=True, key="reg_ac")
        p_ps = st.checkbox("POWER STEERING", value=True, key="reg_ps")
        p_pm = st.checkbox("POWER MIRROR",   value=True, key="reg_pm")
        p_pw = st.checkbox("POWER WINDOW",   value=True, key="reg_pw")

    #Age is calculated but excluded from the model due to perfect multicollinearity
    p_age = 2026 - p_yom

    st.markdown(
        f"<div class='insight-box'>"
        f"<strong>Age of Vehicle:</strong> {p_age} years &nbsp;|&nbsp;"
        f"<span style='color:#7d8590;font-size:0.85rem;'>"
        f"&#9432; Excluded from modeling — perfect multicollinearity with Mileage (r&nbsp;=&nbsp;1.0)"
        f"</span></div>",
        unsafe_allow_html=True,
    )

    #Build input row
    # Encodes user inputs into the exact feature format the model expects
    user_input = pd.DataFrame([{
        "Fuel Type":          p_fuel,
        "Province":           p_province,
        "Engine (cc)":        p_engine,
        "Millage(KM)":        p_mileage,
        "Gear_bin":           1 if p_gear    == "Automatic"  else 0,
        "Leasing_bin":        1 if p_leasing != "No Leasing" else 0,
        "AIR CONDITION_bin":  int(p_ac),
        "POWER STEERING_bin": int(p_ps),
        "POWER MIRROR_bin":   int(p_pm),
        "POWER WINDOW_bin":   int(p_pw),
        "Condition_bin":      1 if p_condition == "NEW" else 0,
    }])

    # Run model prediction
    pred_price = model.predict(user_input)[0]


    # Displays estimated price prominently in a styled card
    st.markdown(
        f"""
        <div style='
            background: linear-gradient(135deg, #1a2e1a, #0f1722);
            border: 1px solid {GOLD};
            border-radius: 12px;
            padding: 24px 32px;
            margin-top: 20px;
            text-align: center;
        '>
            <div style='color:#e6edf3;font-size:14px;margin-bottom:6px;'>Estimated Price</div>
            <div style='color:{GOLD};font-size:38px;font-weight:700;'>
                LKR {pred_price:.2f} Lakhs
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    #Input summary table
    #Shows all selected inputs in a transposed table for easy review
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🔍 Input Summary</div>", unsafe_allow_html=True)
    summary = pd.DataFrame([{
        "Brand":          p_brand,
        "Model":          p_model,
        "Year (YOM)":     p_yom,
        "Age (yrs)":      p_age,
        "Engine (cc)":    p_engine,
        "Mileage (KM)":   f"{p_mileage:,}",
        "Fuel Type":      p_fuel,
        "Transmission":   p_gear,
        "Province":       p_province,
        "Leasing":        p_leasing,
        "Condition":      p_condition,
        "AIR CONDITION":  "Available" if p_ac else "Not Available",
        "POWER STEERING": "Available" if p_ps else "Not Available",
        "POWER MIRROR":   "Available" if p_pm else "Not Available",
        "POWER WINDOW":   "Available" if p_pw else "Not Available",
    }]).T.reset_index()
    summary.columns = ["Feature", "Value"]
    st.dataframe(summary, use_container_width=True, hide_index=True)

    # Diagnostics
    if diagnostics is None:
        st.info("ℹ️ Run `train_model.py` to generate model diagnostic charts.")
        return

    best_name = diagnostics["best_model_name"]
    y_test    = diagnostics["y_test"]
    y_pred    = diagnostics["y_test_pred"]
    residuals = diagnostics["residuals"]
    shap_df   = diagnostics["shap_importance"]
    metrics   = diagnostics["metrics"]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='section-header'>📊 Model Diagnostics — {best_name}</div>",
        unsafe_allow_html=True,
    )

    # Shows Train/Test R² and RMSE to assess model fit and generalisation
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Train R²",   f"{metrics['Train_R2']:.4f}")
    m2.metric("Test R²",    f"{metrics['Test_R2']:.4f}")
    m3.metric("Train RMSE", f"{metrics['Train_RMSE']:.4f}")
    m4.metric("Test RMSE",  f"{metrics['Test_RMSE']:.4f}")

    st.markdown("<br>", unsafe_allow_html=True)
    if "all_results" in diagnostics:
        with st.expander("📊 Compare All Models (Train/Test R² & RMSE)"):
            model_table = pd.DataFrame(diagnostics["all_results"]).T.reset_index()
            model_table.rename(columns={"index": "Model"}, inplace=True)
            model_table = model_table[["Model", "Train_R2", "Test_R2", "Train_RMSE", "Test_RMSE"]]
            st.dataframe(
                model_table.style.format({
                    "Train_R2": "{:.4f}", "Test_R2": "{:.4f}",
                    "Train_RMSE": "{:.2f}", "Test_RMSE": "{:.2f}",
                }),
                use_container_width=True,
                hide_index=True,
            )

    #Actual vs Predicted  +  Residual scatter plots
    ch1, ch2 = st.columns(2)

    with ch1:
        st.markdown("<div class='section-header'>📈 Actual vs Predicted Car Price</div>", unsafe_allow_html=True)
        st.markdown(
            """<div style='color:#7d8590;font-size:13px;margin-bottom:6px;'>
            This chart compares the <b>actual car prices</b> from the test dataset with the
            <b>prices predicted by the machine learning model</b>.
            Points closer to the dashed line indicate more accurate predictions.
            </div>""",
            unsafe_allow_html=True,
        )
        fig_ap = go.Figure()
        fig_ap.add_trace(go.Scatter(
            x=y_test, y=y_pred,
            mode="markers",
            marker=dict(color=GOLD, size=5, opacity=0.5),
            name="Predictions",
        ))
        min_val = float(min(y_test.min(), y_pred.min()))
        max_val = float(max(y_test.max(), y_pred.max()))
        fig_ap.add_trace(go.Scatter(
            x=[min_val, max_val], y=[min_val, max_val],
            mode="lines",
            line=dict(color=BLUE, dash="dash", width=1.5),
            name="Perfect Fit",
        ))
        fig_ap.update_layout(
            **PLOT_LAYOUT, height=370,
            title="Actual vs Predicted Car Price",
            xaxis_title="Actual Price (LKR M)",
            yaxis_title="Predicted Price (LKR M)",
        )
        st.plotly_chart(fig_ap, use_container_width=True)

    with ch2:
        st.markdown("<div class='section-header'>📉 Residual Analysis</div>", unsafe_allow_html=True)
        st.markdown(
            """<div style='color:#7d8590;font-size:13px;margin-bottom:6px;'>
            Residuals represent the difference between the <b>actual price</b> and the
            <b>predicted price</b>.
            If the model performs well, the points should be randomly distributed around zero.
            </div>""",
            unsafe_allow_html=True,
        )
        fig_res = go.Figure()
        fig_res.add_trace(go.Scatter(
            x=y_pred, y=residuals,
            mode="markers",
            marker=dict(color=BLUE, size=5, opacity=0.5),
            name="Residuals",
        ))
        fig_res.add_hline(y=0, line_color=GOLD, line_dash="dash", line_width=1.5)
        fig_res.update_layout(
            **PLOT_LAYOUT, height=370,
            title="Residual Analysis",
            xaxis_title="Predicted Price (LKR M)",
            yaxis_title="Residual (Actual - Predicted)",
        )
        st.plotly_chart(fig_res, use_container_width=True)

    #Residual distribution histogram 
    st.markdown("<div class='section-header'>📊 Residual Distribution</div>", unsafe_allow_html=True)
    st.markdown(
        """<div style='color:#7d8590;font-size:13px;margin-bottom:6px;'>
        This histogram shows how prediction errors are distributed.
        A well-performing model usually produces residuals centered around zero,
        indicating balanced over- and under-predictions.
        </div>""",
        unsafe_allow_html=True,
    )
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=residuals, nbinsx=50,
        marker_color=BLUE, opacity=0.8, name="Residuals",
    ))
    fig_hist.add_vline(x=0, line_color=GOLD, line_dash="dash", line_width=1.5)
    fig_hist.update_layout(
        **PLOT_LAYOUT, height=300,
        title="Residual Distribution",
        xaxis_title="Residual (Actual - Predicted)",
        yaxis_title="Count",
        bargap=0.05,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    #SHAP Feature Importance
    st.markdown(
        "<div class='section-header'>🔑 Feature Importance (SHAP — Mean |SHAP Value|)</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        """<div style='color:#7d8590;font-size:13px;margin-bottom:6px;'>
        SHAP values measure how much each feature contributes to the model's predictions.
        Features with higher importance have a stronger influence on the predicted car price.
        </div>""",
        unsafe_allow_html=True,
    )
    shap_top = shap_df.head(20).sort_values("Importance", ascending=True)
    fig_shap = go.Figure()
    fig_shap.add_trace(go.Bar(
        x=shap_top["Importance"],
        y=shap_top["Feature"],
        orientation="h",
        marker=dict(
            color=shap_top["Importance"],
            colorscale=[[0, "#1e2a3a"], [0.5, BLUE], [1, GOLD]],
            showscale=False,
        ),
    ))
    fig_shap.update_layout(
        **PLOT_LAYOUT,
        height=max(380, len(shap_top) * 24),
        xaxis_title="Mean |SHAP Value|",
        yaxis_title="",
        margin=dict(l=10, r=20, t=10, b=40),
    )
    st.plotly_chart(fig_shap, use_container_width=True)

    with st.expander("📋 Full SHAP Importance Table"):
        st.dataframe(
            shap_df.style.background_gradient(subset=["Importance"], cmap="YlOrBr"),
            use_container_width=True,
            hide_index=True,
        )

    
   # CLUSTER ANALYSIS — collapsible section at the bottom
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style="
            background:#111827;
            border:1px solid #1e2a3a;
            border-radius:12px;
            padding:16px 22px;
            margin-bottom:4px;
        ">
            <div style="color:{GOLD};font-size:16px;font-weight:600;">
                🔬 Cluster Analysis (FAMD + K-Means)
            </div>
            <div style="color:#7d8590;font-size:13px;margin-top:6px;">
                Unsupervised market segmentation using Factor Analysis of Mixed Data (FAMD) 
                followed by K-Means clustering. Expand the sections below to explore results.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    factor = load_factor_results()

    if factor is None:
        with st.expander("🔬 View Cluster Analysis", expanded=False):
            st.warning(
                "⚠️ `factor_analysis_results.pkl` not found.\n\n"
                "Run the analysis first:\n"
                "```bash\n"
                "cd C:\\Users\\MCS\\Desktop\\st\n"
                "python factor_analysis.py\n"
                "```"
            )
    else:
        # Unpack
        eigenvalues                   = factor["eigenvalues"]
        explained_variance_ratio      = factor["explained_variance_ratio"]
        cumulative_explained_variance = factor["cumulative_explained_variance"]
        n_kaiser   = factor["n_kaiser"]
        n_90       = factor["n_90"]
        n_95       = factor["n_95"]
        n_features = factor["n_features"]
        best_k     = factor["best_k"]
        sil_scores = factor["silhouette_scores"]
        cluster_res = factor["cluster_results"]

        # FAMD Overview
        with st.expander("📐 FAMD Factor Analysis — Scree & Variance", expanded=False):
            st.markdown(
                """<div style='color:#7d8590;font-size:13px;margin-bottom:12px;'>
                FAMD reduces the mixed (numerical + categorical) feature space into orthogonal
                factors. The scree plot shows each factor's eigenvalue; factors above the red
                dashed line (Kaiser criterion λ&nbsp;&gt;&nbsp;1) carry meaningful variance.
                </div>""",
                unsafe_allow_html=True,
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Observations",       f"{factor['n_rows']:,}")
            c2.metric("Kaiser Components",  n_kaiser, help="Eigenvalue > 1")
            c3.metric("Components @ 90%",   n_90)
            c4.metric("Components @ 95%",   n_95)

            st.image(factor["scree_png"], use_container_width=True)

            with st.expander("📋 Eigenvalue Table", expanded=False):
                ev_df = pd.DataFrame({
                    "Component":              range(1, len(eigenvalues) + 1),
                    "Eigenvalue (λ)":         np.round(eigenvalues, 4),
                    "Variance Explained (%)": np.round(explained_variance_ratio * 100, 2),
                    "Cumulative (%)":         np.round(cumulative_explained_variance * 100, 2),
                })
                ev_df["Kaiser (λ>1)"] = ev_df["Eigenvalue (λ)"] > 1
                st.dataframe(ev_df, use_container_width=True, hide_index=True)

        # Score Plot
        with st.expander("📍 FAMD Score Plot (Factor 1 vs Factor 2)", expanded=False):
            st.markdown(
                f"""<div style='color:#7d8590;font-size:13px;margin-bottom:12px;'>
                Each point is one car listing projected onto the first two FAMD components.
                Factor&nbsp;1 explains <b>{explained_variance_ratio[0]*100:.2f}%</b> of variance;
                Factor&nbsp;2 explains <b>{explained_variance_ratio[1]*100:.2f}%</b>.
                Clusters of points suggest natural market segments.
                </div>""",
                unsafe_allow_html=True,
            )
            st.image(factor["score_png"], use_container_width=True)

            if factor.get("column_coordinates") is not None:
                with st.expander("📋 Feature Loadings on Factor 1 & Factor 2", expanded=False):
                    cc = factor["column_coordinates"]
                    if hasattr(cc, "iloc"):
                        load_df = cc.iloc[:, :2].copy()
                        load_df.columns = ["Factor 1", "Factor 2"]
                        load_df = load_df.round(4).sort_values("Factor 1", ascending=False)
                        st.dataframe(load_df, use_container_width=True)

        # Silhouette score line
        with st.expander("📊 Silhouette Score vs Number of Clusters (k = 2…10)", expanded=False):
            st.markdown(
                """<div style='color:#7d8590;font-size:13px;margin-bottom:12px;'>
                The silhouette score measures how well each listing fits its assigned cluster
                (range −1 to +1; higher is better). The peak indicates the optimal number
                of clusters.
                </div>""",
                unsafe_allow_html=True,
            )

            sil_col1, sil_col2 = st.columns([2, 1])
            with sil_col1:
                st.image(factor["sil_line_png"], use_container_width=True)
            with sil_col2:
                best_idx = int(np.argmax(sil_scores))
                sil_df = pd.DataFrame({
                    "k":                range(2, 2 + len(sil_scores)),
                    "Silhouette Score": np.round(sil_scores, 4),
                })
                st.dataframe(
                    sil_df.style.highlight_max(
                        subset=["Silhouette Score"], color="#2a3f2a"
                    ),
                    use_container_width=True,
                    hide_index=True,
                )
                st.success(
                    f"**Best k = {best_k}**\n\n"
                    f"Score = {sil_scores[best_idx]:.4f}"
                )

        # Per-k cluster viewer
        with st.expander("🗂️ Cluster & Silhouette Plots by k", expanded=False):
            st.markdown(
                """<div style='color:#7d8590;font-size:13px;margin-bottom:12px;'>
                Use the slider to select a cluster solution. The left panel shows how
                listings are grouped in FAMD space; the right panel shows per-cluster
                silhouette widths — wider and more uniform bars indicate better-separated clusters.
                </div>""",
                unsafe_allow_html=True,
            )

            k_values   = [r["k"] for r in cluster_res]
            selected_k = st.select_slider(
                "Select number of clusters (k)",
                options=k_values,
                value=best_k,
                key="cluster_k_slider",
            )

            sel = next(r for r in cluster_res if r["k"] == selected_k)

            scatter_col, sil_col = st.columns(2)
            with scatter_col:
                st.markdown(
                    f"<div style='color:{GOLD};font-weight:600;margin-bottom:4px;'>"
                    f"Cluster Scatter — k = {selected_k}</div>",
                    unsafe_allow_html=True,
                )
                st.image(sel["scatter_png"], use_container_width=True)

            with sil_col:
                st.markdown(
                    f"<div style='color:{GOLD};font-weight:600;margin-bottom:4px;'>"
                    f"Silhouette Plot — k = {selected_k} &nbsp;"
                    f"<span style='color:#7d8590;font-weight:400;'>"
                    f"(score = {sel['sil_score']:.4f})</span></div>",
                    unsafe_allow_html=True,
                )
                st.image(sel["silhouette_png"], use_container_width=True)

            # Cluster size summary
            labels   = sel["cluster_labels"]
            size_df  = (
                pd.Series(labels, name="Cluster")
                .value_counts()
                .sort_index()
                .reset_index()
            )
            size_df.columns = ["Cluster", "Count"]
            size_df["Share (%)"] = (
                size_df["Count"] / size_df["Count"].sum() * 100
            ).round(1)

            st.markdown(
                f"<div style='color:{GOLD};font-weight:600;margin-top:16px;margin-bottom:4px;'>"
                f"Cluster Size Summary — k = {selected_k}</div>",
                unsafe_allow_html=True,
            )
            st.dataframe(size_df, use_container_width=True, hide_index=True)

        # All-k compact grid
        with st.expander("🔲 All-k Cluster Overview", expanded=False):
            st.markdown(
                """<div style='color:#7d8590;font-size:13px;margin-bottom:12px;'>
                Scatter plots for all tested values of k shown side-by-side for quick
                visual comparison.
                </div>""",
                unsafe_allow_html=True,
            )
            cols_per_row = 3
            rows = [
                cluster_res[i : i + cols_per_row]
                for i in range(0, len(cluster_res), cols_per_row)
            ]
            for row in rows:
                cols = st.columns(cols_per_row)
                for col, r in zip(cols, row):
                    with col:
                        label_color = GOLD if r["k"] == best_k else "#e6edf3"
                        st.markdown(
                            f"<div style='color:{label_color};font-weight:600;font-size:13px;"
                            f"margin-bottom:2px;'>k = {r['k']} &nbsp;"
                            f"<span style='color:#7d8590;font-weight:400;'>"
                            f"sil = {r['sil_score']:.3f}</span>"
                            f"{'&nbsp; ⭐' if r['k'] == best_k else ''}</div>",
                            unsafe_allow_html=True,
                        )
                        st.image(r["scatter_png"], use_container_width=True)
        # Interpretation & Study Decision
        with st.expander("📝 Cluster Interpretation & Study Decision", expanded=False):
            st.markdown(
                """<div style='color:#7d8590;font-size:13px;margin-bottom:16px;'>
                Interpretation of silhouette scores and the rationale behind the modelling 
                approach taken in this study.
                </div>""",
                unsafe_allow_html=True,
            )

            # Silhouette score interpretation table
            st.markdown(
                f"<div style='color:{GOLD};font-weight:600;margin-bottom:8px;'>📊 Silhouette Score Interpretation Guide</div>",
                unsafe_allow_html=True,
            )

            interp_df = pd.DataFrame({
                "Silhouette Score Range": ["0.71 – 1.00", "0.51 – 0.70", "0.26 – 0.50", "< 0.25"],
                "Interpretation":        ["Strong structure", "Reasonable structure", "Weak structure", "No substantial structure"],
                "Cluster Quality":       ["✅ Excellent", "🟡 Good", "🟠 Fair", "🔴 Poor"],
            })
            st.dataframe(interp_df, use_container_width=True, hide_index=True)

            # Current study score callout
            best_idx   = int(np.argmax(sil_scores))
            best_score = sil_scores[best_idx]

            if best_score >= 0.71:
                quality, color, emoji = "Strong", "#2a3f2a", "✅"
            elif best_score >= 0.51:
                quality, color, emoji = "Reasonable", "#3a3a1a", "🟡"
            elif best_score >= 0.26:
                quality, color, emoji = "Weak", "#3a2a1a", "🟠"
            else:
                quality, color, emoji = "No Substantial", "#3a1a1a", "🔴"

            st.markdown(
                f"""
                <div style="
                    background:{color};
                    border-radius:10px;
                    padding:14px 18px;
                    margin:14px 0;
                ">
                    <div style="color:#e6edf3;font-size:14px;">
                        {emoji} <b>This study's best silhouette score: {best_score:.4f} (k = {best_k})</b>
                        — indicates <b>{quality} cluster structure</b> in the vehicle dataset.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            # Study decision
            st.markdown(
                f"<div style='color:{GOLD};font-weight:600;margin-bottom:8px;'>🎯 Modelling Decision</div>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"""
                <div style="
                    background:#111827;
                    border-left:3px solid {GOLD};
                    border-radius:0 8px 8px 0;
                    padding:14px 18px;
                    color:#e6edf3;
                    font-size:13px;
                    line-height:1.7;
                ">
                    Despite the cluster structure identified above, <b>this study does not segment 
                    vehicles into separate clusters for regression modelling.</b><br><br>
                    Instead, a <b>single unified regression model is fitted across all vehicles</b> 
                    in the dataset. This decision was made for the following reasons:
                    <ul style="margin-top:10px;margin-bottom:0;padding-left:20px;color:#7d8590;">
                        <li>The silhouette score suggests the cluster boundaries are not strong 
                            enough to justify splitting the dataset and reducing sample size per model.</li>
                        <li>A global model captures market-wide pricing dynamics without 
                            overfitting to segment-specific noise.</li>
                        <li>Cluster labels are retained as an exploratory diagnostic only — 
                            they inform our understanding of market segments but do not drive 
                            the predictive pipeline.</li>
                    </ul>
                </div>
                """,
                unsafe_allow_html=True,
            )