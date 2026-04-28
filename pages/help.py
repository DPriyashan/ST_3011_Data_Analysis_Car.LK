import streamlit as st

"""
s16798
Help and FAQ section Here, you’ll find answers to common questions and tips for using the app efficiently.
Click the arrow next to any question to reveal the answer.
You can also use the search box to quickly find topics like price, model, or province.
Here you can find answers about searching and filtering cars by brand, model, price, and features.
Charts show listing counts and price distributions, while prices are listed in LKR LKHS.
Province and engine features are shown, and vehicle age is calculated from the year of manufacture.
Use the Data Explorer for interactive filtering and the Car Price Prediction page for price estimates.
This concludes the Help section.
"""

GOLD = "#f0c040"
BLUE = "#58a6ff"


# ── FAQ data ───────────────────────────────────────────────────────────────────
FAQ_SECTIONS = [
    {
        "icon": "🔍",
        "title": "Filters & Search",
        "questions": [
            {
                "q": "How do I search for a specific car brand and model?",
                "a": (
                    "Use the **Brand** dropdown to select your preferred brand. "
                    "The **Model** dropdown will automatically update to show only models "
                    "available for that brand. You can also tick **All Brands** or **All Models** "
                    "to include everything in the dataset."
                ),
            },
            {
                "q": "What does the 'All Brands' / 'All Models' checkbox do?",
                "a": (
                    "Ticking **All Brands** overrides the brand dropdown and includes every brand "
                    "in the dataset. Similarly, **All Models** includes every model for the currently "
                    "selected brand(s). This is useful when you want a market-wide view rather than "
                    "filtering to a specific vehicle."
                ),
            },
            {
                "q": "Why does the Model dropdown change when I select a Brand?",
                "a": (
                    "The Model dropdown is dynamically filtered to only show models that exist "
                    "for the selected brand. This prevents invalid brand–model combinations "
                    "(e.g. a Toyota Civic does not exist). When you change the brand, the model "
                    "list refreshes automatically."
                ),
            },
            {
                "q": "Why is the Price slider different for each selection?",
                "a": (
                    "The price slider range is calculated from the **minimum and maximum prices "
                    "within your current filtered selection**. If you select only Hybrid Toyotas, "
                    "for example, the slider will reflect only their price range — not the full "
                    "dataset range. This keeps the slider useful and precise for your selection."
                ),
            },
            {
                "q": "Why is there no slider when only one price or year value exists?",
                "a": (
                    "A slider requires at least two distinct values to define a range. If your "
                    "current filter results in all listings having the same price or year "
                    "(e.g. you selected a very specific model with one listing), "
                    "the app displays the fixed value as text instead of a slider."
                ),
            },
        ],
    },
    {
        "icon": "📊",
        "title": "Charts & Tables",
        "questions": [
            {
                "q": "What is the difference between 'Bar – Listing Count' and 'Box – Price per Model'?",
                "a": (
                    "**Bar – Listing Count** shows how many listings exist for each model — useful "
                    "for understanding popularity and availability.\n\n"
                    "**Box – Price per Model** shows the full price distribution for each model using "
                    "a box plot. The box represents the middle 50% of prices (25th to 75th percentile), "
                    "the line inside is the median, and the whiskers extend to min/max (excluding outliers shown as dots)."
                ),
            },
            {
                "q": "What does the box plot show — is it the actual price or average price?",
                "a": (
                    "The box plot shows the **full price distribution**, not just the average. "
                    "The centre line is the **median** (middle value), which is more reliable than "
                    "the average when there are expensive outliers. The box spans the interquartile "
                    "range (IQR), and dots outside the whiskers represent unusually high or low prices."
                ),
            },
            {
                "q": "Why does the categorical distribution only show the top 10 values?",
                "a": (
                    "Some columns like Brand or Model can have 50+ unique values. Displaying all of "
                    "them would make the chart unreadable. The **top 10 by count** gives you the most "
                    "meaningful overview. If you need to explore a specific value not in the top 10, "
                    "use the filters above to narrow your selection first."
                ),
            },
            {
                "q": "What does the 'Engine Segment' column mean in the table?",
                "a": (
                    "Engine Segment groups vehicles by engine capacity (CC) into fixed categories:\n\n"
                    "- **Micro** — Less than 800cc\n"
                    "- **Compact** — 800cc to 1,200cc\n"
                    "- **Mid-Range** — 1,200cc to 1,600cc\n"
                    "- **Large** — Greater than 1,600cc\n"
                    "- **Unknown** — Engine capacity is missing or unavailable\n\n"
                    "These ranges cannot be adjusted in the current version of the app."
                ),
            },
        ],
    },
    {
        "icon": "💰",
        "title": "Price & Data Interpretation",
        "questions": [
            {
                "q": "Are the prices the final selling price or the listed asking price?",
                "a": (
                    "All prices are **listed asking prices** scraped from online car marketplaces. "
                    "They reflect what sellers are asking at the time of data collection — not the "
                    "final negotiated transaction price. Actual sale prices may be lower after negotiation."
                ),
            },
            {
                "q": "Does the price include taxes, registration, and insurance?",
                "a": (
                    "**No.** The displayed prices are the listed vehicle prices only. They do **not** "
                    "include government taxes, registration fees, transfer costs, insurance premiums, "
                    "or any other additional charges. Always factor in these costs when budgeting "
                    "for a vehicle purchase."
                ),
            },
            {
                "q": "Why does the same model have very different prices?",
                "a": (
                    "Multiple factors cause price variation within the same model:\n\n"
                    "- **Year of Manufacture** — newer models cost more\n"
                    "- **Mileage** — lower mileage commands a premium\n"
                    "- **Condition** — New, Reconditioned, and Used all differ\n"
                    "- **Features** — A/C, automatic gear, power windows etc. add value\n"
                    "- **Province** — demand and supply vary by location\n"
                    "- **Seller pricing** — some sellers price above or below market"
                ),
            },
            {
                "q": "Why is the average price sometimes much higher than the median?",
                "a": (
                    "A few very expensive listings (luxury cars, supercars, or data entry errors) "
                    "can pull the **average** (mean) significantly upward. The **median** is the "
                    "middle value and is not affected by extremes — it is a better representation "
                    "of what a 'typical' listing costs. Always use the median for a realistic "
                    "market benchmark."
                ),
            },
        ],
    },
    {
        "icon": "🗺️",
        "title": "Province & Location",
        "questions": [
            {
                "q": "How is Province determined — I don't see it in the filters?",
                "a": (
                    "Province is **derived from the Town column** using a predefined mapping. "
                    "The original dataset contains town-level location data, which is then grouped "
                    "into Sri Lanka's nine provinces. Province is shown in the results table and "
                    "used in the prediction model, but it is not a direct filter in the Data Explorer."
                ),
            },
            {
                "q": "Why is my town showing as 'Other' in Province?",
                "a": (
                    "The province mapping covers the most common towns in the dataset. If a town "
                    "was not in the mapping list (e.g. due to spelling variation or a less common "
                    "location), it is grouped under **'Other'**. This affects a small number of listings."
                ),
            },
            {
                "q": "Which towns are mapped to which province?",
                "a": (
                    "Here is the full town-to-province mapping used in the app:\n\n"
                    "- **Western** — Colombo, Gampaha, Negombo, Kalutara, Panadura, Moratuwa, "
                    "Dehiwala-Mount-Lavinia, Maharagama, Kotte, Wattala, Ja-Ela, Kelaniya, "
                    "Kadawatha, Nugegoda, Piliyandala, Boralesgamuwa\n"
                    "- **Central** — Kandy, Matale, Nuwara-Eliya, Gampola, Nawalapitiya, Hatton\n"
                    "- **Southern** — Galle, Matara, Hambantota, Weligama, Tangalle, Hikkaduwa, Ambalangoda\n"
                    "- **Northern** — Jaffna, Vavuniya, Kilinochchi, Mullaitivu\n"
                    "- **Eastern** — Batticaloa, Trincomalee, Ampara, Kalmunai\n"
                    "- **North Western** — Kurunegala, Puttalam, Kuliyapitiya, Chilaw\n"
                    "- **North Central** — Anuradapura, Polonnaruwa\n"
                    "- **Uva** — Badulla, Bandarawela, Haputale, Welimada\n"
                    "- **Sabaragamuwa** — Ratnapura, Kegalle, Balangoda\n"
                    "- **Other** — Any town not listed above"
                ),
            },
        ],
    },
    {
        "icon": "⚙️",
        "title": "Engine & Features",
        "questions": [
            {
                "q": "What are the engine segment categories and their CC ranges?",
                "a": (
                    "Vehicles are grouped into four fixed engine segments based on engine capacity:\n\n"
                    "| Segment | Engine Capacity |\n"
                    "|---|---|\n"
                    "| Micro | Less than 800cc |\n"
                    "| Compact | 800cc – 1,200cc |\n"
                    "| Mid-Range | 1,200cc – 1,600cc |\n"
                    "| Large | Greater than 1,600cc |\n"
                    "| Unknown | Missing data |\n\n"
                    "These thresholds are fixed and cannot be customised in the current version."
                ),
            },
            {
                "q": "What does 'Available' mean for Air Condition / Power Steering etc.?",
                "a": (
                    "**Available** means the feature was listed as present in the original vehicle "
                    "listing. **Not Available** means it was listed as absent or not mentioned. "
                    "The dataset does not capture partially functional features — a feature is "
                    "simply either Available or Not Available based on what the seller reported."
                ),
            },
        ],
    },
    {
        "icon": "📅",
        "title": "Age & Year",
        "questions": [
            {
                "q": "How is vehicle age calculated?",
                "a": (
                    "Vehicle age is calculated as: **Age = 2025 − Year of Manufacture (YOM)**. "
                    "For example, a car manufactured in 2018 has an age of 7 years. "
                    "The base year 2025 is fixed and does not update automatically."
                ),
            },
            {
                "q": "A car manufactured in December 2020 — is its age 4 or 5 years?",
                "a": (
                    "The app calculates age using only the **year**, not the specific month or day. "
                    "So a car with YOM 2020 will always show Age = 5, regardless of whether it was "
                    "manufactured in January or December 2020. This is a known simplification."
                ),
            },
            {
                "q": "Why do some cars have a YOM that seems too old or too new?",
                "a": (
                    "The YOM is taken directly from the seller's listing. Some listings may contain "
                    "data entry errors (e.g. YOM listed as 1990 for a modern car). The dataset "
                    "includes basic cleaning but does not validate every YOM entry against "
                    "the actual model release year."
                ),
            },
        ],
    },
    {
        "icon": "🔎",
        "title": "Data Quality",
        "questions": [
            {
                "q": "Why are some listings missing from the results?",
                "a": (
                    "During data cleaning, rows with **missing critical values** (price, brand, "
                    "model, mileage etc.) and **exact duplicate rows** are removed. This improves "
                    "data quality but means some listings are excluded. Additionally, brands or "
                    "models with fewer than 20 listings are grouped under 'Other' to ensure "
                    "statistical reliability."
                ),
            },
            {
                "q": "Why are there duplicate-looking listings for the same car?",
                "a": (
                    "The same car may be listed multiple times by the same seller (re-listed after "
                    "expiry) or by different sellers (e.g. dealers and private sellers). Only "
                    "**exact duplicate rows** are removed — listings with even one differing field "
                    "(e.g. slightly different price) are kept as separate entries."
                ),
            },
            {
                "q": "How recent is the data — when was it last updated?",
                "a": (
                    "The dataset was collected and fixed at the time of the project. It is "
                    "**not a live feed** and does not update automatically. Prices and availability "
                    "in the real market may have changed since the data was collected. "
                    "Always verify current prices on live platforms before making a purchase decision."
                ),
            },
            {
                "q": "Why does a brand I know exist in Sri Lanka not appear in the list?",
                "a": (
                    "Two possible reasons:\n\n"
                    "1. The brand had **fewer than 20 listings** in the dataset and was grouped "
                    "under **'Other'** to avoid unreliable statistics.\n\n"
                    "2. The brand was not present in the scraped data at all — the dataset may not "
                    "cover every marketplace or every brand available in Sri Lanka."
                ),
            },
            {
                "q": "Does the app account for seasonal price changes or dealer promotions?",
                "a": (
                    "No. The app uses a **static snapshot** of listing data. It does not account for "
                    "seasonal demand fluctuations, government import policy changes, tax revisions, "
                    "or dealer promotions. These factors can significantly influence real market prices."
                ),
            },
        ],
    },
    {
        "icon": "📈",
        "title": "Price Prediction Model",
        "questions": [
            {
                "q": "How does the price prediction work?",
                "a": (
                    "The prediction uses a **machine learning model** trained on the car listings dataset. "
                    "Seven regression models are trained and compared (Linear Regression, Ridge, Lasso, "
                    "Elastic Net, Decision Tree, Random Forest, Gradient Boosting). The best model "
                    "by Test RMSE is selected automatically and saved. When you enter vehicle details, "
                    "the saved model produces an instant price estimate."
                ),
            },
            {
                "q": "Why is Age shown but not used in the prediction?",
                "a": (
                    "Vehicle Age (2026 − YOM) has a **perfect correlation (r = 1.0)** with Mileage "
                    "in this dataset — they carry identical information. Including both would cause "
                    "**multicollinearity**, which distorts model coefficients. Age is shown in the UI "
                    "for reference only; the model uses Mileage instead."
                ),
            },
            {
                "q": "Why is my brand/model not in the prediction dropdown?",
                "a": (
                    "Brands and models with **fewer than 20 listings** are grouped as 'Other' before "
                    "training. If your specific brand or model had too few examples, the model could "
                    "not learn reliable patterns for it. Select 'Other' as the brand/model in this case — "
                    "the prediction will be based on similar vehicles."
                ),
            },
            {
                "q": "How accurate is the price prediction?",
                "a": (
                    "Accuracy depends on the best model selected during training (visible in the "
                    "diagnostics section as R², RMSE, and MAE). As a general guide:\n\n"
                    "- **R² close to 1.0** — model explains most of the price variation\n"
                    "- **RMSE** — average prediction error in LKR Millions\n"
                    "- **MAE** — average absolute error in LKR Millions\n\n"
                    "The prediction is an **estimate** based on historical listing data. "
                    "It should be used as a guide, not a guaranteed valuation."
                ),
            },
        ],
    },
]


