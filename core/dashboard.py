
"""dashboard.py - Streamlit dashboard for Subscription Intelligence Engine."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from core.detector import subscription_summary
from core.predictor import prediction_summary, upcoming_renewals
from core.utils import currency


class Dashboard:

    def render(self, subscriptions: pd.DataFrame, predictions: pd.DataFrame) -> None:
        st.set_page_config(page_title="Subscription Intelligence Engine", layout="wide")
        st.title("Subscription Intelligence Engine")

        sub = subscription_summary(subscriptions)
        pred = prediction_summary(predictions)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Subscriptions", sub["subscriptions"])
        c2.metric("Customers", sub["customers"])
        c3.metric("Monthly Spend", currency(sub["monthly_spend"]))
        c4.metric("Renewals (7 days)", pred["due_this_week"])

        st.divider()

        if not subscriptions.empty:
            st.subheader("Detected Subscriptions")
            merchant = st.selectbox(
                "Merchant Filter",
                ["All"] + sorted(subscriptions["Merchant"].unique().tolist()),
            )
            view = subscriptions if merchant == "All" else subscriptions[subscriptions["Merchant"] == merchant]
            st.dataframe(view, use_container_width=True)

            st.subheader("Subscriptions by Category")
            cat = view.groupby("Category").size().sort_values(ascending=False)
            st.bar_chart(cat)

            st.subheader("Confidence Distribution")
            st.bar_chart(view.set_index("Merchant")["Confidence"])

        if not predictions.empty:
            st.divider()
            st.subheader("Upcoming Renewals")
            due = upcoming_renewals(predictions, 30)
            st.dataframe(due, use_container_width=True)

            csv = due.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download Renewals CSV",
                data=csv,
                file_name="renewal_predictions.csv",
                mime="text/csv",
            )


def show_dashboard(subscriptions: pd.DataFrame, predictions: pd.DataFrame) -> None:
    Dashboard().render(subscriptions, predictions)
