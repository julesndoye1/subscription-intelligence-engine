"""
=========================================================
Subscription Intelligence Agent
Main Application
=========================================================

Author:
Subscription Intelligence Team

Version:
1.0
"""

import streamlit as st
import pandas as pd

from core.loader import (
    load_transactions,
    transaction_summary,
)

from core.detector import (
    detect_subscriptions,
)

from core.predictor import (
    predict_renewals,
)

from core.dashboard import (
    show_dashboard,
)

# -------------------------------------------------------
# Page Configuration
# -------------------------------------------------------

st.set_page_config(
    page_title="Subscription Intelligence Agent",
    page_icon="💳",
    layout="wide",
)

# -------------------------------------------------------
# Session State
# -------------------------------------------------------

if "transactions" not in st.session_state:
    st.session_state.transactions = None

if "subscriptions" not in st.session_state:
    st.session_state.subscriptions = None

if "renewals" not in st.session_state:
    st.session_state.renewals = None

if "uploaded_file_name" not in st.session_state:
    st.session_state.uploaded_file_name = None

if "confidence_threshold" not in st.session_state:
    st.session_state.confidence_threshold = 50

if "due_soon_days" not in st.session_state:
    st.session_state.due_soon_days = 7

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------

st.sidebar.title("💳 Subscription Intelligence")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Customers",
        "Renewals",
        "Transactions",
        "Merchant Intelligence",
        "Settings",
    ],
)

st.sidebar.divider()

uploaded_file = st.sidebar.file_uploader(
    "Upload Visa Transaction Report",
    type=["xlsx"],
)

# -------------------------------------------------------
# Load Uploaded File
# -------------------------------------------------------

if uploaded_file is not None:

    if (
        st.session_state.uploaded_file_name
        != uploaded_file.name
    ):

        try:

            transactions = load_transactions(uploaded_file)

            subscriptions = detect_subscriptions(
                transactions,
                confidence_threshold=st.session_state.confidence_threshold,
            )

            renewals = predict_renewals(
                subscriptions
            )
            st.write("Subscriptions shape:", subscriptions.shape)
            st.write("Subscriptions columns:", list(subscriptions.columns))

            st.write("Renewals shape:", renewals.shape)
            st.write("Renewals columns:", list(renewals.columns))

            st.session_state.transactions = transactions
            st.session_state.subscriptions = subscriptions
            st.session_state.renewals = renewals
            st.session_state.uploaded_file_name = uploaded_file.name

            st.sidebar.success("File loaded successfully.")

        except Exception as e:

            st.sidebar.error(str(e))

# -------------------------------------------------------
# Helper
# -------------------------------------------------------

def require_data():

    if st.session_state.transactions is None:

        st.info(
            "Please upload a Visa transaction report using the sidebar."
        )

        st.stop()

# -------------------------------------------------------
# Dashboard
# -------------------------------------------------------

if page == "Dashboard":

    require_data()

    show_dashboard(
        st.session_state.renewals
    )

# -------------------------------------------------------
# Customers
# -------------------------------------------------------

elif page == "Customers":

    require_data()

    st.title("👤 Customers")

    renewals = st.session_state.renewals.copy()

    customers = sorted(
        renewals["Customer"].unique()
    )

    selected_customer = st.selectbox(
        "Select Customer",
        customers,
    )

    customer_df = renewals[
        renewals["Customer"] == selected_customer
    ]

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Subscriptions",
        len(customer_df),
    )

    col2.metric(
        "Monthly Spend",
        f"{customer_df['Estimated Monthly Spend'].sum():,.2f}",
    )

    col3.metric(
        "Annual Spend",
        f"{customer_df['Estimated Annual Spend'].sum():,.2f}",
    )

    st.divider()

    st.dataframe(
        customer_df,
        use_container_width=True,
        hide_index=True,
    )
    # -------------------------------------------------------
# Renewals
# -------------------------------------------------------

elif page == "Renewals":

    require_data()

    st.title("📅 Subscription Renewals")

    renewals = st.session_state.renewals.copy()

    status = st.selectbox(
        "Renewal Status",
        [
            "All",
            "Upcoming",
            "Due Soon",
            "Overdue",
        ],
    )

    if status != "All":

        renewals = renewals[
            renewals["Renewal Status"] == status
        ]

    merchant_filter = st.text_input(
        "Filter by Merchant"
    )

    if merchant_filter:

        renewals = renewals[
            renewals["Merchant"]
            .str.contains(
                merchant_filter,
                case=False,
                na=False,
            )
        ]

    st.dataframe(
        renewals,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download Renewals CSV",
        data=renewals.to_csv(index=False),
        file_name="renewals.csv",
        mime="text/csv",
    )

