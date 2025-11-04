"""Utility helpers for text normalization and time calculations."""

from __future__ import annotations

import math
import unicodedata
import re
from datetime import datetime, timezone
from typing import List

TOKEN_REGEX = re.compile(r"(?:#\w+(?:-\w+)*)|\b\w+\b", re.UNICODE)


def normalize_token(token: str) -> str:
    """Normalize token for lexicon matching."""
    lowered = token.lower()
    decomposed = unicodedata.normalize("NFKD", lowered)
    stripped = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return stripped


def tokenize(text: str) -> List[str]:
    """Tokenize text using deterministic regex."""
    return TOKEN_REGEX.findall(text)


def ensure_utc(dt: datetime) -> datetime:
    """Return datetime with UTC tzinfo."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def log_decay_factor(length: int) -> float:
    """Return logarithmic decay factor for hashtags longer than 8 characters."""
    if length <= 8:
        return 1.0
    numerator = math.log10(8)
    denominator = math.log10(length)
    if denominator == 0:
        return 1.0
    return numerator / denominator


def accent_insensitive_contains(text: str, fragment: str) -> bool:
    """Check if fragment appears in text ignoring accent/case."""
    normalized_text = normalize_token(text)
    normalized_fragment = normalize_token(fragment)
    return normalized_fragment in normalized_text


def next_prime(n: int) -> int:
    """Return the next prime number greater than or equal to n."""

    def is_prime(x: int) -> bool:
        if x <= 1:
            return False
        if x <= 3:
            return True
        if x % 2 == 0 or x % 3 == 0:
            return False
        i = 5
        while i * i <= x:
            if x % i == 0 or x % (i + 2) == 0:
                return False
            i += 6
        return True

    candidate = max(2, n)
    while not is_prime(candidate):
        candidate += 1
    return candidate


def fibonacci(n: int) -> int:
    """Return the nth Fibonacci number (1-indexed)."""
    if n <= 0:
        raise ValueError("n must be positive for Fibonacci sequence")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
