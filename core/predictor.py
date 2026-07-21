"""
=========================================================
Subscription Intelligence Agent
Renewal Prediction Engine
=========================================================

Predicts the next renewal date for detected subscriptions.

Author:
Subscription Intelligence Team

Version:
1.0
"""

from datetime import timedelta
import pandas as pd


# ---------------------------------------------------------
# Predict Renewals
# ---------------------------------------------------------

def predict_renewals(subscriptions):
    """
    Predict renewal dates for subscriptions.

    Parameters
    ----------
    subscriptions : pandas.DataFrame

    Returns
    -------
    pandas.DataFrame
    """

    if subscriptions.empty:
        return subscriptions

    df = subscriptions.copy()

    today = pd.Timestamp.today().normalize()

    next_dates = []
    days_remaining = []
    statuses = []
    monthly_spend = []
    annual_spend = []

    for _, row in df.iterrows():

        interval = row["Average Interval"]

        # Default to monthly if interval is invalid
        if pd.isna(interval) or interval <= 0:
            interval = 30

        last_charge = pd.to_datetime(row["Last Charge"])

        next_charge = last_charge + timedelta(days=int(interval))

        days = (next_charge - today).days

        if days < 0:
            status = "Overdue"

        elif days <= 7:
            status = "Due Soon"

        else:
            status = "Upcoming"

        next_dates.append(next_charge)
        days_remaining.append(days)
        statuses.append(status)

        amount = row["Average Amount"]

        monthly_spend.append(round(amount, 2))

        if interval >= 360:
            annual = amount

        elif interval >= 80:
            annual = amount * 4

        elif interval >= 25:
            annual = amount * 12

        elif interval >= 6:
            annual = amount * 52

        else:
            annual = amount

        annual_spend.append(round(annual, 2))

    df["Next Renewal"] = next_dates
    df["Days Remaining"] = days_remaining
    df["Renewal Status"] = statuses
    df["Estimated Monthly Spend"] = monthly_spend
    df["Estimated Annual Spend"] = annual_spend

    df = df.sort_values(
        by=[
            "Days Remaining",
            "Confidence"
        ],
        ascending=[True, False]
    )

    df.reset_index(drop=True, inplace=True)

    return df


# ---------------------------------------------------------
# Dashboard Metrics
# ---------------------------------------------------------

def renewal_metrics(df):
    """
    Calculate dashboard metrics.
    """

    if df.empty:

        return {
            "Upcoming": 0,
            "Due Soon": 0,
            "Overdue": 0,
            "Monthly Spend": 0,
            "Annual Spend": 0,
        }

    return {

        "Upcoming":
            len(df[df["Renewal Status"] == "Upcoming"]),

        "Due Soon":
            len(df[df["Renewal Status"] == "Due Soon"]),

        "Overdue":
            len(df[df["Renewal Status"] == "Overdue"]),

        "Monthly Spend":
            round(
                df["Estimated Monthly Spend"].sum(),
                2
            ),

        "Annual Spend":
            round(
                df["Estimated Annual Spend"].sum(),
                2
            ),
    }


# ---------------------------------------------------------
# Upcoming Renewals
# ---------------------------------------------------------

def upcoming_renewals(df, days=7):
    """
    Return subscriptions renewing within N days.
    """

    if df.empty:
        return df

    return df[
        (df["Days Remaining"] >= 0)
        &
        (df["Days Remaining"] <= days)
    ].copy()


# ---------------------------------------------------------
# Overdue Renewals
# ---------------------------------------------------------

def overdue_renewals(df):
    """
    Return overdue subscriptions.
    """

    if df.empty:
        return df

    return df[
        df["Renewal Status"] == "Overdue"
    ].copy()


# ---------------------------------------------------------
# Self Test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("Renewal Prediction Engine")
    print("=" * 50)
    print()
    print("Module loaded successfully.")