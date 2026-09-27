"""
Unit tests for database transactions and repository operations.
"""

import unittest
from datetime import datetime
from src.core.models import JournalEntry, MoodLog, AssessmentResult
from src.storage.database import DatabaseManager
from src.storage.repository import (
    UserRepository,
    JournalRepository,
    MoodRepository,
    AssessmentRepository,
)


class TestStorageAndRepositories(unittest.TestCase):

    def setUp(self):
        # Use fresh in-memory SQLite database
        self.db = DatabaseManager(":memory:")
        self.user_repo = UserRepository(self.db)
        self.journal_repo = JournalRepository(self.db)
        self.mood_repo = MoodRepository(self.db)
        self.assessment_repo = AssessmentRepository(self.db)

        # Seed test user
        self.user = self.user_repo.create_user("student_one", "hash1", "salt1")

    def test_journal_repository_crud(self):
        entry = JournalEntry(
            entry_id=None,
            user_id=self.user.user_id,
            title="Evening Reflection",
            content="Today was peaceful and productive.",
            sentiment_score=0.8,
            dominant_emotion="Joy",
            tags=["peaceful", "productive"]
        )
        saved = self.journal_repo.add_entry(entry)
        self.assertIsNotNone(saved.entry_id)

        entries = self.journal_repo.get_entries_by_user(self.user.user_id)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Evening Reflection")
        self.assertEqual(entries[0].tags, ["peaceful", "productive"])

    def test_mood_repository_crud(self):
        log = MoodLog(
            log_id=None,
            user_id=self.user.user_id,
            date="2026-09-27",
            mood_score=7,
            mood_label="Content",
            energy_level=4,
            sleep_hours=7.0,
            study_hours=4.5,
            exercise_minutes=30,
            notes="Felt good overall."
        )
        saved = self.mood_repo.log_mood(log)
        self.assertIsNotNone(saved.log_id)

        logs = self.mood_repo.get_logs_by_user(self.user.user_id)
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0].mood_score, 7)
        self.assertEqual(logs[0].sleep_hours, 7.0)

    def test_assessment_repository_crud(self):
        res = AssessmentResult(
            assessment_id=None,
            user_id=self.user.user_id,
            assessment_type="PHQ-9",
            raw_score=4,
            max_score=27,
            severity_level="Minimal / None",
            recommendation="Continue healthy habits."
        )
        saved = self.assessment_repo.save_result(res)
        self.assertIsNotNone(saved.assessment_id)

        history = self.assessment_repo.get_results_by_user(self.user.user_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].assessment_type, "PHQ-9")
        self.assertEqual(history[0].severity_level, "Minimal / None")


if __name__ == "__main__":
    unittest.main()
