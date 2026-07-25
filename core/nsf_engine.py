"""
NSF Intelligence Engine
-----------------------

Detects subscription renewal failures caused by
insufficient funds.
"""

from __future__ import annotations

import pandas as pd


class NSFEngine:

    def __init__(self, renewal_window_days=3):
        self.renewal_window_days = renewal_window_days

    # -------------------------------------------------------------

    def detect(
        self,
        renewals: pd.DataFrame,
        transactions: pd.DataFrame,
    ) -> pd.DataFrame:

        if renewals.empty:
            return pd.DataFrame()

        tx = transactions.copy()

        tx["Transaction Date"] = pd.to_datetime(
            tx["Transaction Date"],
            errors="coerce",
        )

        alerts = []

        for _, renewal in renewals.iterrows():

            account = renewal["Account ID"]

            merchant = renewal["Merchant"]

            renewal_date = pd.to_datetime(
                renewal["Predicted Renewal"]
            )

            candidate = tx[
                (tx["Account ID"] == account)
                &
                (tx["Normalized Merchant"] == merchant)
            ]

            candidate = candidate[
                (
                    candidate["Transaction Date"]
                    >= renewal_date
                    - pd.Timedelta(days=self.renewal_window_days)
                )
                &
                (
                    candidate["Transaction Date"]
                    <= renewal_date
                    + pd.Timedelta(days=self.renewal_window_days)
                )
            ]

            if candidate.empty:

                alerts.append(
                    {
                        "Account ID": account,
                        "Merchant": merchant,
                        "Alert": "Renewal Missing",
                        "Severity": "Medium",
                        "Recommendation":
                            "Check customer activity.",
                    }
                )

                continue

            failed = candidate[
                candidate["Status"]
                .astype(str)
                .str.upper()
                .str.contains(
                    "FAIL|DECLIN|NSF|INSUFFICIENT",
                    regex=True,
                    na=False,
                )
            ]

            if failed.empty:
                continue

            latest = failed.iloc[-1]

            alerts.append(
                {
                    "Account ID": account,
                    "Merchant": merchant,
                    "Transaction Date":
                        latest["Transaction Date"],
                    "Amount":
                        latest["Amount"],
                    "Alert":
                        "Insufficient Funds",
                    "Severity":
                        "High",
                    "Recommendation":
                        (
                            "Notify customer before "
                            "next renewal."
                        ),
                }
            )

        return pd.DataFrame(alerts)