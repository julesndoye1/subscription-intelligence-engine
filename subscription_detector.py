import pandas as pd

from merchant import merchant_category


def detect_subscriptions(df):

    subscriptions = []

    # Ignore merchants we don't recognize
    filtered = df[df["Merchant"] != "OTHER"]

    grouped = filtered.groupby(["Account ID", "Merchant"])

    for (account_id, merchant), group in grouped:

        group = group.sort_values("Transaction Date")

        if len(group) < 2:
            continue

        # Customer information (same for all rows in the group)
        name = group.iloc[0]["Name"]
        phone = group.iloc[0]["Phone"]

        dates = list(group["Transaction Date"])
        amounts = list(group["Amount"])

        gaps = []

        for i in range(1, len(dates)):
            gaps.append((dates[i] - dates[i - 1]).days)

        average_gap = sum(gaps) / len(gaps)

        if 27 <= average_gap <= 33:
            frequency = "Monthly"
        elif 13 <= average_gap <= 15:
            frequency = "Biweekly"
        elif 6 <= average_gap <= 8:
            frequency = "Weekly"
        else:
            frequency = "Irregular"

        average_amount = sum(amounts) / len(amounts)

        confidence = 60

        if frequency != "Irregular":
            confidence += 20

        if len(group) >= 3:
            confidence += 10

        if len(group) >= 5:
            confidence += 10

        subscriptions.append({

            "Account ID": account_id,
            "Name": name,
            "Phone": phone,
            "Merchant": merchant,
            "Category": merchant_category(merchant),
            "Occurrences": len(group),
            "Average Amount": round(average_amount, 2),
            "Average Gap": round(average_gap, 1),
            "Frequency": frequency,
            "Confidence": confidence,
            "Last Charge": dates[-1]

        })

    return pd.DataFrame(subscriptions)