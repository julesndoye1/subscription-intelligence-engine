"""
Analytics Engine
----------------

Generates business KPIs from classified subscriptions,
renewal predictions, and NSF alerts.
"""

from __future__ import annotations

import pandas as pd


class AnalyticsEngine:

    def __init__(self):
        pass

    # ---------------------------------------------------------

    def subscription_summary(
        self,
        classified_df: pd.DataFrame,
    ) -> dict:

        if classified_df.empty:
            return {}

        subscriptions = classified_df[
            classified_df["Subscription Status"]
            != "Not Subscription"
        ]

        total_transactions = len(classified_df)

        total_subscriptions = len(subscriptions)

        active_customers = (
            subscriptions["Account ID"]
            .nunique()
        )

        monthly_spend = (
            subscriptions["Amount"]
            .fillna(0)
            .sum()
        )

        average_subscription = (
            subscriptions["Amount"]
            .fillna(0)
            .mean()
        )

        return {

            "Total Transactions":
                total_transactions,

            "Detected Subscriptions":
                total_subscriptions,

            "Active Customers":
                active_customers,

            "Monthly Subscription Spend":
                round(monthly_spend, 2),

            "Average Subscription":
                round(average_subscription, 2),
        }

    # ---------------------------------------------------------

    def merchant_summary(
        self,
        classified_df: pd.DataFrame,
    ) -> pd.DataFrame:

        subscriptions = classified_df[
            classified_df["Subscription Status"]
            != "Not Subscription"
        ]

        if subscriptions.empty:
            return pd.DataFrame()

        report = (
            subscriptions
            .groupby("Normalized Merchant")
            .agg(

                Customers=(
                    "Account ID",
                    "nunique",
                ),

                Transactions=(
                    "Transaction ID",
                    "count",
                ),

                Revenue=(
                    "Amount",
                    "sum",
                ),

                Average=(
                    "Amount",
                    "mean",
                ),
            )
            .reset_index()
        )

        report = report.sort_values(
            "Revenue",
            ascending=False,
        )

        return report

    # ---------------------------------------------------------

    def category_summary(
        self,
        classified_df: pd.DataFrame,
    ) -> pd.DataFrame:

        subscriptions = classified_df[
            classified_df["Subscription Status"]
            != "Not Subscription"
        ]

        if subscriptions.empty:
            return pd.DataFrame()

        return (

            subscriptions

            .groupby(
                "Merchant Category"
            )

            .agg(

                Customers=(
                    "Account ID",
                    "nunique",
                ),

                Revenue=(
                    "Amount",
                    "sum",
                ),

                Transactions=(
                    "Transaction ID",
                    "count",
                ),
            )

            .reset_index()

            .sort_values(
                "Revenue",
                ascending=False,
            )

        )

    # ---------------------------------------------------------

    def renewal_summary(
        self,
        renewal_df: pd.DataFrame,
    ) -> dict:

        if renewal_df.empty:
            return {}

        return {

            "Scheduled":

                len(

                    renewal_df[
                        renewal_df[
                            "Renewal Status"
                        ]
                        == "Scheduled"
                    ]

                ),

            "Upcoming":

                len(

                    renewal_df[
                        renewal_df[
                            "Renewal Status"
                        ]
                        == "Upcoming"
                    ]

                ),

            "Due Soon":

                len(

                    renewal_df[
                        renewal_df[
                            "Renewal Status"
                        ]
                        == "Due Soon"
                    ]

                ),

            "Overdue":

                len(

                    renewal_df[
                        renewal_df[
                            "Renewal Status"
                        ]
                        == "Overdue"
                    ]

                ),

        }

    # ---------------------------------------------------------

    def nsf_summary(
        self,
        nsf_df: pd.DataFrame,
    ) -> dict:

        if nsf_df.empty:

            return {

                "NSF Alerts": 0,

                "Renewal Missing": 0,

            }

        return {

            "NSF Alerts":

                len(

                    nsf_df[
                        nsf_df[
                            "Alert"
                        ]
                        == "Insufficient Funds"
                    ]

                ),

            "Renewal Missing":

                len(

                    nsf_df[
                        nsf_df[
                            "Alert"
                        ]
                        == "Renewal Missing"
                    ]

                ),

        }

    # ---------------------------------------------------------

    def executive_dashboard(
        self,
        classified_df,
        renewal_df,
        nsf_df,
    ):

        return {

            "subscriptions":

                self.subscription_summary(
                    classified_df
                ),

            "renewals":

                self.renewal_summary(
                    renewal_df
                ),

            "nsf":

                self.nsf_summary(
                    nsf_df
                ),

            "merchant_table":

                self.merchant_summary(
                    classified_df
                ),

            "category_table":

                self.category_summary(
                    classified_df
                ),

        }