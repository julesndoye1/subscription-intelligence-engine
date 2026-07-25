"""
Merchant Name Normalizer
------------------------

Normalizes raw merchant descriptions into consistent merchant names.

Example:
    NETFLIX.COM        -> Netflix
    NETFLIX*1234       -> Netflix
    APPLE.COM/BILL     -> Apple
    GOOGLE*YouTube     -> Google
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path

import pandas as pd


class MerchantNormalizer:
    """
    Normalize merchant names using a configurable alias database.
    """

    def __init__(self, alias_file=None):
        self.aliases = {}

        if alias_file is None:
            alias_file = (
                Path(__file__).resolve().parent.parent
                / "data"
                / "merchant_aliases.csv"
            )

        if Path(alias_file).exists():
            df = pd.read_csv(alias_file)

            required = {"Alias", "Merchant"}

            if required.issubset(df.columns):
                for _, row in df.iterrows():
                    alias = str(row["Alias"]).strip().upper()
                    merchant = str(row["Merchant"]).strip()

                    if alias:
                        self.aliases[alias] = merchant

    # -------------------------------------------------------------

    @staticmethod
    def _clean(text: str) -> str:
        """
        Basic merchant text cleanup.
        """

        if not isinstance(text, str):
            return ""

        text = unicodedata.normalize("NFKD", text)

        text = text.upper()

        text = re.sub(r"\d+", " ", text)

        text = re.sub(r"[^A-Z ]", " ", text)

        text = re.sub(r"\s+", " ", text)

        return text.strip()

    # -------------------------------------------------------------

    def normalize(self, merchant_name: str) -> str:
        """
        Return canonical merchant name.
        """

        cleaned = self._clean(merchant_name)

        if cleaned in self.aliases:
            return self.aliases[cleaned]

        for alias, merchant in self.aliases.items():
            if alias in cleaned:
                return merchant

        return cleaned.title()

    # -------------------------------------------------------------

    def tokenize(self, merchant_name: str):
        """
        Return normalized tokens.
        """

        cleaned = self._clean(merchant_name)

        return cleaned.split()

    # -------------------------------------------------------------

    def extract(self, merchant_name: str):
        """
        Return useful normalization information.
        """

        return {
            "raw": merchant_name,
            "normalized": self.normalize(merchant_name),
            "tokens": self.tokenize(merchant_name),
        }