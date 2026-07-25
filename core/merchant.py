"""
merchant.py
===========

Merchant Knowledge Base

Responsibilities
----------------
1. Load the merchant database.
2. Normalize transaction descriptions.
3. Match merchants using aliases.
4. Return standardized Merchant objects.

Author: Jules N
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


# ==========================================================
# Merchant Model
# ==========================================================

@dataclass(frozen=True)
class Merchant:
    """
    Standard merchant returned by the MerchantDatabase.
    """

    name: str
    category: str
    frequency: str
    aliases: List[str]

    @property
    def expected_interval_days(self) -> int:
        """
        Convert billing frequency into expected billing interval.
        """

        mapping = {
            "DAILY": 1,
            "WEEKLY": 7,
            "MONTHLY": 30,
            "QUARTERLY": 90,
            "YEARLY": 365,
        }

        return mapping.get(self.frequency.upper(), 30)



@dataclass(frozen=True)
class MatchResult:
    merchant: Merchant
    matched_alias: str
    score: int

# ==========================================================
# Merchant Database
# ==========================================================

class MerchantDatabase:
    """
    Merchant lookup engine.

    Loads merchant_database.csv and provides merchant matching.
    """

    REQUIRED_COLUMNS = [
        "Merchant",
        "Category",
        "Frequency",
        "Aliases",
    ]

    def __init__(self, csv_path: Optional[str] = None):

        if csv_path is None:

            project_root = Path(__file__).resolve().parent.parent

            csv_path = (
                project_root
                / "data"
                / "merchant_database.csv"
            )

        self.csv_path = Path(csv_path)

        self._merchant_index: Dict[str, Merchant] = {}
        self._alias_index: Dict[str, Merchant] = {}

        self._loaded = False

        self.load()

    # ------------------------------------------------------

    def load(self) -> None:
        """
        Load merchant database into memory.
        """

        if not self.csv_path.exists():
            raise FileNotFoundError(
                f"Merchant database not found: {self.csv_path}"
            )

        df = pd.read_csv(self.csv_path)

        missing = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in df.columns
        ]

        if missing:
            raise ValueError(
                f"Missing required columns: {missing}"
            )

        self._merchant_index.clear()
        self._alias_index.clear()

        for _, row in df.iterrows():

            merchant = Merchant(
                name=str(row["Merchant"]).strip(),
                category=str(row["Category"]).strip(),
                frequency=str(row["Frequency"]).strip(),
                aliases=self._split_aliases(
                    row["Aliases"]
                ),
            )

            self._merchant_index[
                merchant.name.upper()
            ] = merchant

            for alias in merchant.aliases:
                self._alias_index[
                    alias.upper()
                ] = merchant

        self._loaded = True

        logger.info(
            "Loaded %s merchants.",
            len(self._merchant_index),
        )

    # ------------------------------------------------------

    @staticmethod
    def _split_aliases(value) -> List[str]:
        """
        Convert aliases into a list.

        Supports both comma and semicolon separators.
        """

        if pd.isna(value):
            return []

        text = str(value)

        text = text.replace(";", ",")

        aliases = []

        for alias in text.split(","):

            alias = alias.strip()

            if alias:
                aliases.append(alias)

        return aliases

    # ------------------------------------------------------

    @staticmethod
    def normalize(text: str) -> str:
        """Normalize Visa transaction descriptions."""
        if not text:
            return ""
        text = str(text).upper()
        for ch in ("*", "/", "\\\\", "-", "_", "."):
            text = text.replace(ch, " ")
        text = re.sub(r"[^A-Z0-9 ]", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ------------------------------------------------------

    def find(self, description: str) -> Merchant:
        """Return the best merchant match using longest-alias scoring."""
        normalized = self.normalize(description)
        if not normalized:
            return self._unknown_merchant()
        best=None
        best_score=-1
        for alias, merchant in self._alias_index.items():
            a=self.normalize(alias)
            score = 1000 + len(a) if a == normalized else (len(a) if a in normalized else -1)
            if score > best_score:
                best_score = score
                best = merchant
        if best:
            return best
        for name, merchant in self._merchant_index.items():
            if self.normalize(name) in normalized:
                return merchant
        return self._unknown_merchant()

        #
        # Exact merchant
        #

        merchant = self._merchant_index.get(normalized)

        if merchant:
            return merchant

        #
        # Exact alias
        #

        merchant = self._alias_index.get(normalized)

        if merchant:
            return merchant

        #
        # Alias contained in transaction
        #

        for alias, merchant in self._alias_index.items():

            if alias in normalized:
                return merchant

        #
        # Merchant contained in transaction
        #

        for merchant_name, merchant in self._merchant_index.items():

            if merchant_name in normalized:
                return merchant

        return self._unknown_merchant()

    # ------------------------------------------------------

    @staticmethod
    def _unknown_merchant() -> Merchant:
        """
        Return an unknown merchant.
        """

        return Merchant(
            name="OTHER",
            category="Unknown",
            frequency="Unknown",
            aliases=[],
        )