"""
MindPulse: Intelligent Student Mental Health & Cognitive Wellness Management System
Core Data Models and Type Definitions
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class User:
    """Represents an authenticated student/user in the system."""
    user_id: int
    username: str
    password_hash: str
    salt: str
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None


@dataclass
class JournalEntry:
    """Represents a private reflective journal entry with sentiment analysis."""
    entry_id: Optional[int]
    user_id: int
    title: str
    content: str
    sentiment_score: float  # Normalized between -1.0 (very negative) and +1.0 (very positive)
    dominant_emotion: str    # e.g., Joy, Anxiety, Sadness, Calm, Anger, Neutral
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MoodLog:
    """Represents a multi-dimensional daily wellbeing and habit record."""
    log_id: Optional[int]
    user_id: int
    date: str               # YYYY-MM-DD
    mood_score: int         # 1 (Very Low / Distressed) to 10 (Peak Vitality)
    mood_label: str         # Happy, Stressed, Anxious, Calm, Exhausted, etc.
    energy_level: int       # 1 to 5
    sleep_hours: float      # e.g., 6.5
    study_hours: float      # e.g., 4.0
    exercise_minutes: int   # e.g., 30
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AssessmentResult:
    """Represents the outcome of a clinical or psychometric questionnaire."""
    assessment_id: Optional[int]
    user_id: int
    assessment_type: str    # 'PSS-10' (Stress), 'PHQ-9' (Depression), 'GAD-7' (Anxiety)
    raw_score: int
    max_score: int
    severity_level: str     # Low / Mild / Moderate / Severe
    recommendation: str
    completed_at: datetime = field(default_factory=datetime.now)
