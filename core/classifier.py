"""
classifier.py

Merchant classification engine for the Subscription Intelligence Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List

from core.merchant import MerchantDatabase
from core.utils import clean_transaction_description
from core.constants import KNOWN_SUBSCRIPTION_KEYWORDS


class SubscriptionType(str, Enum):
    CONFIRMED = "Confirmed"
    LIKELY = "Likely"
    UNKNOWN = "Unknown"


@dataclass
class ClassificationResult:
    merchant: str
    category: str
    frequency: str
    subscription_type: SubscriptionType
    confidence: int
    matched_alias: str = ""
    reasons: List[str] = field(default_factory=list)


class SubscriptionClassifier:
    """
    Classifies a transaction into a subscription candidate.
    """

    def __init__(self):
        self.db = MerchantDatabase()

    def classify(self, description: str) -> ClassificationResult:
        text = clean_transaction_description(description)

        match = self.db.find(text)

        if match:
            confidence = 90 if getattr(match, "aliases", None) else 80
            return ClassificationResult(
                merchant=match.name,
                category=match.category,
                frequency=match.frequency,
                subscription_type=SubscriptionType.CONFIRMED,
                confidence=confidence,
                matched_alias=text,
                reasons=["Matched merchant database"],
            )

        upper = text.upper()
        for keyword in KNOWN_SUBSCRIPTION_KEYWORDS:
            if keyword in upper:
                return ClassificationResult(
                    merchant=keyword,
                    category="Other",
                    frequency="Unknown",
                    subscription_type=SubscriptionType.LIKELY,
                    confidence=65,
                    matched_alias=keyword,
                    reasons=["Matched subscription keyword"],
                )

        return ClassificationResult(
            merchant="UNKNOWN",
            category="Other",
            frequency="Unknown",
            subscription_type=SubscriptionType.UNKNOWN,
            confidence=0,
            reasons=["No merchant match"],
        )

    def classify_transaction(self, transaction: dict) -> ClassificationResult:
        return self.classify(transaction.get("Transaction For", ""))


default_classifier = SubscriptionClassifier()
