import os
import secrets
from dotenv import load_dotenv

load_dotenv(override=True)


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    # Session config — memory-only, 30-minute lifetime
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes in seconds

    # Rate limiting
    RATE_LIMIT_MAX_REQUESTS = 10
    RATE_LIMIT_WINDOW_SECONDS = 60

    # Question categories metadata
    CATEGORIES = {
        "social": {
            "name": "Social Personality",
            "icon": "👥",
            "description": "Introvert/extrovert tendencies, communication style, and social energy.",
            "color": "#7C9FE8",
        },
        "mental_health": {
            "name": "Mental Wellbeing Screener",
            "icon": "🧠",
            "description": "Self-report indicators for mood and anxiety tendencies. Not a diagnosis.",
            "color": "#A78BDA",
        },
        "big_five": {
            "name": "Big Five (OCEAN)",
            "icon": "🌊",
            "description": "Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism.",
            "color": "#6DB5A0",
        },
        "emotional_intelligence": {
            "name": "Emotional Intelligence (EQ)",
            "icon": "💡",
            "description": "Self-awareness, empathy, emotional regulation, and social skills.",
            "color": "#E8A87C",
        },
        "stress_burnout": {
            "name": "Stress & Burnout Tendency",
            "icon": "🔥",
            "description": "Work-life balance, stress coping mechanisms, and burnout indicators.",
            "color": "#D4799C",
        },
        "career": {
            "name": "Work/Career Personality",
            "icon": "💼",
            "description": "Leadership style, teamwork vs. independent work, decision-making style.",
            "color": "#7CAFC4",
        },
        "relationship": {
            "name": "Relationship & Attachment Style",
            "icon": "💜",
            "description": "Attachment patterns, trust dynamics, and communication in relationships.",
            "color": "#C49EC4",
        },
        "self_esteem": {
            "name": "Self-Esteem & Confidence",
            "icon": "✨",
            "description": "Self-worth, confidence level, inner critic, and personal resilience.",
            "color": "#A0C4B8",
        },
    }
