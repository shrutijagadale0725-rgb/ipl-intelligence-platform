"""
auth/auth_db.py
---------------
Handles SQLite user storage, password hashing, login & registration logic.
No external auth library needed — pure Python + SQLite.
"""

import sqlite3
import hashlib
import os
import re

DB_PATH = os.path.join(os.path.dirname(__file__), "users.db")


# ── DB INIT ───────────────────────────────────────────────────────────────────

def init_db():
    """Creates the users table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            email     TEXT    UNIQUE NOT NULL,
            password  TEXT    NOT NULL,
            team      TEXT,
            created   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ── HELPERS ───────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """SHA-256 hash with a fixed salt. Use bcrypt for production."""
    salt = "ipl_insights_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))


def is_strong_password(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


# ── AUTH OPERATIONS ───────────────────────────────────────────────────────────

def register_user(name: str, email: str, password: str, team: str = "") -> tuple[bool, str]:
    """
    Returns (success: bool, message: str)
    """
    init_db()

    if not name.strip():
        return False, "Name cannot be empty."
    if not is_valid_email(email):
        return False, "Enter a valid email address."
    ok, msg = is_strong_password(password)
    if not ok:
        return False, msg

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (name, email, password, team) VALUES (?, ?, ?, ?)",
            (name.strip(), email.lower().strip(), hash_password(password), team.strip())
        )
        conn.commit()
        conn.close()
        return True, "Account created successfully! Please sign in."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    except Exception as e:
        return False, f"Registration error: {e}"


def login_user(email: str, password: str) -> tuple[bool, str, dict]:
    """
    Returns (success: bool, message: str, user_data: dict)
    user_data contains: id, name, email, team
    """
    init_db()

    if not email or not password:
        return False, "Please fill in all fields.", {}

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT id, name, email, team FROM users WHERE email = ? AND password = ?",
        (email.lower().strip(), hash_password(password))
    )
    row = c.fetchone()
    conn.close()

    if row:
        user = {"id": row[0], "name": row[1], "email": row[2], "team": row[3]}
        return True, f"Welcome back, {row[1]}!", user
    else:
        return False, "Incorrect email or password.", {}


def get_user_by_email(email: str) -> dict | None:
    """Fetch user record by email (for profile display etc.)"""
    init_db()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, name, email, team, created FROM users WHERE email = ?", (email.lower(),))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "email": row[2], "team": row[3], "created": row[4]}
    return None