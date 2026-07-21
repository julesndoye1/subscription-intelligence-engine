"""
Application-wide constants for the Subscription Intelligence Engine.

This module centralizes all configuration values used across the project.
Changing business rules here automatically affects the rest of the system.
"""

from typing import List

# ==============================================================================
# REQUIRED EXCEL COLUMNS
# ==============================================================================

REQUIRED_COLUMNS: List[str] = [
    "Name",
    "Phone",
    "Account ID",
    "Amount",
    "Transaction Fee",
    "Total Amount",
    "Balance",
    "Transaction For",
    "Transaction ID",
    "Status",
    "Transaction Date",
]

# ==============================================================================
# SUPPORTED TRANSACTION STATUSES
# ==============================================================================

# These statuses are still useful for subscription detection because
# they indicate a recurring billing attempt.

VALID_TRANSACTION_STATUSES = {
    "SUCCESS",
    "SUCCESSFUL",
    "APPROVED",
    "DECLINED",
    "DECLINED - INSUFFICIENT FUNDS",
    "INSUFFICIENT FUNDS",
    "DO NOT HONOUR",
    "DO NOT HONOR",
    "EXPIRED CARD",
    "CARD EXPIRED",
    "CARD BLOCKED",
    "LIMIT EXCEEDED",
}

# ==============================================================================
# TRANSACTIONS TO IGNORE
# ==============================================================================

IGNORE_PATTERNS = [
    "Funds Transfer",
    "Wallet Transfer",
    "Transfer to Wallet",
    "Wallet to Card",
    "Card to Wallet",
    "Cash Withdrawal",
    "ATM Withdrawal",
    "Balance Inquiry",
    "PIN Change",
    "Card Creation",
    "Card Activation",
    "Card Fee",
    "Card Replacement",
    "Reversal",
    "Refund",
    "Chargeback",
    "Adjustment",
    "Manual Credit",
    "Manual Debit",
    "POS Reversal",
    "Invalid Reversal",
]

# ==============================================================================
# SUBSCRIPTION INTERVALS (Days)
# ==============================================================================

MONTHLY_MIN_DAYS = 28
MONTHLY_MAX_DAYS = 33

WEEKLY_MIN_DAYS = 6
WEEKLY_MAX_DAYS = 8

BIWEEKLY_MIN_DAYS = 13
BIWEEKLY_MAX_DAYS = 15

QUARTERLY_MIN_DAYS = 85
QUARTERLY_MAX_DAYS = 95

YEARLY_MIN_DAYS = 360
YEARLY_MAX_DAYS = 370

# ==============================================================================
# SUPPORTED FREQUENCIES
# ==============================================================================

MONTHLY = "Monthly"
WEEKLY = "Weekly"
BIWEEKLY = "Biweekly"
QUARTERLY = "Quarterly"
YEARLY = "Yearly"
UNKNOWN = "Unknown"

# ==============================================================================
# CONFIDENCE SCORING WEIGHTS
# ==============================================================================

CONFIDENCE_WEIGHTS = {
    "occurrences": 40,
    "regularity": 25,
    "merchant": 15,
    "amount": 10,
    "success": 10,
}

MAX_CONFIDENCE_SCORE = 100

# ==============================================================================
# MINIMUM DETECTION REQUIREMENTS
# ==============================================================================

MIN_OCCURRENCES = 2

MAX_AMOUNT_VARIATION_PERCENT = 25

# ==============================================================================
# MERCHANT CATEGORIES
# ==============================================================================

MERCHANT_CATEGORIES = [
    "Video Streaming",
    "Music Streaming",
    "Cloud Storage",
    "Gaming",
    "AI",
    "Software",
    "Productivity",
    "Shopping",
    "Telecommunications",
    "Insurance",
    "Education",
    "Fitness",
    "Finance",
    "Transport",
    "Utilities",
    "News",
    "Other",
]

# ==============================================================================
# OUTPUT DATAFRAME SCHEMAS
# ==============================================================================

SUBSCRIPTION_COLUMNS = [
    "Account ID",
    "Customer",
    "Merchant",
    "Category",
    "Frequency",
    "Occurrences",
    "Average Amount",
    "Last Amount",
    "First Charge",
    "Last Charge",
    "Average Interval",
    "Confidence",
]

PREDICTION_COLUMNS = [
    "Account ID",
    "Customer",
    "Merchant",
    "Category",
    "Predicted Renewal",
    "Expected Amount",
    "Confidence",
    "Days Remaining",
]

ALERT_COLUMNS = [
    "Account ID",
    "Customer",
    "Merchant",
    "Alert Type",
    "Priority",
    "Message",
    "Renewal Date",
]

# ==============================================================================
# STREAMLIT DASHBOARD COLORS
# ==============================================================================

SUCCESS_COLOR = "#16A34A"
WARNING_COLOR = "#F59E0B"
ERROR_COLOR = "#DC2626"
INFO_COLOR = "#2563EB"

# ==============================================================================
# DATE FORMATS
# ==============================================================================

DEFAULT_DATE_FORMAT = "%Y-%m-%d"

DISPLAY_DATE_FORMAT = "%d-%b-%Y"

# ==============================================================================
# LOGGING
# ==============================================================================

LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

LOG_LEVEL = "INFO"

# ==============================================================================
# APPLICATION SETTINGS
# ==============================================================================

APPLICATION_NAME = "Subscription Intelligence Engine"

APPLICATION_VERSION = "2.0"

DEFAULT_CONFIDENCE_THRESHOLD = 60

DEFAULT_LOOKBACK_MONTHS = 18

# ==============================================================================
# COMMON MERCHANT KEYWORDS
# ==============================================================================

KNOWN_SUBSCRIPTION_KEYWORDS = [
    "NETFLIX",
    "SPOTIFY",
    "APPLE",
    "ITUNES",
    "APPLE.COM",
    "GOOGLE",
    "GOOGLE ONE",
    "GOOGLE PLAY",
    "YOUTUBE",
    "AMAZON PRIME",
    "AMAZON",
    "PRIME VIDEO",
    "DISNEY",
    "DISNEY+",
    "HULU",
    "MAX",
    "HBO",
    "CRUNCHYROLL",
    "CHATGPT",
    "OPENAI",
    "CLAUDE",
    "ANTHROPIC",
    "MICROSOFT",
    "MICROSOFT 365",
    "ADOBE",
    "CANVA",
    "DROPBOX",
    "ICLOUD",
    "ONEDRIVE",
    "TIKTOK",
    "PAYPAL",
]