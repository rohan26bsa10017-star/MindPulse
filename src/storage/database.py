"""
MindPulse: SQLite Database Connection & Schema Management
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Generator, Optional
from src.core.exceptions import StorageError


class DatabaseManager:
    """
    Manages SQLite database connections, transactional scopes,
    and schema lifecycle migrations.
    """

    def __init__(self, db_path: str = "data/mindpulse.db"):
        self.db_path = db_path
        # Ensure parent directory exists
        dirname = os.path.dirname(self.db_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)
        self._mem_conn: Optional[sqlite3.Connection] = None
        if self.db_path == ":memory:":
            self._mem_conn = sqlite3.connect(":memory:")
            self._mem_conn.row_factory = sqlite3.Row
            self._mem_conn.execute("PRAGMA foreign_keys = ON;")
        self.initialize_schema()

    def get_connection(self) -> sqlite3.Connection:
        """Returns a connection configured with row factories and foreign keys."""
        if self._mem_conn is not None:
            return self._mem_conn
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            raise StorageError(f"Database connection error: {e}") from e

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Cursor, None, None]:
        """Provides an ACID transaction scope with auto-commit and rollback on error."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise StorageError(f"Transaction aborted: {e}") from e
        finally:
            if self._mem_conn is None:
                conn.close()

    @contextmanager
    def query_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Provides a read-only or query cursor safely closing connections when applicable."""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            if self._mem_conn is None:
                conn.close()

    def initialize_schema(self) -> None:
        """Creates the relational database schema if it does not already exist."""
        schema_sql = """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS journal_entries (
            entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            sentiment_score REAL NOT NULL,
            dominant_emotion TEXT NOT NULL,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS mood_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            mood_label TEXT NOT NULL,
            energy_level INTEGER NOT NULL,
            sleep_hours REAL NOT NULL,
            study_hours REAL NOT NULL,
            exercise_minutes INTEGER NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, date),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS assessment_results (
            assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            assessment_type TEXT NOT NULL,
            raw_score INTEGER NOT NULL,
            max_score INTEGER NOT NULL,
            severity_level TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_journal_user ON journal_entries(user_id);
        CREATE INDEX IF NOT EXISTS idx_mood_user_date ON mood_logs(user_id, date);
        CREATE INDEX IF NOT EXISTS idx_assessment_user ON assessment_results(user_id);
        """
        try:
            with self.transaction() as cur:
                cur.executescript(schema_sql)
        except Exception as e:
            raise StorageError(f"Failed to initialize schema: {e}") from e
