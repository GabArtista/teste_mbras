"""Influence and engagement calculations."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List

from .constants import GOLDEN_RATIO
from .utils import fibonacci, next_prime


@dataclass
class UserStats:
    user_id: str
    total_reactions: int = 0
    total_shares: int = 0
    total_views: int = 0
    messages: int = 0

    def register(self, reactions: int, shares: int, views: int) -> None:
        self.total_reactions += reactions
        self.total_shares += shares
        self.total_views += views
        self.messages += 1

    @property
    def interactions(self) -> int:
        return self.total_reactions + self.total_shares

    @property
    def engagement_rate(self) -> float:
        if self.total_views <= 0:
            return 0.0
        base_rate = self.interactions / self.total_views
        if self.interactions > 0 and self.interactions % 7 == 0:
            base_rate *= 1 + (1 / GOLDEN_RATIO)
        return base_rate


def _base_followers(user_id: str) -> int:
    digest = hashlib.sha256(user_id.encode("utf-8")).hexdigest()
    return (int(digest, 16) % 10000) + 100


def _has_non_ascii(text: str) -> bool:
    return any(ord(ch) > 127 for ch in text)


def compute_followers(user_id: str) -> int:
    """Compute followers applying special rules."""
    if _has_non_ascii(user_id):
        return 4242

    if len(user_id) == 13:
        return fibonacci(13)

    if user_id.lower().endswith("_prime"):
        base = _base_followers(user_id)
        return next_prime(base)

    return _base_followers(user_id)


def build_influence_ranking(
    user_stats: Dict[str, UserStats],
) -> List[Dict[str, float]]:
    """Build influence ranking for users."""
    ranking: List[Dict[str, float]] = []
    for user_id, stats in user_stats.items():
        followers = compute_followers(user_id)
        engagement = stats.engagement_rate
        influence = (followers * 0.4) + (engagement * 0.6)

        if user_id.lower().endswith("007"):
            influence *= 0.5

        if "mbras" in user_id.lower():
            influence += 2.0

        ranking.append(
            {
                "user_id": user_id,
                "followers": followers,
                "engagement_rate": round(engagement, 6),
                "influence_score": round(influence, 6),
            }
        )

    ranking.sort(key=lambda entry: (-entry["influence_score"], entry["user_id"]))
    return ranking
