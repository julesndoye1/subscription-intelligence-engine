"""
=========================================================
Subscription Intelligence Agent
Merchant Intelligence Module
=========================================================

This module loads the merchant database from CSV and
provides functions for:

- Merchant normalization
- Merchant category lookup
- Merchant billing frequency lookup

Author:
Subscription Intelligence Team

Version:
1.0
"""

from pathlib import Path
import pandas as pd

# -------------------------------------------------------
# Locate merchant database
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CSV_FILE = DATA_DIR / "merchant_database.csv"


# -------------------------------------------------------
# Load merchant database
# -------------------------------------------------------

try:
    merchant_db = pd.read_csv(CSV_FILE)

    # Replace missing values with empty strings
    merchant_db = merchant_db.fillna("")

except FileNotFoundError:
    raise FileNotFoundError(
        f"\nMerchant database not found:\n{CSV_FILE}\n"
        "Please create data/merchant_database.csv"
    )


# -------------------------------------------------------
# Build lookup dictionaries
# -------------------------------------------------------

merchant_lookup = {}
category_lookup = {}
frequency_lookup = {}

for _, row in merchant_db.iterrows():

    merchant = str(row["Merchant"]).strip().upper()
    category = str(row["Category"]).strip()
    frequency = str(row["Frequency"]).strip()

    category_lookup[merchant] = category
    frequency_lookup[merchant] = frequency

    aliases = str(row["Aliases"]).split(";")

    # Register official merchant name
    merchant_lookup[merchant] = merchant

    # Register aliases
    for alias in aliases:
        alias = alias.strip().upper()

        if alias:
            merchant_lookup[alias] = merchant


# -------------------------------------------------------
# Public Functions
# -------------------------------------------------------

def normalize(description):
    """
    Normalize a transaction description to
    a standard merchant name.
    """

    if pd.isna(description):
        return "OTHER"

    text = str(description).upper()

    for alias, merchant in merchant_lookup.items():

        if alias in text:
            return merchant

    return "OTHER"


def merchant_category(merchant):
    """
    Return merchant category.
    """

    merchant = str(merchant).upper()

    return category_lookup.get(merchant, "Unknown")


def merchant_frequency(merchant):
    """
    Return expected billing frequency.
    """

    merchant = str(merchant).upper()

    return frequency_lookup.get(merchant, "Unknown")


def merchant_exists(merchant):
    """
    Check whether merchant exists.
    """

    merchant = str(merchant).upper()

    return merchant in category_lookup


def merchant_count():
    """
    Return number of merchants loaded.
    """

    return len(category_lookup)


def all_merchants():
    """
    Return list of all merchants.
    """

    return sorted(category_lookup.keys())


# -------------------------------------------------------
# Self Test
# -------------------------------------------------------

if __name__ == "__main__":

    print("=" * 50)
    print("Merchant Intelligence Test")
    print("=" * 50)

    print(f"Merchants loaded : {merchant_count()}")

    samples = [
        "NETFLIX.COM",
        "SPOTIFY USA",
        "APPLE.COM/BILL",
        "GOOGLE*YOUTUBE",
        "AMZN PRIME",
        "OPENAI",
        "CANVA",
        "UNKNOWN STORE"
    ]

    print()

    for sample in samples:

        merchant = normalize(sample)

        print(f"Transaction : {sample}")
        print(f"Merchant    : {merchant}")
        print(f"Category    : {merchant_category(merchant)}")
        print(f"Frequency   : {merchant_frequency(merchant)}")
        print("-" * 50)