# -------------------------------------------------------
# Transactions
# -------------------------------------------------------

elif page == "Transactions":

    require_data()

    st.title("💳 Transactions")

    transactions = (
        st.session_state.transactions.copy()
    )

    search = st.text_input(
        "Search Transaction"
    )

    if search:

        mask = (
            transactions.astype(str)
            .apply(
                lambda col: col.str.contains(
                    search,
                    case=False,
                    na=False,
                )
            )
            .any(axis=1)
        )

        transactions = transactions[mask]

    st.write(
        f"Total Transactions: {len(transactions):,}"
    )

    st.dataframe(
        transactions,
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        label="Download Transactions CSV",
        data=transactions.to_csv(index=False),
        file_name="transactions.csv",
        mime="text/csv",
    )

# -------------------------------------------------------
# Merchant Intelligence
# -------------------------------------------------------

elif page == "Merchant Intelligence":

    require_data()

    st.title("🧠 Merchant Intelligence")

    renewals = st.session_state.renewals.copy()

    st.subheader("Subscriptions by Merchant")

    merchant_summary = (

        renewals

        .groupby("Merchant")

        .agg(

            Subscriptions=("Merchant", "count"),

            Customers=("Account ID", "nunique"),

            MonthlySpend=(
                "Estimated Monthly Spend",
                "sum",
            ),

            AnnualSpend=(
                "Estimated Annual Spend",
                "sum",
            ),

            AvgConfidence=(
                "Confidence",
                "mean",
            ),

        )

        .reset_index()

        .sort_values(
            "MonthlySpend",
            ascending=False,
        )

    )

    st.dataframe(
        merchant_summary,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Monthly Spend by Merchant")

    merchant_chart = (

        merchant_summary

        .set_index("Merchant")[
            "MonthlySpend"
        ]

    )

    st.bar_chart(
        merchant_chart
    )

    st.subheader("Subscriptions by Category")

    category_chart = (

        renewals

        .groupby("Category")[
            "Estimated Monthly Spend"
        ]

        .sum()

        .sort_values(
            ascending=False
        )

    )

    st.bar_chart(
        category_chart
    )

    st.subheader("Top Merchants")

    st.dataframe(

        merchant_summary.head(10),

        use_container_width=True,

        hide_index=True,

    )

    st.download_button(

        label="Download Merchant Report",

        data=merchant_summary.to_csv(index=False),

        file_name="merchant_report.csv",

        mime="text/csv",

    )
    # -------------------------------------------------------
# Settings
# -------------------------------------------------------

elif page == "Settings":

    st.title("⚙️ Settings")

    st.subheader("Subscription Detection")

    confidence = st.slider(
        "Confidence Threshold",
        min_value=0,
        max_value=100,
        value=st.session_state.confidence_threshold,
        step=5,
    )

    due_days = st.slider(
        "Due Soon Window (Days)",
        min_value=1,
        max_value=30,
        value=st.session_state.due_soon_days,
    )

    if st.button("Save Settings"):

        st.session_state.confidence_threshold = confidence
        st.session_state.due_soon_days = due_days

        st.success(
            "Settings saved."
        )

        if st.session_state.transactions is not None:

            subscriptions = detect_subscriptions(
                st.session_state.transactions,
                confidence_threshold=confidence,
            )

            renewals = predict_renewals(
                subscriptions
            )

            st.session_state.subscriptions = subscriptions
            st.session_state.renewals = renewals

            st.success(
                "Subscription analysis refreshed."
            )

    st.divider()

    st.subheader("Current Settings")

    st.write(
        f"Confidence Threshold : "
        f"{st.session_state.confidence_threshold}"
    )

    st.write(
        f"Due Soon Window : "
        f"{st.session_state.due_soon_days} days"
    )

    st.divider()

    if st.button("Clear Loaded Data"):

        st.session_state.transactions = None
        st.session_state.subscriptions = None
        st.session_state.renewals = None
        st.session_state.uploaded_file_name = None

        st.success(
            "Data cleared successfully."
        )

# -------------------------------------------------------
# Footer
# -------------------------------------------------------

st.divider()

if st.session_state.transactions is not None:

    summary = transaction_summary(
        st.session_state.transactions
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Transactions",
        summary["transactions"],
    )

    col2.metric(
        "Customers",
        summary["customers"],
    )

    col3.metric(
        "From",
        str(summary["date_from"].date()),
    )

    col4.metric(
        "To",
        str(summary["date_to"].date()),
    )

st.caption(
    "Subscription Intelligence Agent v1.0"
)

st.caption(
    "Built with Python, Pandas and Streamlit"
)