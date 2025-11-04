"""Static lexicons and constants used by the analyzer."""

from __future__ import annotations

from math import sqrt

# Sentiment lexicon maps normalized tokens to polarity scores.
SENTIMENT_LEXICON = {
    # Positive
    "adorei": 1.0,
    "adoro": 1.0,
    "amo": 1.2,
    "excelente": 1.3,
    "otimo": 1.2,
    "ótimo": 1.2,  # kept for completeness before normalization
    "bom": 1.0,
    "gostei": 1.0,
    "perfeito": 1.3,
    "incrivel": 1.3,
    "incrível": 1.3,
    "fantastico": 1.3,
    "fantástico": 1.3,
    "satisfeito": 0.9,
    # Negative
    "ruim": -1.0,
    "péssimo": -1.4,
    "pessimo": -1.4,
    "terrivel": -1.3,
    "terrível": -1.3,
    "horrivel": -1.5,
    "horrível": -1.5,
    "odeio": -1.2,
    "detestei": -1.1,
    "insuportavel": -1.3,
    "insuportável": -1.3,
    "lamentavel": -1.2,
    "lamentável": -1.2,
}

INTENSIFIERS = {
    "muito",
    "super",
    "bem",
    "demais",
    "mega",
    "extremamente",
    "totalmente",
}

NEGATIONS = {
    "nao",
    "não",
    "nunca",
    "jamais",
    "sem",
}

# Precomputed constants
INTENSIFIER_FACTOR = 1.5
MBRAS_POSITIVE_FACTOR = 2.0
NEGATION_SCOPE = 3
GOLDEN_RATIO = (1 + sqrt(5)) / 2

