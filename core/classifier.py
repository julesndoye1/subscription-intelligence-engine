"""
Subscription Classifier v2
--------------------------

Combines merchant normalization,
merchant knowledge,
and recurring payment analysis
to classify subscriptions.
"""

from __future__ import annotations

import pandas as pd

from core.normalizer import MerchantNormalizer
from core.merchant_db import MerchantDatabase
from core.recurring_engine import RecurringPatternEngine


class SubscriptionClassifier:

    def __init__(self):

        self.normalizer = MerchantNormalizer()

        self.database = MerchantDatabase()

        self.engine = RecurringPatternEngine()

    # ---------------------------------------------------------

    def classify(self, df: pd.DataFrame):

        if df.empty:
            return pd.DataFrame()

        work = df.copy()

        # -----------------------------------------------
        # Normalize merchant names
        # -----------------------------------------------

        work["Normalized Merchant"] = work[
            "Transaction For"
        ].fillna("").apply(
            self.normalizer.normalize
        )

        # -----------------------------------------------
        # Merchant category
        # -----------------------------------------------

        work["Merchant Category"] = work[
            "Normalized Merchant"
        ].apply(
            self.database.category
        )

        # -----------------------------------------------
        # Frequency
        # -----------------------------------------------

        work["Expected Frequency"] = work[
            "Normalized Merchant"
        ].apply(
            self.database.frequency
        )

        # -----------------------------------------------
        # Risk
        # -----------------------------------------------

        work["Merchant Risk"] = work[
            "Normalized Merchant"
        ].apply(
            self.database.risk
        )

        # -----------------------------------------------
        # Recurring analysis
        # -----------------------------------------------

        recurring = self.engine.detect(work)

        recurring_lookup = {}

        if not recurring.empty:

            for _, row in recurring.iterrows():

                recurring_lookup[
                    (
                        str(row["account_id"]),
                        row["merchant"],
                    )
                ] = row

        # -----------------------------------------------
        # Classification
        # -----------------------------------------------

        labels = []

        confidence_scores = []

        next_frequency = []

        for _, row in work.iterrows():

            key = (
                str(row["Account ID"]),
                row["Normalized Merchant"],
            )

            recurring_info = recurring_lookup.get(key)

            if recurring_info is None:

                labels.append("Not Subscription")

                confidence_scores.append(0)

                next_frequency.append("Unknown")

                continue

            confidence = recurring_info["confidence"]

            if confidence >= 90:

                label = "Confirmed Subscription"

            elif confidence >= 75:

                label = "Likely Subscription"

            elif confidence >= 50:

                label = "Possible Subscription"

            else:

                label = "Not Subscription"

            labels.append(label)

            confidence_scores.append(confidence)

            next_frequency.append(
                row["Expected Frequency"]
            )

        work["Subscription Status"] = labels

        work["Subscription Confidence"] = confidence_scores

        work["Billing Frequency"] = next_frequency

        return work