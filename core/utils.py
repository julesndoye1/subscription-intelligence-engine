"""
Common utility functions for the Subscription Intelligence Engine.

These helpers are intentionally generic and reusable across
all modules.

Used by:

- loader.py
- merchant.py
- classifier.py
- detector.py
- predictor.py
- dashboard.py
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Iterable

import pandas as pd

from core.constants import LOG_FORMAT
from core.constants import LOG_LEVEL


# ==============================================================================
# LOGGING
# ==============================================================================

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
)

logger = logging.getLogger("subscription-engine")


# ==============================================================================
# STRING HELPERS
# ==============================================================================

def normalize_text(text: str) -> str:
    """
    Normalize merchant text.

    Example

    "Netflix.com Los Gatos NL"

    becomes

    "NETFLIX COM LOS GATOS NL"
    """

    if pd.isna(text):
        return ""

    text = str(text).upper()

    text = re.sub(r"[^A-Z0-9 ]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def remove_extra_spaces(text: str) -> str:
    """
    Collapse repeated spaces.
    """

    if not text:
        return ""

    return " ".join(str(text).split())


# ==============================================================================
# NUMBER HELPERS
# ==============================================================================

def safe_float(value) -> float:
    """
    Convert any value to float safely.

    Returns 0.0 if conversion fails.
    """

    try:

        if pd.isna(value):
            return 0.0

        if isinstance(value, str):

            value = (
                value.replace(",", "")
                .replace("FCFA", "")
                .replace("XOF", "")
                .strip()
            )

        return float(value)

    except Exception:

        return 0.0


def percent_difference(a: float, b: float) -> float:
    """
    Percentage difference between two values.
    """

    if a == 0 and b == 0:
        return 0.0

    denominator = (abs(a) + abs(b)) / 2

    if denominator == 0:
        return 0.0

    return abs(a - b) / denominator * 100


# ==============================================================================
# DATE HELPERS
# ==============================================================================

def to_datetime(series: pd.Series) -> pd.Series:
    """
    Convert pandas Series to datetime.
    """

    return pd.to_datetime(
        series,
        errors="coerce",
        dayfirst=True,
    )


def days_between(date1, date2) -> int:
    """
    Returns the number of days between two dates.
    """

    if pd.isna(date1) or pd.isna(date2):
        return 0

    return abs((date2 - date1).days)


def average_interval(dates: Iterable[datetime]) -> float:
    """
    Calculate average interval between dates.

    Returns

    0

    if fewer than 2 dates exist.
    """

    dates = sorted(pd.to_datetime(list(dates)))

    if len(dates) < 2:
        return 0

    intervals = []

    for i in range(1, len(dates)):

        intervals.append((dates[i] - dates[i - 1]).days)

    return round(sum(intervals) / len(intervals), 2)


# ==============================================================================
# DATAFRAME HELPERS
# ==============================================================================

def empty_dataframe(columns: list[str]) -> pd.DataFrame:
    """
    Returns an empty dataframe with the required schema.
    """

    return pd.DataFrame(columns=columns)


def sort_transactions(data: pd.DataFrame) -> pd.DataFrame:
    """
    Sort transactions chronologically.
    """

    return data.sort_values(
        by="Transaction Date"
    ).reset_index(drop=True)


def copy_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a defensive copy.
    """

    return df.copy(deep=True)


# ==============================================================================
# STATISTICS
# ==============================================================================

def coefficient_of_variation(values: list[float]) -> float:
    """
    Calculates coefficient of variation.

    Lower value means more stable subscription amount.
    """

    if len(values) < 2:
        return 0

    s = pd.Series(values)

    mean = s.mean()

    if mean == 0:
        return 0

    return float((s.std() / mean) * 100)


# ==============================================================================
# MERCHANT HELPERS
# ==============================================================================

def contains_any(text: str, patterns: list[str]) -> bool:
    """
    Returns True if any pattern exists inside text.
    """

    text = normalize_text(text)

    for pattern in patterns:

        if normalize_text(pattern) in text:

            return True

    return False


def clean_transaction_description(text: str) -> str:
    """
    Remove noisy information from card descriptions.

    Example

    NETFLIX.COM 4087249160 NL

    becomes

    NETFLIX COM NL
    """

    text = normalize_text(text)

    text = re.sub(r"\b\d{6,20}\b", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ==============================================================================
# VALIDATION
# ==============================================================================

def require_columns(
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> None:
    """
    Raise an exception if required columns are missing.
    """

    missing = [
        c
        for c in required_columns
        if c not in dataframe.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {', '.join(missing)}"
        )


# ==============================================================================
# DISPLAY
# ==============================================================================

def currency(amount: float) -> str:
    """
    Format XOF values.

    Example

    12500

    becomes

    12,500 XOF
    """

    return f"{safe_float(amount):,.0f} XOF"


def percentage(value: float) -> str:
    """
    Format percentage.

    Example

    87.56

    becomes

    87.6%
    """

    return f"{value:.1f}%"


# ==============================================================================
# DEBUGGING
# ==============================================================================

def log_dataframe(df: pd.DataFrame, title: str = "DataFrame") -> None:
    """
    Log useful dataframe information.
    """

    logger.info("-" * 60)
    logger.info(title)
    logger.info("Rows : %s", len(df))
    logger.info("Cols : %s", len(df.columns))
    logger.info("Columns : %s", list(df.columns))
    logger.info("-" * 60)