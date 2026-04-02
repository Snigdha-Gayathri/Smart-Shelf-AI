"""Structured mood mapping for non-standard reader moods."""

from __future__ import annotations

GOEMOTIONS_LABELS = frozenset([
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
    "neutral",
])

moodMap = {
    "i want obsession": {
        "emotions": ["desire", "love"],
        "tags": ["possessive", "obsessive", "dark romance"],
        "intensity": "high",
        "aliases": ["obsession", "obsessive love", "possessive love", "i need obsessive love"],
    },
    "emotionally numb": {
        "emotions": ["neutral", "sadness"],
        "tags": ["slow burn", "introspective"],
        "intensity": "low",
        "aliases": ["numb", "emotionally numb", "empty", "dead inside"],
    },
    "ruin me emotionally": {
        "emotions": ["grief", "sadness"],
        "tags": ["angst", "tragic", "dark"],
        "intensity": "very_high",
        "aliases": ["ruin me", "destroy me emotionally", "make me cry", "hurt me"],
    },
    "touch her and die": {
        "emotions": ["anger", "love"],
        "tags": ["protective mmc", "possessive"],
        "intensity": "high",
        "aliases": ["protective mmc", "touch him and die", "touch them and die"],
    },
    "comfort me": {
        "emotions": ["caring", "relief"],
        "tags": ["cozy", "healing", "heartwarming"],
        "intensity": "low",
        "aliases": ["comfort", "soft healing", "cozy", "warm hug"],
    },
    "chaos": {
        "emotions": ["excitement", "surprise"],
        "tags": ["chaotic", "unhinged", "wild"],
        "intensity": "high",
        "aliases": ["unhinged", "chaotic", "wild ride", "messy"],
    },
}

INTENSITY_MULTIPLIERS = {
    "low": 0.9,
    "medium": 1.0,
    "high": 1.12,
    "very_high": 1.2,
}
