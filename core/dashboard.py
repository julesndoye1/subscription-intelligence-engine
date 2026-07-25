"""
dashboard.py

Executive Dashboard for the Subscription Intelligence Engine
"""

from __future__ import annotations

import streamlit as st
import pandas as pd

from core.analytics import AnalyticsEngine


class Dashboard:

    def __init__(self):

        self.analytics = AnalyticsEngine()

    # ---------------------------------------------------------

    def render(
        self,
        classified_df: pd.DataFrame,
        renewal_df: pd.DataFrame,
        nsf_df: pd.DataFrame,
    ):

        st.set_page_config(
            page_title="Subscription Intelligence Engine",
            page_icon="💳",
            layout="wide",
        )

        st.title("💳 Subscription Intelligence Engine")

        dashboard = self.analytics.executive_dashboard(
            classified_df,
            renewal_df,
            nsf_df,
        )

        subscriptions = dashboard["subscriptions"]
        renewals = dashboard["renewals"]
        nsf = dashboard["nsf"]

        # =====================================================
        # Executive KPIs
        # =====================================================

        st.header("Executive Overview")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric(
            "Transactions",
            subscriptions.get("Total Transactions", 0),
        )

        c2.metric(
            "Subscriptions",
            subscriptions.get("Detected Subscriptions", 0),
        )

        c3.metric(
            "Customers",
            subscriptions.get("Active Customers", 0),
        )

        c4.metric(
            "Subscription Spend",
            f"{subscriptions.get('Monthly Subscription Spend', 0):,.2f}",
        )

        c5.metric(
            "Average Subscription",
            f"{subscriptions.get('Average Subscription', 0):,.2f}",
        )

        st.divider()

        # =====================================================
        # Renewal KPIs
        # =====================================================

        st.header("Renewal Status")

        r1, r2, r3, r4 = st.columns(4)

        r1.metric(
            "Scheduled",
            renewals.get("Scheduled", 0),
        )

        r2.metric(
            "Upcoming",
            renewals.get("Upcoming", 0),
        )

        r3.metric(
            "Due Soon",
            renewals.get("Due Soon", 0),
        )

        r4.metric(
            "Overdue",
            renewals.get("Overdue", 0),
        )

        st.divider()

        # =====================================================
        # NSF Monitoring
        # =====================================================

        st.header("NSF Intelligence")

        n1, n2 = st.columns(2)

        n1.metric(
            "NSF Alerts",
            nsf.get("NSF Alerts", 0),
        )

        n2.metric(
            "Missing Renewals",
            nsf.get("Renewal Missing", 0),
        )

        if not nsf_df.empty:

            st.subheader("NSF Alerts")

            st.dataframe(
                nsf_df,
                use_container_width=True,
            )

        st.divider()

        # =====================================================
        # Merchant Analytics
        # =====================================================

        merchant_table = dashboard["merchant_table"]

        st.header("Top Subscription Merchants")

        if not merchant_table.empty:

            st.dataframe(
                merchant_table,
                use_container_width=True,
            )

            merchant_chart = (
                merchant_table
                .set_index("Normalized Merchant")["Revenue"]
            )

            st.bar_chart(merchant_chart)

        st.divider()

        # =====================================================
        # Category Analytics
        # =====================================================

        category_table = dashboard["category_table"]

        st.header("Subscription Categories")

        if not category_table.empty:

            st.dataframe(
                category_table,
                use_container_width=True,
            )

            category_chart = (
                category_table
                .set_index("Merchant Category")["Revenue"]
            )

            st.bar_chart(category_chart)

        st.divider()

        # =====================================================
        # Customer Subscriptions
        # =====================================================

        st.header("Detected Subscriptions")

        subscriptions_only = classified_df[
            classified_df["Subscription Status"] != "Not Subscription"
        ]

        if not subscriptions_only.empty:

            merchant_filter = st.selectbox(
                "Merchant",
                ["All"]
                + sorted(
                    subscriptions_only[
                        "Normalized Merchant"
                    ].unique()
                ),
            )

            if merchant_filter != "All":

                subscriptions_only = subscriptions_only[
                    subscriptions_only[
                        "Normalized Merchant"
                    ]
                    == merchant_filter
                ]

            st.dataframe(
                subscriptions_only,
                use_container_width=True,
            )

        st.divider()

        # =====================================================
        # Upcoming Renewals
        # =====================================================

        st.header("Upcoming Renewals")

        if not renewal_df.empty:

            renewal_df = renewal_df.sort_values(
                "Predicted Renewal"
            )

            st.dataframe(
                renewal_df,
                use_container_width=True,
            )

            csv = renewal_df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "Download Renewal Forecast",
                data=csv,
                file_name="renewal_forecast.csv",
                mime="text/csv",
            )


# -----------------------------------------------------------------

def show_dashboard(
    classified_df: pd.DataFrame,
    renewal_df: pd.DataFrame,
    nsf_df: pd.DataFrame,
):

    Dashboard().render(
        classified_df,
        renewal_df,
        nsf_df,
    )