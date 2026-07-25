"""
Merchant Knowledge Base
-----------------------

Provides merchant lookup services for the Subscription
Intelligence Engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Merchant:

    name: str
    category: str
    frequency: str
    country: str
    risk: str


class MerchantDatabase:

    def __init__(self, database_file=None):

        if database_file is None:
            database_file = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "merchant_database.csv"
            )

        self.database = {}

        if Path(database_file).exists():

            df = pd.read_csv(database_file)

            required = {
                "Merchant",
                "Category",
                "Frequency",
                "Country",
                "Risk",
            }

            if required.issubset(df.columns):

                for _, row in df.iterrows():

                    merchant = Merchant(
                        name=row["Merchant"],
                        category=row["Category"],
                        frequency=row["Frequency"],
                        country=row["Country"],
                        risk=row["Risk"],
                    )

                    self.database[merchant.name.lower()] = merchant

    # -------------------------------------------------------------

    def exists(self, merchant_name):

        return merchant_name.lower() in self.database

    # -------------------------------------------------------------

    def get(self, merchant_name):

        return self.database.get(merchant_name.lower())

    # -------------------------------------------------------------

    def category(self, merchant_name):

        merchant = self.get(merchant_name)

        return merchant.category if merchant else "Unknown"

    # -------------------------------------------------------------

    def frequency(self, merchant_name):

        merchant = self.get(merchant_name)

        return merchant.frequency if merchant else "Unknown"

    # -------------------------------------------------------------

    def risk(self, merchant_name):

        merchant = self.get(merchant_name)

        return merchant.risk if merchant else "Unknown"

    # -------------------------------------------------------------

    def all_merchants(self):

        return list(self.database.keys())