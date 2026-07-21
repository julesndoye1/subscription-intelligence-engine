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
6. Remove duplicate transactions
7. Clean transaction descriptions
8. Return a clean DataFrame

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

    Example
    -------

    loader = TransactionLoader()

    df = loader.load("transactions.xlsx")
    """

    def __init__(self):

        pass

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def load(self, file_path: str | Path) -> pd.DataFrame:
        """
        Load an Excel transaction report.

        Parameters
        ----------
        file_path

            Excel file

        Returns
        -------
        pandas.DataFrame
        """

        logger.info("Loading transaction file...")

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

        This method is useful for unit tests or
        Streamlit uploads where the dataframe is
        already in memory.
        """

        df = copy_dataframe(dataframe)

        df = self._normalize_columns(df)

        require_columns(df, REQUIRED_COLUMNS)

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
        Remove duplicate transactions.

        Transaction ID is considered authoritative.

        If it does not exist,
        use a fallback combination.
        """

        before = len(df)

        if "Transaction ID" in df.columns:

            df = df.drop_duplicates(
                subset=["Transaction ID"]
            )

        else:

            df = df.drop_duplicates(
                subset=[
                    "Account ID",
                    "Transaction Date",
                    "Amount",
                    "Transaction For",
                ]
            )

        removed = before - len(df)

        if removed > 0:

            logger.info(
                "Removed %s duplicate transactions",
                removed,
            )

        return df.reset_index(drop=True)


# ----------------------------------------------------------------------
# Convenience Function
# ----------------------------------------------------------------------

def load_transactions(file_path: str | Path) -> pd.DataFrame:
    """
    Convenience wrapper.

    Example
    -------

    df = load_transactions("transactions.xlsx")
    """

    loader = TransactionLoader()

    return loader.load(file_path)