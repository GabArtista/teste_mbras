"""Anomaly detection for message feeds."""

from __future__ import annotations

from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Deque, Dict, Iterable, List, Tuple


def detect_burst(messages_by_user: Dict[str, List[datetime]], threshold: int = 10) -> bool:
    """Detect bursts where a user posts more than threshold messages within five minutes."""
    window = timedelta(minutes=5)
    for timestamps in messages_by_user.values():
        timestamps.sort()
        left = 0
        for right, ts in enumerate(timestamps):
            while ts - timestamps[left] > window:
                left += 1
            if right - left + 1 > threshold:
                return True
    return False


def detect_alternating_pattern(
    sentiments_by_user: Dict[str, List[str]],
    required_length: int = 10,
) -> bool:
    """Detect alternating positive/negative pattern with required length."""
    for sentiments in sentiments_by_user.values():
        filtered = [label for label in sentiments if label in {"positive", "negative"}]
        if len(filtered) < required_length:
            continue
        max_sequence = 1
        current_sequence = 1
        for previous, current in zip(filtered, filtered[1:]):
            if previous != current:
                current_sequence += 1
                max_sequence = max(max_sequence, current_sequence)
            else:
                current_sequence = 1
        if max_sequence >= required_length:
            return True
    return False


def detect_synchronized_posting(timestamps: List[datetime]) -> bool:
    """Detect at least three messages inside ±2 seconds."""
    if len(timestamps) < 3:
        return False
    timestamps.sort()
    window_size = timedelta(seconds=4)
    left = 0
    for right, ts in enumerate(timestamps):
        while ts - timestamps[left] > window_size:
            left += 1
        if right - left + 1 >= 3:
            return True
    return False


def detect_anomalies(
    messages: List[Tuple[str, datetime]],
    sentiments: List[Tuple[str, str]],
) -> Dict[str, bool]:
    """Return anomaly indicators for the current window."""
    messages_by_user: Dict[str, List[datetime]] = defaultdict(list)
    sentiments_by_user: Dict[str, List[str]] = defaultdict(list)
    all_timestamps: List[datetime] = []

    for user_id, ts in messages:
        messages_by_user[user_id].append(ts)
        all_timestamps.append(ts)

    for user_id, label in sentiments:
        sentiments_by_user[user_id].append(label)

    burst = detect_burst(messages_by_user)
    alternating = detect_alternating_pattern(sentiments_by_user)
    synchronized = detect_synchronized_posting(all_timestamps)

    return {
        "burst_activity": burst,
        "alternating_sentiment": alternating,
        "synchronized_posting": synchronized,
    }

