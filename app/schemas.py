"""Pydantic schemas used by the MBRAS analyzer service."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List
import re

from pydantic import BaseModel, Field, field_validator

from .utils import normalize_token

USER_ID_PATTERN = re.compile(r"^user_[a-z0-9_]{3,}$", re.IGNORECASE)


class MessageInput(BaseModel):
    """Single message within the analysis payload."""

    id: str = Field(min_length=1)
    content: str = Field(min_length=1, max_length=280)
    timestamp: datetime
    user_id: str = Field(min_length=1)
    hashtags: List[str] = Field(default_factory=list)
    reactions: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)

    @field_validator("timestamp", mode="before")
    @classmethod
    def _ensure_rfc3339_z(cls, value: str) -> datetime:
        if isinstance(value, datetime):
            dt = value
        elif isinstance(value, str):
            if not value.endswith("Z"):
                msg = "timestamp must be an RFC 3339 string with UTC suffix 'Z'"
                raise ValueError(msg)
            try:
                dt = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError as exc:
                raise ValueError("timestamp must follow RFC3339 format YYYY-MM-DDTHH:MM:SSZ") from exc
        else:
            raise TypeError("timestamp must be a string in RFC3339 format")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    @field_validator("user_id")
    @classmethod
    def _validate_user_id(cls, value: str) -> str:
        normalized = normalize_token(value)
        if not USER_ID_PATTERN.fullmatch(normalized):
            raise ValueError("user_id must match pattern ^user_[a-z0-9_]{3,}$")
        return value

    @field_validator("hashtags")
    @classmethod
    def _validate_hashtags(cls, value: List[str]) -> List[str]:
        validated = []
        for item in value:
            if not isinstance(item, str):
                raise TypeError("hashtags must be strings")
            if not item.startswith("#"):
                raise ValueError("hashtags must start with '#'")
            validated.append(item)
        return validated


class AnalyzeFeedRequest(BaseModel):
    """Payload accepted by the /analyze-feed endpoint."""

    messages: List[MessageInput] = Field(min_length=1)
    time_window_minutes: int = Field(gt=0)


class SentimentDistribution(BaseModel):
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 0.0


class InfluenceEntry(BaseModel):
    user_id: str
    followers: int
    engagement_rate: float
    influence_score: float


class AnalysisResult(BaseModel):
    sentiment_distribution: SentimentDistribution
    engagement_score: float
    trending_topics: List[str]
    influence_ranking: List[InfluenceEntry]
    anomaly_detected: bool
    anomaly_details: Dict[str, bool]
    flags: Dict[str, bool]
    processing_time_ms: int


class AnalyzeFeedResponse(BaseModel):
    analysis: AnalysisResult
