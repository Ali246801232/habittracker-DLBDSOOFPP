import sqlite3
from pathlib import Path

from platformdirs import user_data_dir

DB_PATH = None


def default_db_path() -> str:
    data_dir = Path(user_data_dir("HabitTracker"))
    data_dir.mkdir(parents=True, exist_ok=True)
    return str(data_dir / "habits.db")


def set_db_path(path=None):
    global DB_PATH
    DB_PATH = path if path else default_db_path()


def _get_conn():
    """Get a connection to the database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def initialize_database():
    """Initialize databse with habits, completions, and periods table"""
    try:
        with _get_conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS habits (
                    uuid TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    periodicity_amount INTEGER NOT NULL,
                    periodicity_unit TEXT NOT NULL,
                    notes TEXT,
                    start_date TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS periods (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_uuid TEXT NOT NULL,
                    start TEXT NOT NULL,
                    end TEXT NOT NULL,
                    FOREIGN KEY (habit_uuid) REFERENCES habits(uuid) ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_uuid TEXT NOT NULL,
                    completed_at TEXT NOT NULL,
                    FOREIGN KEY (habit_uuid) REFERENCES habits(uuid) ON DELETE CASCADE
                );
                """
            )
    except sqlite3.Error as e:
        print(f"Database initialization failed: {e}")
        raise


def load_all():
    """Load all habits from database

    Returns:
        dict: {"uuid": "habits", "periods", "completions"}
    """
    data = {}
    try:
        with _get_conn() as conn:
            habits = conn.execute("SELECT * FROM habits").fetchall()

            for habit in habits:
                # Habit details
                uuid = habit["uuid"]

                # Habit periods
                periods = conn.execute(
                    "SELECT start, end FROM periods WHERE habit_uuid = ?", (uuid,)
                ).fetchall()

                # Habit completions
                completions = conn.execute(
                    "SELECT completed_at FROM completions WHERE habit_uuid = ?", (uuid,)
                ).fetchall()

                # Format as dictionary
                data[uuid] = {
                    "habit": dict(habit),
                    "periods": [dict(period) for period in periods],
                    "completions": [
                        completion["completed_at"] for completion in completions
                    ],
                }
    except sqlite3.Error as e:
        print(f"Failed to load data from database: {e}")
        raise
    return data


def save_all(data: dict):
    """Save all habits to database

    Args:
        data (dict): {"uuid": "habits", "periods", "completions"}
    """
    try:
        with _get_conn() as conn:
            # Delete uuids that no longer exist
            rows = conn.execute("SELECT uuid FROM habits").fetchall()
            old_uuids = {row["uuid"] for row in rows}
            new_uuids = set(data.keys())
            to_delete = old_uuids - new_uuids
            if to_delete:
                conn.executemany(
                    "DELETE FROM habits WHERE uuid = ?", [(uuid,) for uuid in to_delete]
                )

            # Upsert remaining habits
            for uuid, data in data.items():
                habit = data["habit"]

                # Habit details
                conn.execute(
                    """
                    INSERT INTO habits (uuid, name, periodicity_amount, periodicity_unit, notes, start_date)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(uuid) DO UPDATE SET
                        name=excluded.name,
                        periodicity_amount=excluded.periodicity_amount,
                        periodicity_unit=excluded.periodicity_unit,
                        notes=excluded.notes
                    """,
                    (
                        uuid,
                        habit["name"],
                        habit["periodicity_amount"],
                        habit["periodicity_unit"],
                        habit["notes"],
                        habit["start_date"],
                    ),
                )

                # Habit periods
                conn.execute("DELETE FROM periods WHERE habit_uuid = ?", (uuid,))
                conn.executemany(
                    "INSERT INTO periods (habit_uuid, start, end) VALUES (?, ?, ?)",
                    [
                        (uuid, period["start"], period["end"])
                        for period in data["periods"]
                    ],
                )

                # Habit completions
                conn.execute("DELETE FROM completions WHERE habit_uuid = ?", (uuid,))
                conn.executemany(
                    "INSERT INTO completions (habit_uuid, completed_at) VALUES (?, ?)",
                    [(uuid, completion) for completion in data["completions"]],
                )
    except sqlite3.Error as e:
        print(f"Failed to save data to database: {e}")
        raise


def is_first_run() -> bool:
    """Return True if the database file does not yet exist"""
    return DB_PATH and not Path(DB_PATH).exists()
