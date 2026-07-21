from datetime import datetime, timedelta
import pandas as pd


def predict_renewals(subscriptions):

    if subscriptions.empty:
        return subscriptions

    today = pd.Timestamp.today().normalize()

    predictions = []

    for _, row in subscriptions.iterrows():

        last_charge = pd.to_datetime(row["Last Charge"])

        gap = row["Average Gap"]

        next_charge = last_charge + timedelta(days=gap)

        days_remaining = (next_charge - today).days

        if days_remaining < 0:
            status = "Overdue"

        elif days_remaining <= 3:
            status = "Due Soon"

        else:
            status = "Upcoming"

        record = row.to_dict()

        record["Next Charge"] = next_charge.date()

        record["Days Remaining"] = days_remaining

        record["Status"] = status

        predictions.append(record)

    return pd.DataFrame(predictions)