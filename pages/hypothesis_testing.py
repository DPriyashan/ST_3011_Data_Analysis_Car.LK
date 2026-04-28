import streamlit as st
import scipy.stats as stats
import plotly.express as px
import scikit_posthocs as sp
import pandas as pd

#Lets user choose a categorical variable
#Tests whether Price differs across groups
#Automatically selects the correct statistical test
#Shows assumptions, hypotheses, decision, and conclusion
#Creates a boxplot
#Adds extra analysis if Fuel Type is selected

def page_hypotesting(df):

    st.markdown("## 🧪 Hypothesis Testing")

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    #select categorical variable to tests whether Price differs across groups in selected variable
    categorical_vars = df.select_dtypes(include="object").columns.tolist()

    group_var = st.selectbox(
        "Compare car prices across:",
        categorical_vars
    )

    st.markdown(f"""
    🔎 **Selected Variable:** `{group_var}`  

    We will statistically test whether car prices are significantly different across the categories of `{group_var}`.
    """)


    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    # Select only the chosen categorical variable and Price column
    # Also remove rows with missing values to ensure clean data
    df_test = df[[group_var, "Price"]].dropna()

    # Get all unique categories (groups) inside the selected variable
    groups = df_test[group_var].unique()

    # Count how many groups exist
    k = len(groups)

    # If there are fewer than 2 groups,
    # we cannot perform a comparison test
    if k < 2:
        st.warning("Not enough groups.")
        return

    # Set significance level (alpha)
    # This is the threshold for deciding statistical significance
    alpha = 0.05

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    # MAIN HYPOTHESIS TEST
    # Display Research Question Section
    # This dynamically shows the hypothesis questio
    st.markdown("## 📌 Research Question")
    st.markdown(f"### Is there a significant difference in car prices across {group_var}?")

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    #Check Parametric Assumptions
    st.markdown("## 🔍 Check Parametric Assumptions")
    st.write(
        "Before applying parametric tests such as the Independent t-test or One-Way ANOVA, "
        "it is necessary to verify whether key assumptions are satisfied. "
        "These include normality of the data within each group and homogeneity of variances across groups."
    )

    #stores price data for each category
    group_data = []
    #stores whether each group is normally distributed (True or False)
    normality_results = []
    #checks normality for each group separately
    for g in groups:
        data = df_test[df_test[group_var] == g]["Price"]
        group_data.append(data)

        if len(data) >= 3:
            _, p = stats.shapiro(data.sample(min(500, len(data)))) #Takes a sample,Shapiro is unreliable for very large samples
            normality_results.append(p > alpha)
        else:
            normality_results.append(False)

    #If ALL groups are normal,True
    normality = all(normality_results)
    # Summary shown on main page
    st.write(f"1.Normality Assumption: {'✅ Satisfied' if normality else '❌ Violated'}")
    # Detailed results hidden
    with st.expander("📊 View Shapiro-Wilk Test Details (Per Group)"):
        st.write("H₀: Data is normally distributed.")
        st.write("H₁: Data is not normally distributed.")
        st.markdown("---")

        for g in groups:
            data = df_test[df_test[group_var] == g]["Price"]

            if len(data) >= 3:
                sample_data = data.sample(min(500, len(data)))
                shapiro_stat, shapiro_p = stats.shapiro(sample_data)

                st.write(f"**Group: {g}**")
                st.write(f"Test Statistic: {shapiro_stat:.4f}")
                st.write(f"P-value: {shapiro_p:.5f}")

                if shapiro_p < alpha:
                    st.write("Decision: Reject H₀ (Not Normal)")
                else:
                    st.write("Decision: Fail to Reject H₀ (Normal)")

                st.markdown("---")
            else:
                st.write(f"**Group: {g}** → Not enough data for test")
                st.markdown("---")

    # Homogeneity of Variance (Levene’s Test)
    levene_stat, levene_p = stats.levene(*group_data)
    # Decision logic
    equal_variance = levene_p > alpha
    #Summary (Simple Result Shown on Page)
    st.write(f"2.Equal Variance Assumption: {'✅ Satisfied' if equal_variance else '❌ Violated'}")
    #Detailed Results (Hidden Box)
    with st.expander("📊 View Levene’s Test Details"):

        st.write("H₀: Group variances are equal.")
        st.write("H₁: At least one group variance differs.")

        st.write(f"Test Statistic: {levene_stat:.4f}")
        st.write(f"P-value: {levene_p:.5f}")

        if equal_variance:
            st.write("Decision: Fail to Reject H₀ (Variances are equal)")
        else:
            st.write("Decision: Reject H₀ (Variances are significantly different)")

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)
    st.markdown("## 🔬Select Appropriate Test")

    if k == 2:

        if normality and equal_variance:
            test_name = "Independent T-Test"
            stat, p_value = stats.ttest_ind(group_data[0], group_data[1])
            test_type = "Parametric"
        else:
            test_name = "Mann–Whitney U Test"
            stat, p_value = stats.mannwhitneyu(group_data[0], group_data[1])
            test_type = "Non-Parametric"

    else:

        if normality and equal_variance:
            test_name = "One-Way ANOVA"
            stat, p_value = stats.f_oneway(*group_data)
            test_type = "Parametric"
        else:
            test_name = "Kruskal–Wallis Test"
            stat, p_value = stats.kruskal(*group_data)
            test_type = "Non-Parametric"

    st.write(f"Selected Test Type: **{test_type}**")
    st.write(f"Test Used: **{test_name}**")
    st.write(f"Significance Level (α): {alpha}")

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    st.markdown("## 📊Hypotheses")

    if test_type == "Parametric":
        st.write("H₀: The mean car prices are equal across groups.")
        st.write("H₁: At least one group mean differs.")
    else:
        st.write("H₀: The distribution of car prices is the same across groups.")
        st.write("H₁: At least one group distribution differs.")

    col1, col2 = st.columns(2)
    col1.metric("Test Statistic", round(stat, 3))
    col2.metric("P-Value", round(p_value, 5))

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    st.markdown("## 📌Decision")

    if p_value < alpha:
        st.success(f"Reject H₀ at α = {alpha}. There is a statistically significant difference.")
    else:
        st.warning(f"Fail to Reject H₀ at α = {alpha}. There is insufficient evidence of a significant difference.")
    
    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    st.markdown("## 📘 Conclusion")

    if p_value < alpha:
        st.write(f"There is sufficient evidence (α = {alpha}) that car prices differ across {group_var}.")
    else:
        st.write(f"There is insufficient evidence (α = {alpha}) to conclude price differences across {group_var}.")

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

    # VISUALISATION
    st.markdown("## 📊 Visualisation of Price Distribution")

    fig = px.box(
        df_test,
        x=group_var,
        y="Price",
        color=group_var,
        title=f"Car Price Distribution by {group_var}"
    )

    fig.update_layout(template="plotly_dark", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)



    #additional tests(one sided)
    one_sided_vars = ["Gear", "Condition"]

    # ONE-SIDED HYPOTHESIS TEST (Uses previous test selection)
    if group_var in one_sided_vars and k == 2:
        st.markdown("## 📌 Research Question")
        st.markdown(f"### Is one category significantly more expensive than the other in {group_var}?")

        # Define comparison direction
        if group_var == "Gear":
            high_label = "Automatic"
            low_label = "Manual"

        elif group_var == "Condition":
            high_label = "New"
            low_label = "Used"

        # Extract data
        high_data = df_test[df_test[group_var] == high_label]["Price"]
        low_data = df_test[df_test[group_var] == low_label]["Price"]

        st.markdown("## One-Sided Hypothesis Test")

        # Display Correct Hypotheses

        if test_type == "Parametric":

            st.write(f"H₀: μ_{high_label} = μ_{low_label}")
            st.write(f"H₁: μ_{high_label} > μ_{low_label}")

        else:

            st.write("H₀: The price distributions are the same.")
            st.write(f"H₁: {high_label} cars tend to have higher prices than {low_label} cars.")

        # Run Appropriate Test
        if test_type == "Parametric":

            # Two-sided t-test → convert to one-sided
            stat, p_two = stats.ttest_ind(high_data, low_data)
            p_one = p_two / 2
            test_used = "Independent T-Test (One-Sided)"
        else:
            # Direct one-sided Mann–Whitney
            stat, p_one = stats.mannwhitneyu(
                high_data,
                low_data,
                alternative="greater"
            )

            test_used = "Mann–Whitney U Test (One-Sided)"

        # Show Results
        st.write(f"Test Used: **{test_used}**")
        col1, col2 = st.columns(2)
        col1.metric("Test Statistic", round(stat, 3))
        col2.metric("One-Sided P-Value", round(p_one, 5))

        # Decision
        if p_one < alpha:
            st.success(f"Reject H₀ at α = {alpha}. Evidence suggests {high_label} cars are more expensive.")
        else:
            st.warning(f"Fail to Reject H₀ at α = {alpha}. Insufficient evidence that {high_label} cars are more expensive.")
        st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)
    
   
    # POST-HOC TEST (k > 2 and significant overall test)

    if k > 2 and p_value < alpha:

        st.markdown("## 🔍 Post Hoc Analysis")
        st.write(
            "Post hoc pairwise comparisons were conducted to identify specific group differences "
            "at the 5% significance level."
        )

        significant_pairs = []

        if test_type == "Parametric":

            from statsmodels.stats.multicomp import pairwise_tukeyhsd

            tukey = pairwise_tukeyhsd(
                endog=df_test["Price"],
                groups=df_test[group_var],
                alpha=alpha
            )

            tukey_df = pd.DataFrame(
                data=tukey.summary().data[1:], 
                columns=tukey.summary().data[0]
            )

            for _, row in tukey_df.iterrows():
                if row["reject"] == True:
                    significant_pairs.append((row["group1"], row["group2"]))

            posthoc_df = tukey_df


        else:

            import scikit_posthocs as sp

            dunn = sp.posthoc_dunn(
                df_test,
                val_col="Price",
                group_col=group_var,
                p_adjust="bonferroni"
            )

            posthoc_df = dunn

            for i in range(len(dunn.columns)):
                for j in range(i+1, len(dunn.columns)):
                    if dunn.iloc[i, j] < alpha:
                        significant_pairs.append((dunn.index[i], dunn.columns[j]))

        with st.expander("📂 View Post Hoc Detailed Results"):

            st.subheader("📊 Post Hoc DataFrame")
            st.dataframe(posthoc_df)



        with st.expander("📂 View Post Hoc Detailed Results"):
            st.subheader("📝 Interpretation (α = 0.05)")
            if significant_pairs:
                for g1, g2 in significant_pairs:
                    st.write(f"• {g1} and {g2} price differ significantly.")
            else:
                st.write("No pairwise significant differences found.")


            # ADDITIONAL FUEL TYPE ANALYSIS
            # This section groups fuel types into:
            # Traditional (Petrol, Diesel)
            # Alternative (Electric, Hybrid)
            # Then tests whether their prices differ

        if group_var == "Fuel Type":

            st.markdown("---")
            st.markdown("## 🔥 Additional Analysis: Traditional vs Alternative Vehicles")

            df_alt = df_test.copy()

            df_alt["Fuel_Group"] = df_alt["Fuel Type"].replace({
                "Petrol": "Traditional",
                "Diesel": "Traditional",
                "Electric": "Alternative",
                "Hybrid": "Alternative"
            })

            df_alt = df_alt[df_alt["Fuel_Group"].isin(["Traditional", "Alternative"])]

            if df_alt["Fuel_Group"].nunique() < 2:
                st.warning("Not enough data after grouping.")
                return
            st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)
            st.markdown("### 📌 Research Question")
            st.write("Is there a significant difference in car prices between Traditional and Alternative vehicles?")
            st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)
            group_data_alt = [
                df_alt[df_alt["Fuel_Group"] == g]["Price"]
                for g in df_alt["Fuel_Group"].unique()
            ]

            # Assumptions
            st.markdown("### 🔍Parametric Test Assumption Checks")
            st.write(
                "Before applying parametric tests such as the Independent t-test or One-Way ANOVA, "
                "it is necessary to verify whether key assumptions are satisfied. "
                "These include normality of the data within each group and homogeneity of variances across groups."
            )

            normality_results = []
            for data in group_data_alt:
                if len(data) >= 3:
                    _, p = stats.shapiro(data.sample(min(500, len(data))))
                    normality_results.append(p > alpha)
                else:
                    normality_results.append(False)

            normality = all(normality_results)

            levene_stat, levene_p = stats.levene(*group_data_alt)
            equal_variance = levene_p > alpha

            st.write(f"Normality satisfied: {'✅ Yes' if normality else '❌ No'}")
            st.write(f"Equal variance satisfied: {'✅ Yes' if equal_variance else '❌ No'}")

            # Test selection
            if normality and equal_variance:
                test_name = "Independent T-Test"
                stat, p_value = stats.ttest_ind(group_data_alt[0], group_data_alt[1])
                test_type = "Parametric"
            else:
                test_name = "Mann–Whitney U Test"
                stat, p_value = stats.mannwhitneyu(group_data_alt[0], group_data_alt[1])
                test_type = "Non-Parametric"

            st.write(f"Selected Test Type: **{test_type}**")
            st.write(f"Test Used: **{test_name}**")
            st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)
            st.markdown("### 📊 Hypotheses")

            if test_type == "Parametric":
                st.write("H₀: The mean prices of Traditional and Alternative vehicles are equal.")
                st.write("H₁: The mean prices differ.")
            else:
                st.write("H₀: The price distributions are the same.")
                st.write("H₁: The price distributions differ.")

            col1, col2 = st.columns(2)
            col1.metric("Test Statistic", round(stat, 3))
            col2.metric("P-Value", round(p_value, 5))

            st.markdown("### 📌 Decision")

            if p_value < alpha:
                st.success("Reject H₀")
            else:
                st.warning("Fail to Reject H₀")

            st.markdown("### 📘 Conclusion")

            if p_value < alpha:
                st.write("There is sufficient evidence that Alternative and Traditional vehicles differ in price.")
            else:
                st.write("There is insufficient evidence to conclude a price difference.")
            st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)
            # Visualisation
            st.markdown("### 📊 Visualisation")

            fig_alt = px.box(
                df_alt,
                x="Fuel_Group",
                y="Price",
                color="Fuel_Group",
                title="Price Distribution: Traditional vs Alternative Vehicles"
            )

            fig_alt.update_layout(template="plotly_dark", showlegend=False)
            st.plotly_chart(fig_alt, use_container_width=True)

        st.markdown("<hr style='border:1px solid #d4af37;margin-top:8px;margin-bottom:20px;'>", unsafe_allow_html=True)

        st.markdown("## ⚠️ Hypothesis TestingStudy Limitations")

        with st.expander("⚠️ Study Limitations", expanded=False):

            st.write(
                "The conclusions drawn from hypothesis testing are subject to certain limitations:"
            )

            st.markdown("""
            1. The analysis assumes that the collected data accurately represent the target population.  
            2. Violations of statistical assumptions may influence the robustness of parametric tests.  
            3. Non-parametric tests are less sensitive but may have lower statistical power.  
            4. The significance level (α = 0.05) is arbitrary and affects decision outcomes.  
            5. External factors not included in the model may influence price variations.  
            """)