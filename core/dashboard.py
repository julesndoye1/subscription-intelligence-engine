"""
core/dashboard.py

Production-ready dashboard for Subscription Intelligence Engine.
"""

from __future__ import annotations
import pandas as pd
import streamlit as st
from core.analytics import AnalyticsEngine


class Dashboard:
    def __init__(self):
        self.analytics = AnalyticsEngine()

    def _safe_df(self, df: pd.DataFrame, rows: int | None = None):
        if df is None or df.empty:
            return
        view = df.head(rows) if rows else df
        st.dataframe(view, use_container_width=True, hide_index=True)

    def render(self, classified_df: pd.DataFrame,
               renewal_df: pd.DataFrame,
               nsf_df: pd.DataFrame):

        dashboard = self.analytics.executive_dashboard(
            classified_df, renewal_df, nsf_df
        )

        subs = dashboard["subscriptions"]
        ren = dashboard["renewals"]
        nsf = dashboard["nsf"]

        st.header("Executive Overview")
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Transactions", subs.get("Total Transactions",0))
        c2.metric("Subscriptions", subs.get("Detected Subscriptions",0))
        c3.metric("Customers", subs.get("Active Customers",0))
        c4.metric("Monthly Spend", f'{subs.get("Monthly Subscription Spend",0):,.2f}')
        c5.metric("Average", f'{subs.get("Average Subscription",0):,.2f}')

        st.divider()

        st.header("Renewal Status")
        r1,r2,r3,r4 = st.columns(4)
        r1.metric("Scheduled", ren.get("Scheduled",0))
        r2.metric("Upcoming", ren.get("Upcoming",0))
        r3.metric("Due Soon", ren.get("Due Soon",0))
        r4.metric("Overdue", ren.get("Overdue",0))

        st.divider()

        st.header("NSF Intelligence")
        n1,n2 = st.columns(2)
        n1.metric("NSF Alerts", nsf.get("NSF Alerts",0))
        n2.metric("Missing Renewals", nsf.get("Renewal Missing",0))
        if not nsf_df.empty:
            self._safe_df(nsf_df, 500)

        st.divider()

        merchant = dashboard.get("merchant_table", pd.DataFrame())
        category = dashboard.get("category_table", pd.DataFrame())

        left,right = st.columns(2)

        with left:
            st.subheader("Top Merchants")
            if not merchant.empty:
                self._safe_df(merchant)
                if {"Normalized Merchant","Revenue"} <= set(merchant.columns):
                    st.bar_chart(
                        merchant.set_index("Normalized Merchant")[["Revenue"]]
                    )

        with right:
            st.subheader("Categories")
            if not category.empty:
                self._safe_df(category)
                if {"Merchant Category","Revenue"} <= set(category.columns):
                    st.bar_chart(
                        category.set_index("Merchant Category")[["Revenue"]]
                    )

        st.divider()

        st.header("Detected Subscriptions")
        subscriptions = classified_df[
            classified_df["Subscription Status"]!="Not Subscription"
        ].copy()

        if subscriptions.empty:
            st.info("No subscriptions detected.")
        else:
            merchants = ["All"] + sorted(
                subscriptions["Normalized Merchant"].dropna().unique().tolist()
            )
            selected = st.selectbox("Merchant", merchants)
            if selected != "All":
                subscriptions = subscriptions[
                    subscriptions["Normalized Merchant"] == selected
                ]
            self._safe_df(subscriptions, 1000)

        st.divider()

        st.header("Upcoming Renewals")
        if renewal_df.empty:
            st.info("No renewal predictions.")
        else:
            renewal_df = renewal_df.sort_values("Predicted Renewal")
            self._safe_df(renewal_df, 1000)
            st.download_button(
                "Download Renewal Forecast",
                renewal_df.to_csv(index=False).encode("utf-8"),
                "renewal_forecast.csv",
                "text/csv",
            )


def show_dashboard(classified_df: pd.DataFrame,
                   renewal_df: pd.DataFrame,
                   nsf_df: pd.DataFrame):
    Dashboard().render(classified_df, renewal_df, nsf_df)
