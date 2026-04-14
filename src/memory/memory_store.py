"""Memory Store — SQLite persistent memory for cross-session context.

Stores conversation history, computed strategies, and user preferences
in a local SQLite database for persistent cross-session memory.
"""

import sqlite3
import json
from datetime import datetime

DB_PATH = "f1_memory.db"


class MemoryStore:
    """Persistent memory store backed by SQLite."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Create tables if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS strategies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    circuit TEXT,
                    total_laps INTEGER,
                    weather_conditions TEXT,
                    recommended_strategy TEXT,
                    total_time REAL,
                    details TEXT,
                    timestamp TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE,
                    value TEXT,
                    updated_at TEXT
                )
            """)
            conn.commit()

    # ── Conversation Memory ────────────────────────────────────────

    def save_message(self, session_id: str, role: str, content: str):
        """Save a chat message to conversation history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (session_id, role, content, timestamp) "
                "VALUES (?, ?, ?, ?)",
                (session_id, role, content, datetime.now().isoformat()),
            )

    def get_conversation_history(self, session_id: str, limit: int = 20) -> list:
        """Retrieve recent conversation history for a session."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content, timestamp FROM conversations "
                "WHERE session_id = ? ORDER BY id DESC LIMIT ?",
                (session_id, limit),
            ).fetchall()
        return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in reversed(rows)]

    def get_all_sessions(self) -> list:
        """List all past conversation sessions."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT DISTINCT session_id, MIN(timestamp) as started, "
                "COUNT(*) as messages FROM conversations "
                "GROUP BY session_id ORDER BY started DESC"
            ).fetchall()
        return [{"session_id": r[0], "started": r[1], "messages": r[2]} for r in rows]

    # ── Strategy Memory ────────────────────────────────────────────

    def save_strategy(self, circuit: str, total_laps: int, weather: dict,
                      strategy_name: str, total_time: float, details: dict):
        """Save a computed strategy for future reference."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO strategies (circuit, total_laps, weather_conditions, "
                "recommended_strategy, total_time, details, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (circuit, total_laps, json.dumps(weather), strategy_name,
                 total_time, json.dumps(details), datetime.now().isoformat()),
            )

    def get_past_strategies(self, circuit: str = None, limit: int = 10) -> list:
        """Get previously computed strategies, optionally filtered by circuit."""
        with sqlite3.connect(self.db_path) as conn:
            if circuit:
                rows = conn.execute(
                    "SELECT circuit, total_laps, weather_conditions, "
                    "recommended_strategy, total_time, details, timestamp "
                    "FROM strategies WHERE circuit = ? ORDER BY id DESC LIMIT ?",
                    (circuit, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT circuit, total_laps, weather_conditions, "
                    "recommended_strategy, total_time, details, timestamp "
                    "FROM strategies ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()
        return [
            {"circuit": r[0], "total_laps": r[1], "weather": json.loads(r[2]),
             "strategy": r[3], "total_time": r[4],
             "details": json.loads(r[5]), "timestamp": r[6]}
            for r in rows
        ]

    # ── User Preferences ──────────────────────────────────────────

    def save_preference(self, key: str, value: str):
        """Save or update a user preference."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO user_preferences (key, value, updated_at) "
                "VALUES (?, ?, ?)",
                (key, value, datetime.now().isoformat()),
            )

    def get_preference(self, key: str, default: str = None) -> str:
        """Get a single user preference."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT value FROM user_preferences WHERE key = ?", (key,)
            ).fetchone()
        return row[0] if row else default

    def get_all_preferences(self) -> dict:
        """Get all user preferences as a dict."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT key, value FROM user_preferences").fetchall()
        return {r[0]: r[1] for r in rows}
