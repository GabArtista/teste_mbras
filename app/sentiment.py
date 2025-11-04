"""Sentiment analysis engine for the MBRAS challenge."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .constants import (
    INTENSIFIER_FACTOR,
    INTENSIFIERS,
    MBRAS_POSITIVE_FACTOR,
    NEGATION_SCOPE,
    NEGATIONS,
    SENTIMENT_LEXICON,
)
from .utils import normalize_token, tokenize


@dataclass
class MessageSentiment:
    """Store sentiment evaluation for a single message."""

    score: float
    label: str
    token_count: int
    is_meta: bool = False


META_PHRASE = "teste técnico mbras"


def is_meta_message(content: str) -> bool:
    """Return True if content should be treated as meta message."""
    stripped = content.strip()
    if not stripped:
        return False
    normalized = normalize_token(stripped)
    return normalized == normalize_token(META_PHRASE)


def classify_score(score: float) -> str:
    """Classify average sentiment score into categorical label."""
    if score > 0.1:
        return "positive"
    if score < -0.1:
        return "negative"
    return "neutral"


def analyze_message(content: str) -> MessageSentiment:
    """Compute sentiment score for a message content."""
    if is_meta_message(content):
        return MessageSentiment(score=0.0, label="meta", token_count=1, is_meta=True)

    tokens = tokenize(content)
    if not tokens:
        return MessageSentiment(score=0.0, label="neutral", token_count=0, is_meta=False)

    normalized_tokens = [normalize_token(token) for token in tokens]
    negation_indices: List[int] = []
    for idx, norm in enumerate(normalized_tokens):
        if norm in NEGATIONS:
            negation_indices.append(idx)

    total_score = 0.0
    analyzed_tokens = 0
    pending_intensity = 1.0
    for idx, (token, norm) in enumerate(zip(tokens, normalized_tokens)):
        if token.startswith("#"):
            continue

        analyzed_tokens += 1

        if norm in INTENSIFIERS:
            pending_intensity *= INTENSIFIER_FACTOR
            continue

        base_score = SENTIMENT_LEXICON.get(norm)
        if base_score is None:
            pending_intensity = 1.0
            continue

        score = base_score * pending_intensity
        pending_intensity = 1.0

        negation_count = sum(1 for n_idx in negation_indices if n_idx < idx <= n_idx + NEGATION_SCOPE)
        if negation_count % 2 == 1:
            score *= -1

        if score > 0:
            score *= MBRAS_POSITIVE_FACTOR

        total_score += score

    if analyzed_tokens == 0:
        return MessageSentiment(score=0.0, label="neutral", token_count=0, is_meta=False)

    average_score = total_score / analyzed_tokens
    label = classify_score(average_score)
    return MessageSentiment(score=average_score, label=label, token_count=analyzed_tokens, is_meta=False)
