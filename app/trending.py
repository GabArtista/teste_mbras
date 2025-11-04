"""Trending topic calculation."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, Iterable, List

from .utils import log_decay_factor


@dataclass
class TrendingAccumulator:
    total_weight: float = 0.0
    frequency: int = 0
    sentiment_weight: float = 0.0


def compute_trending_topics(
    hashtag_records: Iterable[tuple[str, float, float]],
    limit: int = 5,
) -> List[str]:
    """
    Compute trending topics.

    Args:
        hashtag_records: iterable of tuples (hashtag, temporal_weight, sentiment_multiplier).
    """
    accumulators: Dict[str, TrendingAccumulator] = defaultdict(TrendingAccumulator)

    for hashtag, temporal_weight, sentiment_multiplier in hashtag_records:
        normalized = hashtag.lower()
        factor = log_decay_factor(len(normalized))
        weight = temporal_weight * sentiment_multiplier * factor
        acc = accumulators[normalized]
        acc.total_weight += weight
        acc.frequency += 1
        acc.sentiment_weight += sentiment_multiplier

    sorted_items = sorted(
        accumulators.items(),
        key=lambda item: (
            -item[1].total_weight,
            -item[1].frequency,
            -item[1].sentiment_weight,
            item[0],
        ),
    )

    results = [item[0] for item in sorted_items[:limit]]
    return results
