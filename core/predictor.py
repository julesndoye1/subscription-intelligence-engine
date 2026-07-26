"""
core/predictor.py

Renewal Predictor - Version 2

Predicts future renewal dates for merchants contained in
subscription_whitelist.csv.
"""

from __future__ import annotations

from datetime import timedelta

import pandas as pd


class RenewalPredictor:

    def __init__(self):
        pass

    # ---------------------------------------------------------

    def predict(
        self,
        classified_df: pd.DataFrame,
    ) -> pd.DataFrame:

        if classified_df.empty:
            return pd.DataFrame()

        work = classified_df.copy()

        # ---------------------------------------------------------
        # Convert Transaction Date
        # ---------------------------------------------------------

        work["Transaction Date"] = pd.to_datetime(
            work["Transaction Date"],
            errors="coerce",
        )

        work = work.dropna(
            subset=["Transaction Date"]
        )

        # ---------------------------------------------------------
        # Keep only confirmed subscriptions
        # ---------------------------------------------------------

        subscriptions = work[
            work["Subscription Status"]
            == "Confirmed Subscription"
        ].copy()

        if subscriptions.empty:
            return pd.DataFrame()

        predictions = []

        grouped = subscriptions.groupby(
            [
                "Account ID",
                "Normalized Merchant",
            ]
        )

        # ---------------------------------------------------------

        for (account, merchant), group in grouped:

            group = group.sort_values(
                "Transaction Date"
            )

            last_txn = group.iloc[-1]

            # -------------------------------------------------
            # Estimate renewal interval
            # -------------------------------------------------

            if len(group) >= 2:

                intervals = (
                    group["Transaction Date"]
                    .diff()
                    .dt.days
                    .dropna()
                )

                average_interval = int(
                    round(intervals.mean())
                )

            else:

                frequency = str(
                    last_txn.get(
                        "Billing Frequency",
                        "Monthly",
                    )
                )

                defaults = {

                    "Daily": 1,

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

            # -------------------------------------------------
            # Predict next renewal
            # -------------------------------------------------

            renewal_date = (
                last_txn["Transaction Date"]
                + timedelta(days=average_interval)
            )

            days_remaining = (
                renewal_date.normalize()
                - pd.Timestamp.today().normalize()
            ).days

            # -------------------------------------------------
            # Renewal status
            # -------------------------------------------------

            if days_remaining < 0:

                status = "Overdue"

            elif days_remaining <= 3:

                status = "Due Soon"

            elif days_remaining <= 7:

                status = "Upcoming"

            else:

                status = "Scheduled"

            # -------------------------------------------------
            # Build prediction record
            # -------------------------------------------------

            predictions.append({

                "Name":
                    last_txn.get(
                        "Name",
                        "",
                    ),

                "Phone":
                    last_txn.get(
                        "Phone",
                        "",
                    ),

                "Account ID":
                    account,

                "Merchant":
                    merchant,

                "Merchant Category":
                    last_txn.get(
                        "Merchant Category",
                        "",
                    ),

                "Amount":
                    last_txn.get(
                        "Amount",
                        0,
                    ),

                "Billing Frequency":
                    last_txn.get(
                        "Billing Frequency",
                        "",
                    ),

                "Last Payment":
                    last_txn[
                        "Transaction Date"
                    ],

                "Predicted Renewal":
                    renewal_date,

                "Average Interval":
                    average_interval,

                "Days Remaining":
                    days_remaining,

                "Renewal Status":
                    status,

                "Transaction ID":
                    str(
                        last_txn.get(
                            "Transaction ID",
                            "",
                        )
                    ),

            })

        # ---------------------------------------------------------
        # Build DataFrame
        # ---------------------------------------------------------

        prediction_df = pd.DataFrame(
            predictions
        )

        if prediction_df.empty:
            return prediction_df

        # ---------------------------------------------------------
        # Clean Transaction ID
        # ---------------------------------------------------------

        prediction_df["Transaction ID"] = (
            prediction_df["Transaction ID"]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace(".0", "", regex=False)
        )

        # ---------------------------------------------------------
        # Sort by nearest renewal
        # ---------------------------------------------------------

        prediction_df = prediction_df.sort_values(
            [
                "Days Remaining",
                "Predicted Renewal",
                "Merchant",
            ]
        )

        prediction_df.reset_index(
            drop=True,
            inplace=True,
        )

        return prediction_df