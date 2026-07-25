"""
core/recurring_engine.py
Phase 3 - Recurring Pattern Engine
"""
from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass
class RecurringSubscription:
    account_id: str
    merchant: str
    occurrences: int
    average_amount: float
    average_interval_days: float
    first_date: pd.Timestamp
    last_date: pd.Timestamp
    confidence: float


class RecurringPatternEngine:
    def __init__(
        self,
        merchant_column="Normalized Merchant",
        account_column="Account ID",
        amount_column="Amount",
        date_column="Transaction Date",
        min_occurrences=2,
        amount_tolerance=0.15,
    ):
        self.merchant_column = merchant_column
        self.account_column = account_column
        self.amount_column = amount_column
        self.date_column = date_column
        self.min_occurrences = min_occurrences
        self.amount_tolerance = amount_tolerance

    def detect(self, df: pd.DataFrame) -> pd.DataFrame:
        required = [
            self.account_column,
            self.merchant_column,
            self.amount_column,
            self.date_column,
        ]
        for c in required:
            if c not in df.columns:
                raise KeyError(f"Missing required column: {c}")

        work = df.copy()
        work[self.date_column] = pd.to_datetime(work[self.date_column], errors="coerce")

        records = []

        grouped = work.groupby([self.account_column, self.merchant_column])

        for (account, merchant), g in grouped:
            g = g.sort_values(self.date_column)

            if len(g) < self.min_occurrences:
                continue

            dates = g[self.date_column].dropna()

            if len(dates) < self.min_occurrences:
                continue

            intervals = dates.diff().dt.days.dropna()

            avg_interval = float(intervals.mean()) if len(intervals) else 0.0

            amounts = pd.to_numeric(
                g[self.amount_column], errors="coerce"
            ).dropna()

            avg_amount = float(amounts.mean()) if len(amounts) else 0.0

            confidence = self._confidence(
                len(g),
                avg_interval,
                amounts.std() if len(amounts) > 1 else 0.0,
                avg_amount,
            )

            records.append(
                RecurringSubscription(
                    account_id=str(account),
                    merchant=str(merchant),
                    occurrences=len(g),
                    average_amount=round(avg_amount, 2),
                    average_interval_days=round(avg_interval, 1),
                    first_date=dates.min(),
                    last_date=dates.max(),
                    confidence=round(confidence, 1),
                ).__dict__
            )

        return pd.DataFrame(records)

    def _confidence(self, occurrences, avg_interval, std_amount, avg_amount):
        score = 40.0

        score += min(occurrences * 10, 30)

        if 27 <= avg_interval <= 33:
            score += 20
        elif 6 <= avg_interval <= 8:
            score += 15

        if avg_amount > 0:
            variation = std_amount / avg_amount if avg_amount else 0
            if variation <= self.amount_tolerance:
                score += 10

        return min(score, 100.0)
