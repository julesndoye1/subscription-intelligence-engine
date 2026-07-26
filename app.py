"""
app.py

Subscription Intelligence Engine
Production Entry Point

Author: OpenAI
"""

from __future__ import annotations

import traceback

import pandas as pd
import streamlit as st

from core.loader import TransactionLoader
from core.classifier import SubscriptionClassifier
from core.predictor import RenewalPredictor
from core.nsf_engine import NSFEngine
from core.dashboard import show_dashboard


# ==========================================================
# Page Configuration
# ==========================================================

st.set_page_config(
    page_title="Subscription Intelligence Engine",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# Session State
# ==========================================================

DEFAULT_STATE = {
    "transactions": None,
    "classified": None,
    "renewals": None,
    "nsf": None,
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ==========================================================
# Sidebar
# ==========================================================

with st.sidebar:

    st.title("💳 Subscription Intelligence")

    st.markdown(
        """
Detect recurring subscriptions, predict future renewals,
and identify customers likely to experience insufficient funds.
"""
    )

    st.divider()

    uploaded_file = st.file_uploader(
        "Upload Visa Transaction Report",
        type=["xlsx", "xls", "csv"],
    )

    st.divider()

    run_analysis = st.button(
        "Run Analysis",
        use_container_width=True,
    )


# ==========================================================
# Header
# ==========================================================

st.title("💳 Subscription Intelligence Engine")

st.caption(
    "Executive dashboard for recurring payment intelligence."
)

# ==========================================================
# Waiting Screen
# ==========================================================

if uploaded_file is None:

    st.info(
        "Upload a Visa transaction report from the sidebar."
    )

    st.stop()


# ==========================================================
# Run Analysis
# ==========================================================

if run_analysis or st.session_state.transactions is None:

    try:

        progress = st.progress(0)

        status = st.empty()

        # --------------------------------------------------
        # Load Transactions
        # --------------------------------------------------

        status.info("Loading transactions...")

        loader = TransactionLoader()

        transactions = loader.load(uploaded_file)

        progress.progress(20)

        if transactions.empty:

            st.warning(
                "The uploaded report contains no transactions."
            )

            st.stop()

        # --------------------------------------------------
        # Classification
        # --------------------------------------------------

        status.info("Detecting subscriptions...")

        classifier = SubscriptionClassifier()

        classified = classifier.classify(
            transactions
        )

        progress.progress(45)

        # --------------------------------------------------
        # Renewal Prediction
        # --------------------------------------------------

        status.info("Predicting renewals...")

        predictor = RenewalPredictor()

        renewals = predictor.predict(
            classified
        )

        progress.progress(70)

        # --------------------------------------------------
        # NSF Detection
        # --------------------------------------------------

        status.info("Detecting NSF events...")

        nsf_engine = NSFEngine()

        nsf = nsf_engine.detect(
            renewals,
            classified,
        )

        progress.progress(90)

        # --------------------------------------------------
        # Save Session
        # --------------------------------------------------

        st.session_state.transactions = transactions

        st.session_state.classified = classified

        st.session_state.renewals = renewals

        st.session_state.nsf = nsf

        progress.progress(100)

        status.success(
            "Analysis completed successfully."
        )

    except Exception:

        st.error(
            "The Subscription Intelligence Engine encountered an unexpected error."
        )

        st.code(traceback.format_exc())

        st.stop()


# ==========================================================
# Dashboard
# ==========================================================

transactions = st.session_state.transactions

classified = st.session_state.classified

renewals = st.session_state.renewals

nsf = st.session_state.nsf

if classified is None:

    st.stop()

show_dashboard(
    classified_df=classified,
    renewal_df=renewals,
    nsf_df=nsf,
)

# ==========================================================
# Technical Summary
# ==========================================================

with st.expander(
    "Technical Summary",
    expanded=False,
):

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Transactions",
        len(transactions),
    )

    c2.metric(
        "Subscriptions",
        len(
            classified[
                classified["Subscription Status"]
                != "Not Subscription"
            ]
        ),
    )

    c3.metric(
        "Renewals",
        len(renewals),
    )

    c4.metric(
        "NSF Alerts",
        len(nsf),
    )

# ==========================================================
# Debug Information
# ==========================================================

with st.expander(
    "Debug Data",
    expanded=False,
):

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Transactions",
            "Subscriptions",
            "Renewals",
            "NSF",
        ]
    )

    with tab1:

        st.write(
            f"Rows: {len(transactions):,}"
        )

        st.dataframe(
            transactions.head(20),
            use_container_width=True,
            hide_index=True,
        )

    with tab2:

        st.write(
            f"Rows: {len(classified):,}"
        )

        st.dataframe(
            classified.head(20),
            use_container_width=True,
            hide_index=True,
        )

    with tab3:

        if renewals.empty:

            st.info(
                "No renewal predictions."
            )

        else:

            st.write(
                f"Rows: {len(renewals):,}"
            )

            st.dataframe(
                renewals.head(20),
                use_container_width=True,
                hide_index=True,
            )

    with tab4:

        if nsf.empty:

            st.info(
                "No NSF alerts detected."
            )

        else:

            st.write(
                f"Rows: {len(nsf):,}"
            )

            st.dataframe(
                nsf.head(20),
                use_container_width=True,
                hide_index=True,
            )