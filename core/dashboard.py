"""
=========================================================
Subscription Intelligence Agent
Executive Dashboard
=========================================================

Displays subscription analytics using Streamlit.

Author:
Subscription Intelligence Team

Version:
1.0
"""

import streamlit as st


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------

def show_dashboard(renewals):
    """
    Display the executive dashboard.

    Parameters
    ----------
    renewals : pandas.DataFrame
    """

    st.title("📊 Subscription Intelligence Dashboard")

    if renewals.empty:
        st.info("No subscriptions detected.")
        return

    # -----------------------------------------------------
    # KPI Cards
    # -----------------------------------------------------

    total_subscriptions = len(renewals)

    total_customers = renewals["Account ID"].nunique()

    monthly_spend = renewals["Estimated Monthly Spend"].sum()

    annual_spend = renewals["Estimated Annual Spend"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Subscriptions",
        total_subscriptions,
    )

    col2.metric(
        "Customers",
        total_customers,
    )

    col3.metric(
        "Monthly Spend",
        f"{monthly_spend:,.2f}",
    )

    col4.metric(
        "Annual Spend",
        f"{annual_spend:,.2f}",
    )

    st.divider()

    # -----------------------------------------------------
    # Renewal Status
    # -----------------------------------------------------

    st.subheader("Renewal Status")

    renewal_counts = (
        renewals["Renewal Status"]
        .value_counts()
    )

    st.bar_chart(renewal_counts)

    st.divider()

    # -----------------------------------------------------
    # Spend by Merchant
    # -----------------------------------------------------

    st.subheader("Monthly Spend by Merchant")

    merchant_spend = (
        renewals
        .groupby("Merchant")["Estimated Monthly Spend"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(merchant_spend)

    st.divider()

    # -----------------------------------------------------
    # Spend by Category
    # -----------------------------------------------------

    st.subheader("Monthly Spend by Category")

    category_spend = (
        renewals
        .groupby("Category")["Estimated Monthly Spend"]
        .sum()
        .sort_values(ascending=False)
    )

    st.bar_chart(category_spend)

    st.divider()

    # -----------------------------------------------------
    # Upcoming Renewals
    # -----------------------------------------------------

    st.subheader("Upcoming Renewals")

    upcoming = renewals[
        renewals["Days Remaining"] <= 7
    ].copy()

    upcoming = upcoming[
        upcoming["Days Remaining"] >= 0
    ]

    if upcoming.empty:

        st.success(
            "No renewals due within the next 7 days."
        )

    else:

        st.dataframe(
            upcoming[
                [
                    "Customer",
                    "Merchant",
                    "Next Renewal",
                    "Days Remaining",
                    "Average Amount",
                ]
            ],
            use_container_width=True,
        )

    st.divider()

    # -----------------------------------------------------
    # All Subscriptions
    # -----------------------------------------------------

    st.subheader("Detected Subscriptions")

    st.dataframe(
        renewals,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="📥 Download Results (CSV)",
        data=renewals.to_csv(index=False),
        file_name="subscription_results.csv",
        mime="text/csv",
    )