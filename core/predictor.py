"""
Renewal Predictor v2
--------------------

Predicts the next subscription renewal date
using historical recurring payment patterns.
"""

from __future__ import annotations

from datetime import timedelta

import pandas as pd


class RenewalPredictor:

    def __init__(self):
        pass

    # ---------------------------------------------------------

    def predict(self, classified_df: pd.DataFrame) -> pd.DataFrame:

        if classified_df.empty:
            return pd.DataFrame()

        work = classified_df.copy()

        work["Transaction Date"] = pd.to_datetime(
            work["Transaction Date"],
            errors="coerce",
        )

        predictions = []

        grouped = work.groupby(
            ["Account ID", "Normalized Merchant"]
        )

        for (account, merchant), group in grouped:

            subscriptions = group[
                group["Subscription Status"] != "Not Subscription"
            ]

            if subscriptions.empty:
                continue

            subscriptions = subscriptions.sort_values(
                "Transaction Date"
            )

            last_txn = subscriptions.iloc[-1]

            if len(subscriptions) >= 2:

                intervals = (
                    subscriptions["Transaction Date"]
                    .diff()
                    .dt.days
                    .dropna()
                )

                average_interval = int(round(intervals.mean()))

            else:

                frequency = last_txn["Billing Frequency"]

                defaults = {
                    "Weekly": 7,
                    "Biweekly": 14,
                    "Monthly": 30,
                    "Quarterly": 90,
                    "Yearly": 365,
                }

                average_interval = defaults.get(
                    frequency,
                    30,
                )

            renewal_date = (
                last_txn["Transaction Date"]
                + timedelta(days=average_interval)
            )

            days_remaining = (
                renewal_date.normalize()
                - pd.Timestamp.today().normalize()
            ).days

            if days_remaining < 0:
                status = "Overdue"

            elif days_remaining <= 3:
                status = "Due Soon"

            elif days_remaining <= 7:
                status = "Upcoming"

            else:
                status = "Scheduled"

            predictions.append(
                {
                    "Account ID": account,
                    "Merchant": merchant,
                    "Last Payment": last_txn["Transaction Date"],
                    "Predicted Renewal": renewal_date,
                    "Average Interval": average_interval,
                    "Days Remaining": days_remaining,
                    "Renewal Status": status,
                    "Subscription Confidence": last_txn[
                        "Subscription Confidence"
                    ],
                }
            )

        return pd.DataFrame(predictions)