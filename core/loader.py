"""
loader.py

Loads and validates transaction files for the Subscription
Intelligence Engine.

Responsibilities
----------------
1. Read Excel files
2. Validate required columns
3. Standardize column names
4. Parse dates
5. Convert numeric fields
6. Preserve Phone and Account ID as text
7. Remove duplicate transactions
8. Clean transaction descriptions
9. Return a clean DataFrame

This module deliberately DOES NOT perform:

- Merchant detection
- Subscription detection
- Renewal prediction

Those belong to later pipeline stages.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.constants import REQUIRED_COLUMNS
from core.utils import (
    clean_transaction_description,
    copy_dataframe,
    logger,
    require_columns,
    safe_float,
    sort_transactions,
    to_datetime,
)


class TransactionLoader:
    """
    Reads and prepares transaction files.
    """

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def load(self, file_path: str | Path) -> pd.DataFrame:
        """
        Load an Excel transaction report.
        """

        logger.info("Loading transaction file...")

        # Read everything exactly as stored in Excel
        df = pd.read_excel(file_path)

        df = self.prepare(df)

        logger.info(
            "Loaded %s transactions",
            len(df),
        )

        return df

    def prepare(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate an existing dataframe.
        """

        df = copy_dataframe(dataframe)

        df = self._normalize_columns(df)

        require_columns(df, REQUIRED_COLUMNS)

        df = self._format_identifiers(df)

        df = self._convert_dates(df)

        df = self._convert_numbers(df)

        df = self._clean_descriptions(df)

        df = self._remove_duplicates(df)

        df = sort_transactions(df)

        return df

    # ------------------------------------------------------------------
    # Private
    # ------------------------------------------------------------------

    def _normalize_columns(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Remove leading/trailing spaces from column names.
        """

        df.columns = [str(c).strip() for c in df.columns]

        return df

    def _format_identifiers(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Keep Phone and Account ID as clean text values.

        Examples

        221771234567.0 -> 221771234567
        25350054.0     -> 25350054
        """

        identifier_columns = [
            "Phone",
            "Account ID",
        ]

        for column in identifier_columns:

            if column not in df.columns:
                continue

            df[column] = (
                df[column]
                .fillna("")
                .astype(str)
                .str.replace(".0", "", regex=False)
                .str.strip()
            )

        return df

    def _convert_dates(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert Transaction Date into datetime.
        """

        logger.info("Converting dates...")

        df["Transaction Date"] = to_datetime(
            df["Transaction Date"]
        )

        return df

    def _convert_numbers(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Convert monetary columns to float.
        """

        logger.info("Converting numeric columns...")

        numeric_columns = [
            "Amount",
            "Transaction Fee",
            "Total Amount",
            "Balance",
        ]

        for column in numeric_columns:

            if column not in df.columns:
                continue

            df[column] = df[column].apply(safe_float)

        return df

    def _clean_descriptions(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Clean transaction descriptions.
        """

        logger.info("Cleaning descriptions...")

        df["Transaction For"] = (
            df["Transaction For"]
            .fillna("")
            .astype(str)
            .apply(clean_transaction_description)
        )

        return df

    def _remove_duplicates(
        self,
        df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Remove duplicate transactions based on Transaction ID.
        """

        logger.info("Removing duplicate transactions...")

        if "Transaction ID" not in df.columns:
            return df

        before = len(df)

        df = df.drop_duplicates(
            subset=["Transaction ID"],
            keep="first",
        ).reset_index(drop=True)

        removed = before - len(df)

        logger.info(
            "Removed %s duplicate transactions",
            removed,
        )

        return df