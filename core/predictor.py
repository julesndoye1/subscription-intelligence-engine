
"""
predictor.py

Predicts the next subscription renewal date.
"""

from __future__ import annotations

from datetime import timedelta
import pandas as pd

from core.constants import (
    PREDICTION_COLUMNS,
    MONTHLY,
    WEEKLY,
    BIWEEKLY,
    QUARTERLY,
    YEARLY,
)
from core.utils import empty_dataframe


FREQUENCY_DAYS = {
    MONTHLY: 30,
    WEEKLY: 7,
    BIWEEKLY: 14,
    QUARTERLY: 91,
    YEARLY: 365,
}


class RenewalPredictor:
    """Predict future subscription renewals."""

    def predict(self, subscriptions: pd.DataFrame) -> pd.DataFrame:

        if subscriptions.empty:
            return empty_dataframe(PREDICTION_COLUMNS)

        today = pd.Timestamp.today().normalize()
        predictions = []

        for _, row in subscriptions.iterrows():

            frequency = row.get("Frequency", "Unknown")
            interval = FREQUENCY_DAYS.get(
                frequency,
                row.get("Average Interval", 30) or 30,
            )

            last_charge = pd.to_datetime(row["Last Charge"])

            renewal = last_charge + timedelta(days=int(interval))

            predictions.append({
                "Account ID": row["Account ID"],
                "Customer": row["Customer"],
                "Merchant": row["Merchant"],
                "Category": row["Category"],
                "Predicted Renewal": renewal,
                "Expected Amount": row["Average Amount"],
                "Confidence": row["Confidence"],
                "Days Remaining": (renewal - today).days,
            })

        return (
            pd.DataFrame(predictions)
            .sort_values("Predicted Renewal")
            .reset_index(drop=True)
        )


def predict_renewals(subscriptions: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper."""
    return RenewalPredictor().predict(subscriptions)


def upcoming_renewals(
    predictions: pd.DataFrame,
    days: int = 7,
) -> pd.DataFrame:
    """Return renewals due within the next N days."""

    if predictions.empty:
        return predictions

    return predictions[
        (predictions["Days Remaining"] >= 0)
        & (predictions["Days Remaining"] <= days)
    ].copy()


def prediction_summary(predictions: pd.DataFrame) -> dict:
    """Summary metrics for dashboard."""

    if predictions.empty:
        return {
            "renewals": 0,
            "due_this_week": 0,
            "expected_spend": 0,
        }

    due = upcoming_renewals(predictions, 7)

    return {
        "renewals": len(predictions),
        "due_this_week": len(due),
        "expected_spend": round(
            predictions["Expected Amount"].sum(),
            2,
        ),
    }
