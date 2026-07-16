import os
import secrets

from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Session config - memory-only, 30-minute lifetime
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 1800

    # Rate limiting
    RATE_LIMIT_MAX_REQUESTS = 10
    RATE_LIMIT_WINDOW_SECONDS = 60

    # Question categories metadata
    CATEGORIES = {
        "social": {
            "name": "Social Personality",
            "icon": "SP",
            "description": "Introvert/extrovert tendencies, communication style, and social energy.",
            "color": "#3b82f6",
        },
        "mental_health": {
            "name": "Mental Wellbeing Screener",
            "icon": "MW",
            "description": "Self-report indicators for mood and anxiety tendencies. Not a diagnosis.",
            "color": "#8b5cf6",
        },
        "big_five": {
            "name": "Big Five (OCEAN)",
            "icon": "BF",
            "description": "Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism.",
            "color": "#0f766e",
        },
        "emotional_intelligence": {
            "name": "Emotional Intelligence (EQ)",
            "icon": "EQ",
            "description": "Self-awareness, empathy, emotional regulation, and social skills.",
            "color": "#d97706",
        },
        "stress_burnout": {
            "name": "Stress & Burnout Tendency",
            "icon": "SB",
            "description": "Work-life balance, stress coping mechanisms, and burnout indicators.",
            "color": "#e11d48",
        },
        "career": {
            "name": "Work/Career Personality",
            "icon": "WK",
            "description": "Leadership style, teamwork vs. independent work, decision-making style.",
            "color": "#0891b2",
        },
        "relationship": {
            "name": "Relationship & Attachment Style",
            "icon": "RS",
            "description": "Attachment patterns, trust dynamics, and communication in relationships.",
            "color": "#be185d",
        },
        "self_esteem": {
            "name": "Self-Esteem & Confidence",
            "icon": "SE",
            "description": "Self-worth, confidence level, inner critic, and personal resilience.",
            "color": "#16a34a",
        },
    }
