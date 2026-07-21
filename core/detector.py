"""
=========================================================
Subscription Intelligence Agent
Subscription Detection Engine
=========================================================

Detects recurring subscriptions from transaction history.

Author:
Subscription Intelligence Team

Version:
1.1
"""

import pandas as pd

from core.merchant import (
    normalize,
    merchant_category,
    merchant_frequency,
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MONTHLY_MIN = 25
MONTHLY_MAX = 35

WEEKLY_MIN = 6
WEEKLY_MAX = 8

YEARLY_MIN = 360
YEARLY_MAX = 370


# ---------------------------------------------------------
# Detect Subscriptions
# ---------------------------------------------------------

def detect_subscriptions(df, confidence_threshold=50):
    """
    Detect recurring subscriptions.

    Parameters
    ----------
    df : pandas.DataFrame

    confidence_threshold : int

    Returns
    -------
    pandas.DataFrame
    """

    data = df.copy()

    # ---------------------------------------------
    # Only successful transactions
    # ---------------------------------------------

    data["Status"] = (
        data["Status"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    data = data[
        data["Status"] == "SUCCESS"
    ].copy()

    if data.empty:
        return pd.DataFrame()

    # ---------------------------------------------
    # Normalize merchants
    # ---------------------------------------------

    data["Merchant"] = (
        data["Transaction For"]
        .apply(normalize)
    )

    data = data[
        data["Merchant"] != "OTHER"
    ]

    if data.empty:
        return pd.DataFrame()

    subscriptions = []

    grouped = data.groupby(
        ["Account ID", "Merchant"]
    )

    for (account_id, merchant), group in grouped:

        group = group.sort_values(
            "Transaction Date"
        )

        # Need at least two successful payments
        if len(group) < 2:
            continue

        intervals = (
            group["Transaction Date"]
            .diff()
            .dt.days
            .dropna()
        )

        if intervals.empty:
            continue

        average_interval = round(intervals.mean())

        average_amount = round(
            group["Amount"].mean(),
            2
        )

        latest = group.iloc[-1]

        confidence = calculate_confidence(
            group,
            average_interval,
            average_amount,
        )

        if confidence < confidence_threshold:
            continue

        subscriptions.append({

            "Account ID":
                account_id,

            "Customer":
                latest["Name"],

            "Merchant":
                merchant,

            "Category":
                merchant_category(merchant),

            "Frequency":
                merchant_frequency(merchant),

            "Occurrences":
                len(group),

            "Average Amount":
                average_amount,

            "Last Amount":
                latest["Amount"],

            "First Charge":
                group.iloc[0]["Transaction Date"],

            "Last Charge":
                latest["Transaction Date"],

            "Average Interval":
                average_interval,

            "Confidence":
                confidence,
        })

    if len(subscriptions) == 0:
        return pd.DataFrame()

    subscriptions = pd.DataFrame(subscriptions)

    subscriptions = subscriptions.sort_values(
        by=[
            "Confidence",
            "Occurrences",
        ],
        ascending=False,
    )

    subscriptions.reset_index(
        drop=True,
        inplace=True,
    )

    return subscriptions


# ---------------------------------------------------------
# Confidence Score
# ---------------------------------------------------------

def calculate_confidence(
    transactions,
    average_interval,
    average_amount,
):
    """
    Calculate confidence score (0-100).
    """

    score = 0

    # ---------------------------------------------
    # Occurrences (40 points)
    # ---------------------------------------------

    count = len(transactions)

    if count >= 8:
        score += 40

    elif count >= 6:
        score += 35

    elif count >= 4:
        score += 30

    elif count >= 2:
        score += 20

    # ---------------------------------------------
    # Billing interval (35 points)
    # ---------------------------------------------

    if MONTHLY_MIN <= average_interval <= MONTHLY_MAX:
        score += 35

    elif WEEKLY_MIN <= average_interval <= WEEKLY_MAX:
        score += 30

    elif YEARLY_MIN <= average_interval <= YEARLY_MAX:
        score += 35

    # ---------------------------------------------
    # Stable amount (25 points)
    # ---------------------------------------------

    std = transactions["Amount"].std()

    if pd.isna(std):
        std = 0

    if average_amount > 0:
        variation = (std / average_amount) * 100
    else:
        variation = 100

    if variation < 2:
        score += 25

    elif variation < 5:
        score += 20

    elif variation < 10:
        score += 15

    elif variation < 20:
        score += 10

    return min(score, 100)


# ---------------------------------------------------------
# Dashboard Summary
# ---------------------------------------------------------

def subscription_summary(df):

    if df.empty:

        return {
            "subscriptions": 0,
            "customers": 0,
            "monthly_spend": 0,
        }

    return {

        "subscriptions":
            len(df),

        "customers":
            df["Account ID"].nunique(),

        "monthly_spend":
            round(
                df["Average Amount"].sum(),
                2,
            ),
    }


# ---------------------------------------------------------
# Self Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("Subscription Detection Engine")
    print("=" * 50)
    print("Module loaded successfully.")