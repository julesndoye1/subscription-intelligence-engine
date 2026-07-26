"""
Subscription Intelligence Dashboard

Executive Dashboard
Dashboard V2
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.analytics import AnalyticsEngine


# ------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------

class Dashboard:

    def __init__(self):

        self.analytics = AnalyticsEngine()

    # --------------------------------------------------------

    def _show_table(
        self,
        df: pd.DataFrame,
        height: int = 450,
    ):

        if df is None:
            return

        if df.empty:
            return

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            height=height,
        )

    # --------------------------------------------------------

    @staticmethod
    def _clean_transaction_id(value):

        if pd.isna(value):
            return ""

        try:

            return str(int(float(value)))

        except Exception:

            return (
                str(value)
                .replace(",", "")
                .replace(".0", "")
            )

    # --------------------------------------------------------

    @staticmethod
    def _customer_subscription_summary(
        renewal_df: pd.DataFrame,
    ) -> pd.DataFrame:

        """
        One row per customer per merchant.
        """

        if renewal_df.empty:

            return renewal_df

        summary = renewal_df.copy()
                # --------------------------------------------
        # Clean Transaction ID
        # --------------------------------------------

        if "Transaction ID" in summary.columns:

            summary["Transaction ID"] = (

                summary["Transaction ID"]

                .apply(
                    Dashboard._clean_transaction_id
                )

            )

        # --------------------------------------------
        # Keep latest payment
        # --------------------------------------------

        if "Last Payment" in summary.columns:

            summary = summary.sort_values(

                "Last Payment",

                ascending=False,

            )

        # --------------------------------------------
        # One row/customer/merchant
        # --------------------------------------------

        keys = []

        if "Account ID" in summary.columns:

            keys.append("Account ID")

        if "Merchant" in summary.columns:

            keys.append("Merchant")

        if keys:

            summary = summary.drop_duplicates(

                subset=keys,

                keep="first",

            )

        # --------------------------------------------
        # Sort
        # --------------------------------------------

        sort_columns = []

        if "Days Remaining" in summary.columns:

            sort_columns.append(
                "Days Remaining"
            )

        if "Name" in summary.columns:

            sort_columns.append(
                "Name"
            )

        if "Merchant" in summary.columns:

            sort_columns.append(
                "Merchant"
            )

        if sort_columns:

            summary = summary.sort_values(
                sort_columns
            )

        return summary

    # --------------------------------------------------------

    def render(

        self,

        classified_df: pd.DataFrame,

        renewal_df: pd.DataFrame,

        nsf_df: pd.DataFrame,

    ):

        dashboard = self.analytics.executive_dashboard(

            classified_df,

            renewal_df,

            nsf_df,

        )

        summary = self._customer_subscription_summary(
            renewal_df
        )
                # ==========================================================
        # Executive Overview
        # ==========================================================

        st.title("Subscription Intelligence Dashboard")

        st.caption(
            "Executive view of active customer subscriptions."
        )

        customers = (
            summary["Account ID"].nunique()
            if not summary.empty and "Account ID" in summary.columns
            else 0
        )

        active_subscriptions = len(summary)

        renewing_this_week = (
            (
                summary["Days Remaining"] <= 7
            ).sum()
            if (
                not summary.empty
                and "Days Remaining" in summary.columns
            )
            else 0
        )

        monthly_spend = (
            summary["Amount"].sum()
            if (
                not summary.empty
                and "Amount" in summary.columns
            )
            else 0
        )

        nsf_alerts = (
            len(nsf_df)
            if nsf_df is not None
            else 0
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "Customers",
            f"{customers:,}"
        )

        col2.metric(
            "Subscriptions",
            f"{active_subscriptions:,}"
        )

        col3.metric(
            "Renewing (7 Days)",
            f"{renewing_this_week:,}"
        )

        col4.metric(
            "Monthly Spend",
            f"{monthly_spend:,.2f}"
        )

        col5.metric(
            "NSF Alerts",
            f"{nsf_alerts:,}"
        )

        st.divider()
                # ==========================================================
        # Customer Subscription Summary
        # ==========================================================

        st.header("Customer Subscription Summary")

        if summary.empty:

            st.info(
                "No active subscriptions found."
            )

        else:

            left, right, right2 = st.columns(3)

            customer_filter = left.text_input(
                "Customer Name"
            )

            merchants = ["All"]

            if "Merchant" in summary.columns:

                merchants.extend(
                    sorted(
                        summary["Merchant"]
                        .dropna()
                        .unique()
                        .tolist()
                    )
                )

            merchant_filter = right.selectbox(
                "Merchant",
                merchants,
            )

            statuses = ["All"]

            if "Renewal Status" in summary.columns:

                statuses.extend(
                    sorted(
                        summary["Renewal Status"]
                        .dropna()
                        .unique()
                        .tolist()
                    )
                )

            status_filter = right2.selectbox(
                "Renewal Status",
                statuses,
            )

            filtered = summary.copy()

            if customer_filter:

                if "Name" in filtered.columns:

                    filtered = filtered[
                        filtered["Name"]
                        .str.contains(
                            customer_filter,
                            case=False,
                            na=False,
                        )
                    ]

            if merchant_filter != "All":

                filtered = filtered[
                    filtered["Merchant"]
                    == merchant_filter
                ]

            if status_filter != "All":

                filtered = filtered[
                    filtered["Renewal Status"]
                    == status_filter
                ]

            preferred_columns = [

                "Name",

                "Phone",

                "Account ID",

                "Merchant",

                "Merchant Category",

                "Amount",

                "Billing Frequency",

                "Last Payment",

                "Predicted Renewal",

                "Days Remaining",

                "Renewal Status",

                "Transaction ID",

            ]

            columns = [
                c
                for c in preferred_columns
                if c in filtered.columns
            ]

            remaining = [
                c
                for c in filtered.columns
                if c not in columns
            ]

            filtered = filtered[
                columns + remaining
            ]

            self._show_table(
                filtered,
                height=500,
            )

            st.download_button(
                "Download Customer Subscription Summary",
                filtered.to_csv(
                    index=False
                ).encode("utf-8"),
                file_name="customer_subscription_summary.csv",
                mime="text/csv",
            )

        st.divider()
                # ==========================================================
        # Upcoming Renewals
        # ==========================================================

        st.header("Upcoming Renewals (Next 8 Days)")

        if summary.empty:

            st.info(
                "No upcoming renewals."
            )

        else:

            renewals = summary.copy()

            if "Days Remaining" in renewals.columns:

                renewals = renewals[
                    (renewals["Days Remaining"] >= 1)
                    &
                    (renewals["Days Remaining"] <= 8)
                ]

            if renewals.empty:

                st.success(
                    "No subscriptions renewing within the next 8 days."
                )

            else:

                renewals = renewals.sort_values(
                    [
                        "Days Remaining",
                        "Predicted Renewal",
                        "Merchant",
                        "Name",
                    ],
                    ascending=True,
                )

                # ------------------------------------------
                # Renewal Priority
                # ------------------------------------------

                def priority(days):

                    if pd.isna(days):
                        return "Unknown"

                    if days <= 2:
                        return "🔴 Critical"

                    if days <= 5:
                        return "🟠 High"

                    return "🟢 Normal"

                renewals["Priority"] = renewals[
                    "Days Remaining"
                ].apply(priority)

                preferred_columns = [

                    "Priority",

                    "Name",

                    "Phone",

                    "Merchant",

                    "Merchant Category",

                    "Amount",

                    "Last Payment",

                    "Predicted Renewal",

                    "Days Remaining",

                    "Renewal Status",

                    "Transaction ID",

                ]

                columns = [

                    c

                    for c in preferred_columns

                    if c in renewals.columns

                ]

                renewals = renewals[
                    columns
                ]

                self._show_table(
                    renewals,
                    height=400,
                )

                st.download_button(
                    "Download Renewal Forecast",
                    renewals.to_csv(
                        index=False
                    ).encode("utf-8"),
                    file_name="renewal_forecast.csv",
                    mime="text/csv",
                )

        st.divider()
                # ==========================================================
        # Renewal Campaign Summary
        # ==========================================================

        if not renewals.empty:

            st.subheader("Renewal Campaign")

            c1, c2, c3 = st.columns(3)

            critical = (
                renewals["Priority"]
                == "🔴 Critical"
            ).sum()

            high = (
                renewals["Priority"]
                == "🟠 High"
            ).sum()

            normal = (
                renewals["Priority"]
                == "🟢 Normal"
            ).sum()

            c1.metric(
                "Critical",
                critical,
            )

            c2.metric(
                "High",
                high,
            )

            c3.metric(
                "Normal",
                normal,
            )

        st.divider()
                # ==========================================================
        # NSF Intelligence
        # ==========================================================

        st.header("NSF Intelligence")

        if nsf_df is None or nsf_df.empty:

            st.success(
                "No NSF alerts detected."
            )

        else:

            nsf = nsf_df.copy()

            # ----------------------------------------------
            # Clean Transaction ID
            # ----------------------------------------------

            if "Transaction ID" in nsf.columns:

                nsf["Transaction ID"] = (
                    nsf["Transaction ID"]
                    .apply(self._clean_transaction_id)
                )

            # ----------------------------------------------
            # Calculate Risk
            # ----------------------------------------------

            if (
                "Balance" in nsf.columns
                and
                "Amount" in nsf.columns
            ):

                def calculate_risk(row):

                    try:

                        balance = float(row["Balance"])
                        amount = float(row["Amount"])

                        if balance <= 0:
                            return "🔴 No Funds"

                        if balance < amount:
                            return "🟠 Insufficient"

                        if balance <= amount * 1.20:
                            return "🟡 Low Balance"

                        return "🟢 Healthy"

                    except Exception:

                        return "Unknown"

                nsf["Wallet Health"] = nsf.apply(
                    calculate_risk,
                    axis=1,
                )

            else:

                nsf["Wallet Health"] = "Unknown"

            # ----------------------------------------------
            # Priority
            # ----------------------------------------------

            priority_order = {

                "🔴 No Funds": 1,
                "🟠 Insufficient": 2,
                "🟡 Low Balance": 3,
                "🟢 Healthy": 4,
                "Unknown": 5,

            }

            nsf["Priority"] = nsf[
                "Wallet Health"
            ].map(priority_order)

            nsf = nsf.sort_values(
                "Priority"
            )
                        # ----------------------------------------------
            # KPI Cards
            # ----------------------------------------------

            red = (
                nsf["Wallet Health"]
                == "🔴 No Funds"
            ).sum()

            orange = (
                nsf["Wallet Health"]
                == "🟠 Insufficient"
            ).sum()

            yellow = (
                nsf["Wallet Health"]
                == "🟡 Low Balance"
            ).sum()

            green = (
                nsf["Wallet Health"]
                == "🟢 Healthy"
            ).sum()

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "No Funds",
                red,
            )

            c2.metric(
                "Insufficient",
                orange,
            )

            c3.metric(
                "Low Balance",
                yellow,
            )

            c4.metric(
                "Healthy",
                green,
            )

            st.divider()

            # ----------------------------------------------
            # Display Columns
            # ----------------------------------------------

            preferred = [

                "Wallet Health",

                "Name",

                "Phone",

                "Account ID",

                "Merchant",

                "Amount",

                "Balance",

                "Predicted Renewal",

                "Days Remaining",

                "Transaction ID",

            ]

            columns = [

                c

                for c in preferred

                if c in nsf.columns

            ]

            remaining = [

                c

                for c in nsf.columns

                if c not in columns

            ]

            nsf = nsf[
                columns + remaining
            ]

            self._show_table(
                nsf,
                height=450,
            )

            st.download_button(

                "Download NSF Report",

                nsf.to_csv(
                    index=False
                ).encode("utf-8"),

                file_name="nsf_intelligence.csv",

                mime="text/csv",

            )

        st.divider()
                # ==========================================================
        # Customer Outreach Queue
        # ==========================================================

        if nsf_df is not None and not nsf_df.empty:

            st.subheader(
                "Customer Outreach Queue"
            )

            outreach = nsf.copy()

            if "Wallet Health" in outreach.columns:

                outreach = outreach[
                    outreach["Wallet Health"].isin(
                        [
                            "🔴 No Funds",
                            "🟠 Insufficient",
                        ]
                    )
                ]

            if not outreach.empty:

                cols = [

                    "Name",

                    "Phone",

                    "Merchant",

                    "Amount",

                    "Balance",

                    "Predicted Renewal",

                    "Wallet Health",

                ]

                cols = [
                    c
                    for c in cols
                    if c in outreach.columns
                ]

                self._show_table(
                    outreach[cols],
                    height=300,
                )

            else:

                st.success(
                    "No customers require proactive outreach."
                )

        st.divider()
                # ==========================================================
        # Merchant Analytics
        # ==========================================================

        st.header("Merchant Analytics")

        if summary.empty:

            st.info(
                "No merchant analytics available."
            )

        else:

            merchant_summary = summary.copy()

            # ------------------------------------------------------
            # Merchant KPIs
            # ------------------------------------------------------

            total_merchants = (
                merchant_summary["Merchant"]
                .nunique()
                if "Merchant" in merchant_summary.columns
                else 0
            )

            total_categories = (
                merchant_summary["Merchant Category"]
                .nunique()
                if "Merchant Category" in merchant_summary.columns
                else 0
            )

            total_revenue = (
                merchant_summary["Amount"].sum()
                if "Amount" in merchant_summary.columns
                else 0
            )

            avg_subscription = (
                merchant_summary["Amount"].mean()
                if "Amount" in merchant_summary.columns
                else 0
            )

            k1, k2, k3, k4 = st.columns(4)

            k1.metric(
                "Merchants",
                f"{total_merchants:,}",
            )

            k2.metric(
                "Categories",
                f"{total_categories:,}",
            )

            k3.metric(
                "Monthly Revenue",
                f"{total_revenue:,.2f}",
            )

            k4.metric(
                "Average Subscription",
                f"{avg_subscription:,.2f}",
            )

            st.divider()
                        # ------------------------------------------------------
            # Merchant Performance
            # ------------------------------------------------------

            merchant_table = (
                merchant_summary
                .groupby("Merchant", as_index=False)
                .agg(
                    Customers=("Account ID", "nunique"),
                    Subscriptions=("Merchant", "count"),
                    Revenue=("Amount", "sum"),
                )
                .sort_values(
                    "Revenue",
                    ascending=False,
                )
            )

            st.subheader(
                "Top Subscription Merchants"
            )

            self._show_table(
                merchant_table,
                height=350,
            )
                        # ------------------------------------------------------
            # Revenue by Merchant
            # ------------------------------------------------------

            st.subheader(
                "Monthly Revenue by Merchant"
            )

            chart = merchant_table.set_index(
                "Merchant"
            )[["Revenue"]]

            st.bar_chart(
                chart
            )

            st.divider()
                        # ------------------------------------------------------
            # Category Analytics
            # ------------------------------------------------------

            if "Merchant Category" in merchant_summary.columns:

                category_table = (
                    merchant_summary
                    .groupby(
                        "Merchant Category",
                        as_index=False,
                    )
                    .agg(
                        Customers=("Account ID", "nunique"),
                        Revenue=("Amount", "sum"),
                    )
                    .sort_values(
                        "Revenue",
                        ascending=False,
                    )
                )

                st.subheader(
                    "Subscription Categories"
                )

                self._show_table(
                    category_table,
                    height=250,
                )

                chart = category_table.set_index(
                    "Merchant Category"
                )[["Revenue"]]

                st.bar_chart(
                    chart
                )

                st.divider()
                            # ------------------------------------------------------
            # Download
            # ------------------------------------------------------

            st.download_button(

                "Download Merchant Analytics",

                merchant_table.to_csv(
                    index=False
                ).encode("utf-8"),

                file_name="merchant_analytics.csv",

                mime="text/csv",

            )

        st.divider()
                # ==========================================================
        # Executive Insights
        # ==========================================================

        st.header("Executive Insights")

        if summary.empty:

            st.info(
                "No insights available."
            )

        else:

            insights = []

            # ------------------------------------------------------
            # Largest merchant
            # ------------------------------------------------------

            if "Merchant" in summary.columns:

                top_merchant = (
                    summary["Merchant"]
                    .value_counts()
                    .idxmax()
                )

                top_count = (
                    summary["Merchant"]
                    .value_counts()
                    .max()
                )

                insights.append(
                    f"🏆 {top_merchant} is your largest subscription merchant with {top_count:,} active subscriptions."
                )

            # ------------------------------------------------------
            # Revenue
            # ------------------------------------------------------

            if "Amount" in summary.columns:

                revenue = summary["Amount"].sum()

                insights.append(
                    f"💰 Estimated monthly recurring subscription volume is {revenue:,.2f}."
                )

            # ------------------------------------------------------
            # Renewals this week
            # ------------------------------------------------------

            if "Days Remaining" in summary.columns:

                renewals = (
                    summary["Days Remaining"] <= 7
                ).sum()

                insights.append(
                    f"📅 {renewals:,} subscriptions are scheduled to renew within the next 7 days."
                )

            # ------------------------------------------------------
            # Customer concentration
            # ------------------------------------------------------

            if (
                "Account ID" in summary.columns
                and
                "Merchant" in summary.columns
            ):

                avg = (
                    summary.groupby(
                        "Account ID"
                    )["Merchant"]
                    .count()
                    .mean()
                )

                insights.append(
                    f"👤 Customers have an average of {avg:.1f} active subscriptions."
                )

            # ------------------------------------------------------
            # Display
            # ------------------------------------------------------

            for item in insights:

                st.success(item)

        st.divider()
                # ==========================================================
        # Top Customers
        # ==========================================================

        st.header("Top Customers by Subscription Spend")

        if summary.empty:

            st.info(
                "No customer spending available."
            )

        else:

            if (
                "Account ID" in summary.columns
                and
                "Amount" in summary.columns
            ):

                customer_table = (

                    summary

                    .groupby(

                        [

                            "Account ID",

                            "Name",

                            "Phone",

                        ],

                        as_index=False,

                    )

                    .agg(

                        Active_Subscriptions=(

                            "Merchant",

                            "count",

                        ),

                        Monthly_Spend=(

                            "Amount",

                            "sum",

                        ),

                    )

                    .sort_values(

                        "Monthly_Spend",

                        ascending=False,

                    )

                )

                self._show_table(

                    customer_table.head(20),

                    height=400,

                )

                st.download_button(

                    "Download Customer Spend",

                    customer_table.to_csv(
                        index=False
                    ).encode("utf-8"),

                    file_name="customer_spend.csv",

                    mime="text/csv",

                )

        st.divider()
                # ==========================================================
        # Export Center
        # ==========================================================

        st.header("Export Center")

        export1, export2 = st.columns(2)

        with export1:

            st.download_button(

                "Export Subscription Summary",

                summary.to_csv(
                    index=False
                ).encode("utf-8"),

                file_name="subscription_summary.csv",

                mime="text/csv",

            )

        with export2:

            st.download_button(

                "Export Renewal Forecast",

                renewal_df.to_csv(
                    index=False
                ).encode("utf-8"),

                file_name="renewal_forecast.csv",

                mime="text/csv",

            )

        st.divider()
                # ==========================================================
        # Customer 360
        # ==========================================================

        st.header("Customer 360")

        if summary.empty:

            st.info(
                "No customer subscription data available."
            )

        else:

            customer_list = sorted(
                summary["Name"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_customer = st.selectbox(
                "Select Customer",
                customer_list,
            )

            customer_df = summary[
                summary["Name"] == selected_customer
            ].copy()
                        # ---------------------------------------------
            # Customer KPIs
            # ---------------------------------------------

            total_subscriptions = len(customer_df)

            monthly_spend = (
                customer_df["Amount"].sum()
                if "Amount" in customer_df.columns
                else 0
            )

            next_days = (
                customer_df["Days Remaining"].min()
                if (
                    "Days Remaining"
                    in customer_df.columns
                )
                else None
            )

            wallet_balance = None

            if (
                "Balance"
                in customer_df.columns
            ):

                wallet_balance = (
                    customer_df["Balance"]
                    .max()
                )

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "Subscriptions",
                total_subscriptions,
            )

            c2.metric(
                "Monthly Spend",
                f"{monthly_spend:,.2f}",
            )

            c3.metric(
                "Next Renewal",
                (
                    str(next_days)
                    + " Days"
                    if next_days is not None
                    else "-"
                ),
            )

            c4.metric(
                "Wallet Balance",
                (
                    f"{wallet_balance:,.2f}"
                    if wallet_balance is not None
                    else "-"
                ),
            )

            st.divider()
                        # ---------------------------------------------
            # Subscription Portfolio
            # ---------------------------------------------

            st.subheader(
                "Subscription Portfolio"
            )

            portfolio_columns = [

                "Merchant",

                "Merchant Category",

                "Amount",

                "Billing Frequency",

                "Last Payment",

                "Predicted Renewal",

                "Days Remaining",

                "Renewal Status",

            ]

            portfolio_columns = [

                c

                for c in portfolio_columns

                if c in customer_df.columns

            ]

            self._show_table(
                customer_df[
                    portfolio_columns
                ],
                height=300,
            )
                        # ---------------------------------------------
            # Renewal Timeline
            # ---------------------------------------------

            if (
                "Predicted Renewal"
                in customer_df.columns
            ):

                timeline = customer_df[
                    [

                        "Merchant",

                        "Predicted Renewal",

                        "Days Remaining",

                    ]

                ].sort_values(
                    "Predicted Renewal"
                )

                st.subheader(
                    "Renewal Timeline"
                )

                self._show_table(
                    timeline,
                    height=250,
                )
                            # ---------------------------------------------
            # Wallet Health
            # ---------------------------------------------

            if (
                "Balance"
                in customer_df.columns
                and
                "Amount"
                in customer_df.columns
            ):

                st.subheader(
                    "Wallet Health"
                )

                wallet = customer_df[
                    [

                        "Merchant",

                        "Amount",

                        "Balance",

                    ]

                ].copy()

                wallet["Coverage"] = (

                    wallet["Balance"]

                    /

                    wallet["Amount"]

                ).round(2)

                self._show_table(
                    wallet,
                    height=250,
                )

        st.divider()
                # ==========================================================
        # Dashboard Settings
        # ==========================================================

        st.header("Dashboard Settings")

        settings_col1, settings_col2 = st.columns(2)

        with settings_col1:

            renewal_window = st.slider(
                "Renewal Alert Window (Days)",
                min_value=1,
                max_value=30,
                value=8,
            )

            critical_threshold = st.slider(
                "Critical Threshold (Days)",
                min_value=1,
                max_value=7,
                value=2,
            )

        with settings_col2:

            warning_threshold = st.slider(
                "High Priority Threshold (Days)",
                min_value=2,
                max_value=14,
                value=5,
            )

            show_only_active = st.checkbox(
                "Show Active Subscriptions Only",
                value=True,
            )

        st.caption(
            "These settings affect only the dashboard view and do not modify stored subscription data."
        )

        st.divider()
                # ==========================================================
        # Executive Health Check
        # ==========================================================

        st.header("Executive Health Check")

        checks = []

        if summary.empty:

            checks.append(
                ("❌", "No active subscriptions detected.")
            )

        else:

            checks.append(
                ("✅", f"{len(summary):,} active subscriptions detected.")
            )

        if nsf_df is None or nsf_df.empty:

            checks.append(
                ("✅", "No NSF alerts currently detected.")
            )

        else:

            checks.append(
                (
                    "⚠️",
                    f"{len(nsf_df):,} subscriptions may fail because of insufficient funds.",
                )
            )

        if (
            not summary.empty
            and
            "Days Remaining" in summary.columns
        ):

            due = (
                summary["Days Remaining"] <= renewal_window
            ).sum()

            checks.append(
                (
                    "📅",
                    f"{due:,} subscriptions renew within the next {renewal_window} days.",
                )
            )

        for icon, message in checks:

            if icon == "❌":

                st.error(message)

            elif icon == "⚠️":

                st.warning(message)

            else:

                st.success(message)

        st.divider()
                # ==========================================================
        # Footer
        # ==========================================================

        st.caption(
            "Subscription Intelligence Dashboard • Version 2.0"
        )

        st.caption(
            "Designed for proactive subscription monitoring, renewal forecasting, and NSF prevention."
        )
        # ==========================================================
# Public Entry Point
# ==========================================================

def show_dashboard(
    classified_df: pd.DataFrame,
    renewal_df: pd.DataFrame,
    nsf_df: pd.DataFrame,
):
    """
    Render the Subscription Intelligence Dashboard.
    """

    Dashboard().render(
        classified_df=classified_df,
        renewal_df=renewal_df,
        nsf_df=nsf_df,
    )
    