"""
core/merchant_registry.py

Version 1

Merchant Registry for the Subscription Intelligence Engine.

The whitelist is the ONLY source of truth.

If a merchant is found in subscription_whitelist.csv,
it is considered a subscription merchant.

All other merchants are treated as non-subscription merchants.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import re

import pandas as pd


# ==========================================================
# Merchant Model
# ==========================================================

@dataclass
class Merchant:

    name: str

    category: str = "Unknown"

    frequency: str = "Unknown"

    country: str = "Unknown"

    risk: str = "Unknown"


# ==========================================================
# Merchant Registry
# ==========================================================

class MerchantRegistry:

    def __init__(self, data_dir: Optional[str] = None):

        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = (
                Path(__file__).resolve().parent.parent / "data"
            )

        self.merchants = {}

        self._load_whitelist()

    # ------------------------------------------------------

    @staticmethod
    def normalize(text: str) -> str:
        """
        Normalize merchant names.
        """

        if text is None:
            return ""

        text = str(text).upper()

        # Remove long numbers
        text = re.sub(r"\d{6,}", " ", text)

        # Replace separators
        text = re.sub(r"[*_/.,\\-]", " ", text)

        # Remove duplicate spaces
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # ------------------------------------------------------

    def _load_whitelist(self):

        file = self.data_dir / "subscription_whitelist.csv"

        if not file.exists():

            raise FileNotFoundError(
                f"Cannot find {file}"
            )

        df = pd.read_csv(file).fillna("")

        for _, row in df.iterrows():

            merchant = Merchant(

                name=row["Merchant"],

                category=row.get(
                    "Category",
                    "Unknown",
                ),

                frequency=row.get(
                    "Frequency",
                    "Unknown",
                ),

                country=row.get(
                    "Country",
                    "Unknown",
                ),

                risk=row.get(
                    "Risk",
                    "Unknown",
                ),

            )

            key = self.normalize(
                merchant.name
            )

            self.merchants[key] = merchant
        

    # ------------------------------------------------------

    def find(
        self,
        merchant_name: str,
    ) -> Optional[Merchant]:
        """
        Returns the merchant if it exists
        in the whitelist.

        Otherwise returns None.
        """

        normalized = self.normalize(
            merchant_name
        )

        # Exact match

        if normalized in self.merchants:
            return self.merchants[normalized]

        # Partial match

        for key, merchant in self.merchants.items():

            if key in normalized:
                return merchant

        return None

    # ------------------------------------------------------

    def is_subscription(
        self,
        merchant_name: str,
    ) -> bool:

        return self.find(
            merchant_name
        ) is not None