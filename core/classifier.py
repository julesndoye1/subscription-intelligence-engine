"""
core/classifier.py

Version 1

Simple subscription classifier.

The whitelist is the ONLY source of truth.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

from core.merchant_registry import MerchantRegistry


class SubscriptionClassifier:

    def __init__(self, data_dir: Optional[str] = None):

        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = (
                Path(__file__).resolve().parent.parent / "data"
            )

        self.registry = MerchantRegistry(self.data_dir)

    # ---------------------------------------------------------

    def classify(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:

        if df.empty:
            return df.copy()

        work = df.copy()

        # -----------------------------------------------------
        # Ensure required columns exist
        # -----------------------------------------------------

        required = [
            "Transaction For",
            "Amount",
        ]

        for col in required:

            if col not in work.columns:
                raise ValueError(
                    f"Missing required column: {col}"
                )

        # -----------------------------------------------------
        # Create output columns
        # -----------------------------------------------------

        work["Normalized Merchant"] = ""
        work["Subscription Status"] = "Not Subscription"
        work["Merchant Category"] = ""
        work["Billing Frequency"] = ""
        work["Merchant Country"] = ""
        work["Merchant Risk"] = ""

        # -----------------------------------------------------
        # Classify each transaction
        # -----------------------------------------------------

        for index, row in work.iterrows():

            merchant_name = row["Transaction For"]

            normalized = self.registry.normalize(
                merchant_name
            )

            work.at[
                index,
                "Normalized Merchant",
            ] = normalized

            merchant = self.registry.find(
                normalized
            )

            if merchant is None:
                continue

            work.at[
                index,
                "Subscription Status",
            ] = "Confirmed Subscription"

            work.at[
                index,
                "Merchant Category",
            ] = merchant.category

            work.at[
                index,
                "Billing Frequency",
            ] = merchant.frequency

            work.at[
                index,
                "Merchant Country",
            ] = merchant.country

            work.at[
                index,
                "Merchant Risk",
            ] = merchant.risk

        return work

    # ---------------------------------------------------------

    def summary(
        self,
        classified_df: pd.DataFrame,
    ) -> dict:

        subscriptions = classified_df[
            classified_df["Subscription Status"]
            == "Confirmed Subscription"
        ]

        return {

            "Total Transactions":
                len(classified_df),

            "Detected Subscriptions":
                len(subscriptions),

            "Active Customers":
                subscriptions["Account ID"].nunique()
                if "Account ID" in subscriptions.columns
                else 0,

            "Subscription Merchants":
                subscriptions["Normalized Merchant"].nunique()
                if "Normalized Merchant" in subscriptions.columns
                else 0,
        }