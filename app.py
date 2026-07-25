
"""app.py - Subscription Intelligence Engine"""

import streamlit as st
import pandas as pd

from core.loader import TransactionLoader
from core.detector import SubscriptionDetector
from core.predictor import RenewalPredictor
from core.dashboard import show_dashboard


st.set_page_config(
    page_title="Subscription Intelligence Engine",
    page_icon="💳",
    layout="wide",
)

st.title("💳 Subscription Intelligence Engine")
st.caption("Detect recurring subscriptions and predict upcoming renewals.")

uploaded = st.file_uploader(
    "Upload Visa Transaction Report",
    type=["xlsx", "xls"],
)

if uploaded is None:
    st.info("Upload an Excel transaction report to begin.")
    st.stop()

try:

    loader = TransactionLoader()

    raw = pd.read_excel(uploaded)

    transactions = loader.prepare(raw)

    st.success(f"Loaded {len(transactions):,} transactions")

    with st.spinner("Detecting subscriptions..."):

        detector = SubscriptionDetector()

        subscriptions = detector.detect(transactions)

    with st.spinner("Predicting renewals..."):

        predictor = RenewalPredictor()

        predictions = predictor.predict(subscriptions)

    show_dashboard(
        subscriptions,
        predictions,
    )

    with st.expander("Preview Transactions"):

        st.dataframe(
            transactions,
            use_container_width=True,
        )

except Exception as ex:

    st.exception(ex)
