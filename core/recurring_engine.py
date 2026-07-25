"""
Recurring Pattern Engine
------------------------

Detects recurring payment patterns from transaction history.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pandas as pd


@dataclass
class RecurringSubscription:

    account_id: str
    merchant: str
    occurrences: int
    average_amount: float
    average_interval_days: float
    confidence: float


class RecurringPatternEngine:

    def __init__(
        self,
        interval_tolerance: int = 5,
        amount_tolerance: float = 0.15,
        minimum_occurrences: int = 2,
    ):
        self.interval_tolerance = interval_tolerance
        self.amount_tolerance = amount_tolerance
        self.minimum_occurrences = minimum_occurrences

    # ---------------------------------------------------------

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:

        if df.empty:
            return pd.DataFrame()

        work = df.copy()

        work["Transaction Date"] = pd.to_datetime(
            work["Transaction Date"],
            errors="coerce",
        )

        work = work.sort_values("Transaction Date")

        subscriptions: List[RecurringSubscription] = []

        grouped = work.groupby(
            ["Account ID", "Normalized Merchant"]
        )

        for (account, merchant), group in grouped:

            if len(group) < self.minimum_occurrences:
                continue

            group = group.sort_values("Transaction Date")

            amounts = group["Amount"].astype(float)

            dates = group["Transaction Date"]

            intervals = dates.diff().dt.days.dropna()

            if intervals.empty:
                continue

            avg_interval = intervals.mean()

            avg_amount = amounts.mean()

            amount_cv = amounts.std(ddof=0) / max(avg_amount, 1)

            interval_cv = intervals.std(ddof=0) / max(avg_interval, 1)

            confidence = 100.0

            confidence -= amount_cv * 50

            confidence -= interval_cv * 50

            confidence = max(0, min(100, confidence))

            subscriptions.append(

                RecurringSubscription(
                    account_id=str(account),
                    merchant=merchant,
                    occurrences=len(group),
                    average_amount=round(avg_amount, 2),
                    average_interval_days=round(avg_interval, 1),
                    confidence=round(confidence, 1),
                )

            )

        return pd.DataFrame([s.__dict__ for s in subscriptions])