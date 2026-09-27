"""
MindPulse: Data Access Repositories (Repository Pattern)
"""

import json
from datetime import datetime
from typing import List, Optional
from src.core.models import User, JournalEntry, MoodLog, AssessmentResult
from src.core.exceptions import StorageError
from src.storage.database import DatabaseManager


class UserRepository:
    """Handles persistence and retrieval of User accounts."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def create_user(self, username: str, password_hash: str, salt: str) -> User:
        query = """
        INSERT INTO users (username, password_hash, salt, created_at)
        VALUES (?, ?, ?, ?)
        """
        now = datetime.now().isoformat()
        try:
            with self.db.transaction() as cur:
                cur.execute(query, (username, password_hash, salt, now))
                user_id = cur.lastrowid
                return User(
                    user_id=user_id,
                    username=username,
                    password_hash=password_hash,
                    salt=salt,
                    created_at=datetime.fromisoformat(now),
                )
        except Exception as e:
            raise StorageError(f"Error creating user: {e}") from e

    def get_by_username(self, username: str) -> Optional[User]:
        query = "SELECT user_id, username, password_hash, salt, created_at, last_login FROM users WHERE username = ?"
        with self.db.query_cursor() as cur:
            cur.execute(query, (username,))
            row = cur.fetchone()
            if not row:
                return None
            return User(
                user_id=row["user_id"],
                username=row["username"],
                password_hash=row["password_hash"],
                salt=row["salt"],
                created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else datetime.now(),
                last_login=datetime.fromisoformat(row["last_login"]) if row["last_login"] else None,
            )

    def update_last_login(self, user_id: int) -> None:
        query = "UPDATE users SET last_login = ? WHERE user_id = ?"
        now = datetime.now().isoformat()
        with self.db.transaction() as cur:
            cur.execute(query, (now, user_id))


class JournalRepository:
    """Handles persistence and retrieval of reflective Journal entries."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def add_entry(self, entry: JournalEntry) -> JournalEntry:
        query = """
        INSERT INTO journal_entries (user_id, title, content, sentiment_score, dominant_emotion, tags, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = entry.created_at.isoformat()
        tags_str = json.dumps(entry.tags)
        try:
            with self.db.transaction() as cur:
                cur.execute(query, (
                    entry.user_id,
                    entry.title,
                    entry.content,
                    entry.sentiment_score,
                    entry.dominant_emotion,
                    tags_str,
                    now
                ))
                entry.entry_id = cur.lastrowid
                return entry
        except Exception as e:
            raise StorageError(f"Error saving journal entry: {e}") from e

    def get_entries_by_user(self, user_id: int, limit: int = 50) -> List[JournalEntry]:
        query = """
        SELECT entry_id, user_id, title, content, sentiment_score, dominant_emotion, tags, created_at
        FROM journal_entries
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """
        with self.db.query_cursor() as cur:
            cur.execute(query, (user_id, limit))
            entries = []
            for row in cur.fetchall():
                tags = json.loads(row["tags"]) if row["tags"] else []
                entries.append(JournalEntry(
                    entry_id=row["entry_id"],
                    user_id=row["user_id"],
                    title=row["title"],
                    content=row["content"],
                    sentiment_score=float(row["sentiment_score"]),
                    dominant_emotion=row["dominant_emotion"],
                    tags=tags,
                    created_at=datetime.fromisoformat(row["created_at"])
                ))
            return entries


class MoodRepository:
    """Handles daily wellbeing logs and lifestyle parameters."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def log_mood(self, log: MoodLog) -> MoodLog:
        query = """
        INSERT OR REPLACE INTO mood_logs 
        (user_id, date, mood_score, mood_label, energy_level, sleep_hours, study_hours, exercise_minutes, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        now = log.created_at.isoformat()
        try:
            with self.db.transaction() as cur:
                cur.execute(query, (
                    log.user_id,
                    log.date,
                    log.mood_score,
                    log.mood_label,
                    log.energy_level,
                    log.sleep_hours,
                    log.study_hours,
                    log.exercise_minutes,
                    log.notes,
                    now
                ))
                log.log_id = cur.lastrowid
                return log
        except Exception as e:
            raise StorageError(f"Error saving mood log: {e}") from e

    def get_logs_by_user(self, user_id: int, days: int = 30) -> List[MoodLog]:
        query = """
        SELECT log_id, user_id, date, mood_score, mood_label, energy_level, sleep_hours, study_hours, exercise_minutes, notes, created_at
        FROM mood_logs
        WHERE user_id = ?
        ORDER BY date ASC
        LIMIT ?
        """
        with self.db.query_cursor() as cur:
            cur.execute(query, (user_id, days))
            logs = []
            for row in cur.fetchall():
                logs.append(MoodLog(
                    log_id=row["log_id"],
                    user_id=row["user_id"],
                    date=row["date"],
                    mood_score=int(row["mood_score"]),
                    mood_label=row["mood_label"],
                    energy_level=int(row["energy_level"]),
                    sleep_hours=float(row["sleep_hours"]),
                    study_hours=float(row["study_hours"]),
                    exercise_minutes=int(row["exercise_minutes"]),
                    notes=row["notes"],
                    created_at=datetime.fromisoformat(row["created_at"])
                ))
            return logs


class AssessmentRepository:
    """Handles clinical and psychometric assessment results."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def save_result(self, result: AssessmentResult) -> AssessmentResult:
        query = """
        INSERT INTO assessment_results (user_id, assessment_type, raw_score, max_score, severity_level, recommendation, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        now = result.completed_at.isoformat()
        try:
            with self.db.transaction() as cur:
                cur.execute(query, (
                    result.user_id,
                    result.assessment_type,
                    result.raw_score,
                    result.max_score,
                    result.severity_level,
                    result.recommendation,
                    now
                ))
                result.assessment_id = cur.lastrowid
                return result
        except Exception as e:
            raise StorageError(f"Error saving assessment result: {e}") from e

    def get_results_by_user(self, user_id: int) -> List[AssessmentResult]:
        query = """
        SELECT assessment_id, user_id, assessment_type, raw_score, max_score, severity_level, recommendation, completed_at
        FROM assessment_results
        WHERE user_id = ?
        ORDER BY completed_at DESC
        """
        with self.db.query_cursor() as cur:
            cur.execute(query, (user_id,))
            results = []
            for row in cur.fetchall():
                results.append(AssessmentResult(
                    assessment_id=row["assessment_id"],
                    user_id=row["user_id"],
                    assessment_type=row["assessment_type"],
                    raw_score=int(row["raw_score"]),
                    max_score=int(row["max_score"]),
                    severity_level=row["severity_level"],
                    recommendation=row["recommendation"],
                    completed_at=datetime.fromisoformat(row["completed_at"])
                ))
            return results
