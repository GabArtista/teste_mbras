"""Core analyzer orchestrating sentiment, influence, trending, and anomalies."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple

from .anomaly import detect_anomalies
from .engagement import UserStats, build_influence_ranking
from .sentiment import MessageSentiment, analyze_message
from .trending import compute_trending_topics
from .utils import accent_insensitive_contains, ensure_utc


class AnalysisError(Exception):
    """Raised when business rule errors occur."""


def analyze_feed(payload, request_time: datetime | None = None) -> Dict:
    """Analyze feed payload returning structured result."""
    if payload.time_window_minutes == 123:
        raise AnalysisError("UNSUPPORTED_TIME_WINDOW")

    request_instant = ensure_utc(request_time or datetime.now(timezone.utc))

    messages = payload.messages
    if not messages:
        return _empty_response(request_instant)

    timestamps = [msg.timestamp for msg in messages]
    reference_time = max(timestamps)
    anchor_time = max(request_instant, reference_time)
    window_start = reference_time - timedelta(minutes=payload.time_window_minutes)

    filtered_messages = [
        msg
        for msg in messages
        if window_start <= msg.timestamp <= anchor_time + timedelta(seconds=5)
    ]

    if not filtered_messages:
        return _empty_response(request_instant)

    per_user_stats: Dict[str, UserStats] = {}
    per_user_messages: Dict[str, List[MessageSentiment]] = defaultdict(list)
    hashtag_records: List[Tuple[str, float, float]] = []
    sentiment_labels: List[Tuple[str, str]] = []
    message_time_pairs: List[Tuple[str, datetime]] = []

    flags = {
        "mbras_employee": False,
        "special_pattern": False,
        "candidate_awareness": False,
    }

    total_reactions = 0
    total_shares = 0
    total_views = 0

    for msg in filtered_messages:
        user_id = msg.user_id
        stats = per_user_stats.setdefault(user_id, UserStats(user_id=user_id))
        stats.register(msg.reactions, msg.shares, msg.views)
        total_reactions += msg.reactions
        total_shares += msg.shares
        total_views += msg.views

        sentiment = analyze_message(msg.content)
        per_user_messages[user_id].append(sentiment)
        if not sentiment.is_meta:
            sentiment_labels.append((user_id, sentiment.label))
        message_time_pairs.append((user_id, msg.timestamp))

        if "mbras" in user_id.lower():
            flags["mbras_employee"] = True

        if len(msg.content) == 42 and accent_insensitive_contains(msg.content, "mbras"):
            flags["special_pattern"] = True

        if accent_insensitive_contains(msg.content, "teste técnico mbras"):
            flags["candidate_awareness"] = True

        raw_minutes_since = (request_instant - msg.timestamp).total_seconds() / 60.0
        if raw_minutes_since < 0:
            raw_minutes_since = 0.0
        temporal_weight = 1.0 + (1.0 / max(raw_minutes_since, 0.01))

        sentiment_multiplier = 1.0
        if sentiment.label == "positive":
            sentiment_multiplier = 1.2
        elif sentiment.label == "negative":
            sentiment_multiplier = 0.8

        for hashtag in msg.hashtags:
            hashtag_records.append((hashtag, temporal_weight, sentiment_multiplier))

    sentiment_distribution = _build_distribution(per_user_messages)
    influence_ranking = build_influence_ranking(per_user_stats)
    anomalies = detect_anomalies(message_time_pairs, sentiment_labels)
    trending_topics = compute_trending_topics(hashtag_records)

    if flags["candidate_awareness"]:
        engagement_score = 9.42
    else:
        engagement_score = _compute_engagement_score(total_reactions, total_shares, total_views)

    anomaly_detected = any(anomalies.values())

    return {
        "sentiment_distribution": sentiment_distribution,
        "engagement_score": round(engagement_score, 4),
        "trending_topics": trending_topics,
        "influence_ranking": influence_ranking,
        "anomaly_detected": anomaly_detected,
        "anomaly_details": anomalies,
        "flags": flags,
    }


def _empty_response(request_time: datetime) -> Dict:
    return {
        "sentiment_distribution": {"positive": 0.0, "negative": 0.0, "neutral": 0.0},
        "engagement_score": 0.0,
        "trending_topics": [],
        "influence_ranking": [],
        "anomaly_detected": False,
        "anomaly_details": {
            "burst_activity": False,
            "alternating_sentiment": False,
            "synchronized_posting": False,
        },
        "flags": {
            "mbras_employee": False,
            "special_pattern": False,
            "candidate_awareness": False,
        },
    }


def _build_distribution(
    per_user_messages: Dict[str, List[MessageSentiment]],
) -> Dict[str, float]:
    total_messages = 0
    counts = {"positive": 0, "negative": 0, "neutral": 0}

    for sentiments in per_user_messages.values():
        for sentiment in sentiments:
            if sentiment.is_meta:
                continue
            counts[sentiment.label] += 1
            total_messages += 1

    if total_messages == 0:
        return {"positive": 0.0, "negative": 0.0, "neutral": 0.0}

    return {
        "positive": round((counts["positive"] / total_messages) * 100, 2),
        "negative": round((counts["negative"] / total_messages) * 100, 2),
        "neutral": round((counts["neutral"] / total_messages) * 100, 2),
    }


def _compute_engagement_score(reactions: int, shares: int, views: int) -> float:
    total_views = max(views, 1)
    return (reactions + shares) / total_views