# ── Help page function ─────────────────────────────────────────────────────────
def page_help():
    st.markdown("<div class='page-title'>❓ Help & FAQ</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Everything you need to know about using this app. "
        "Click any question to reveal the answer.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("""
    <div style='
        background: linear-gradient(135deg, #0d1117, #111827);
        border: 1px solid #1e2a3a;
        border-left: 4px solid #f0c040;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 20px 0 30px 0;
        color: #e6edf3;
        font-size: 0.92rem;
        line-height: 1.7;
    '>
        💡 <strong>Tip:</strong> Use the section headers to jump to the topic you need.
        Each question expands individually — click the <strong>▶ arrow</strong> to reveal the answer.
    </div>
    """, unsafe_allow_html=True)

    # Search box
    search = st.text_input(
        "🔎 Search questions...",
        placeholder="e.g. price, province, age, model...",
        key="help_search",
    ).strip().lower()

    st.markdown("<br>", unsafe_allow_html=True)

    total_shown = 0

    for section in FAQ_SECTIONS:
        # Filter questions by search term
        if search:
            matched = [
                item for item in section["questions"]
                if search in item["q"].lower() or search in item["a"].lower()
            ]
        else:
            matched = section["questions"]

        if not matched:
            continue

        total_shown += len(matched)

        # Section header
        st.markdown(
            f"""
            <div style='
                display: flex;
                align-items: center;
                gap: 10px;
                margin: 28px 0 10px 0;
            '>
                <span style='font-size: 1.4rem;'>{section["icon"]}</span>
                <span style='
                    font-family: Syne, sans-serif;
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: {GOLD};
                    letter-spacing: 0.5px;
                '>{section["title"]}</span>
                <span style='
                    background: #1e2a3a;
                    color: #58a6ff;
                    font-size: 0.75rem;
                    padding: 2px 10px;
                    border-radius: 20px;
                    font-weight: 600;
                '>{len(matched)} question{"s" if len(matched) != 1 else ""}</span>
            </div>
            <div style='height:1px; background: #1e2a3a; margin-bottom: 12px;'></div>
            """,
            unsafe_allow_html=True,
        )

        # Questions as expanders
        for item in matched:
            with st.expander(f"  {item['q']}"):
                st.markdown(
                    f"""
                    <div style='
                        background: #0d1117;
                        border-left: 3px solid {BLUE};
                        border-radius: 0 8px 8px 0;
                        padding: 14px 18px;
                        color: #c9d1d9;
                        font-size: 0.93rem;
                        line-height: 1.75;
                    '>
                    {item["a"].replace(chr(10), "<br>")}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # No results message
    if search and total_shown == 0:
        st.markdown(
            f"""
            <div style='
                text-align: center;
                padding: 40px 20px;
                color: #7d8590;
                font-size: 0.95rem;
            '>
                😕 No questions found matching <strong style='color:{GOLD};'>"{search}"</strong><br>
                <span style='font-size:0.85rem;'>Try a different keyword or clear the search box.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='
        height:4px;
        background:linear-gradient(90deg,transparent,#d4af37,#f0c040,#d4af37,transparent);
        margin: 20px 0;
        border-radius:5px;
    '></div>
    <div style='text-align:center; color:#7d8590; font-size:0.82rem; padding: 10px 0 20px 0;'>
        Still have questions? Check the
        <strong style='color:#f0c040;'>Data Explorer</strong> page for interactive filters,
        or the <strong style='color:#f0c040;'>Car Price Prediction</strong> page for estimates.
    </div>
    """, unsafe_allow_html=True)