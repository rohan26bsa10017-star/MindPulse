"""
Unit tests for core domain models.
"""

import unittest
from datetime import datetime
from src.core.models import User, JournalEntry, MoodLog, AssessmentResult


class TestCoreModels(unittest.TestCase):

    def test_user_instantiation(self):
        user = User(
            user_id=1,
            username="aditya_sharma",
            password_hash="mock_hash_123",
            salt="mock_salt_456"
        )
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.username, "aditya_sharma")
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsNone(user.last_login)

    def test_journal_entry_instantiation(self):
        entry = JournalEntry(
            entry_id=10,
            user_id=1,
            title="Late night coding",
            content="Felt productive yet slightly tired.",
            sentiment_score=0.45,
            dominant_emotion="Joy",
            tags=["coding", "productive"]
        )
        self.assertEqual(entry.title, "Late night coding")
        self.assertEqual(entry.tags, ["coding", "productive"])
        self.assertEqual(entry.sentiment_score, 0.45)

    def test_mood_log_instantiation(self):
        log = MoodLog(
            log_id=100,
            user_id=1,
            date="2026-09-27",
            mood_score=8,
            mood_label="Energized",
            energy_level=4,
            sleep_hours=7.5,
            study_hours=5.0,
            exercise_minutes=45,
            notes="Morning run helped focus"
        )
        self.assertEqual(log.mood_score, 8)
        self.assertEqual(log.sleep_hours, 7.5)
        self.assertEqual(log.exercise_minutes, 45)

    def test_assessment_result_instantiation(self):
        result = AssessmentResult(
            assessment_id=5,
            user_id=1,
            assessment_type="PSS-10",
            raw_score=14,
            max_score=40,
            severity_level="Moderate Stress",
            recommendation="Practice grounding techniques."
        )
        self.assertEqual(result.assessment_type, "PSS-10")
        self.assertEqual(result.raw_score, 14)


if __name__ == "__main__":
    unittest.main()
