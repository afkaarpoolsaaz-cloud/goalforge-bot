import sqlite3
import threading
from datetime import datetime, date, timedelta

_local = threading.local()


def get_conn():
    if not hasattr(_local, "conn"):
        _local.conn = sqlite3.connect("data.db")
        _local.cursor = _local.conn.cursor()
        _init_tables(_local.cursor, _local.conn)
    return _local.conn, _local.cursor


def _init_tables(cursor, conn):
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            status TEXT DEFAULT 'active',
            progress INTEGER DEFAULT 0,
            created_at TIMESTAMP,
            completed_at TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS user_profile (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            coaching_style TEXT DEFAULT 'friendly',
            main_goal TEXT,
            reminder_time TEXT,
            daily_minutes INTEGER DEFAULT 15,
            language TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS behavior_patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            pattern_type TEXT,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS learning (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            input_text TEXT,
            ai_response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS streaks (
            user_id INTEGER PRIMARY KEY,
            current_streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0,
            last_active_date TEXT,
            total_active_days INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS daily_checkins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            checkin_date TEXT,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS xp (
            user_id INTEGER PRIMARY KEY,
            total_xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS xp_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            achievement_key TEXT,
            achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS trust (
            user_id INTEGER PRIMARY KEY,
            score INTEGER DEFAULT 50,
            total_verified INTEGER DEFAULT 0,
            total_fake INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS premium (
            user_id INTEGER PRIMARY KEY,
            is_premium INTEGER DEFAULT 0,
            expires_at TEXT,
            granted_by TEXT
        );
    """)
    conn.commit()


# =========================
# MEMORY
# =========================
def save_memory(user_id, role, message):
    conn, cursor = get_conn()
    cursor.execute("INSERT INTO memory (user_id, role, message) VALUES (?, ?, ?)", (user_id, role, message))
    conn.commit()


def get_memory(user_id, limit=15):
    _, cursor = get_conn()
    cursor.execute("SELECT role, message FROM memory WHERE user_id=? ORDER BY id DESC LIMIT ?", (user_id, limit))
    return list(reversed(cursor.fetchall()))


# =========================
# USER PROFILE
# =========================
def save_user_profile(user_id, name=None, coaching_style=None, main_goal=None,
                      reminder_time=None, daily_minutes=None, language=None):
    conn, cursor = get_conn()
    cursor.execute("SELECT user_id FROM user_profile WHERE user_id=?", (user_id,))
    exists = cursor.fetchone()

    if exists:
        if name: cursor.execute("UPDATE user_profile SET name=? WHERE user_id=?", (name, user_id))
        if coaching_style: cursor.execute("UPDATE user_profile SET coaching_style=? WHERE user_id=?", (coaching_style, user_id))
        if main_goal: cursor.execute("UPDATE user_profile SET main_goal=? WHERE user_id=?", (main_goal, user_id))
        if reminder_time: cursor.execute("UPDATE user_profile SET reminder_time=? WHERE user_id=?", (reminder_time, user_id))
        if daily_minutes: cursor.execute("UPDATE user_profile SET daily_minutes=? WHERE user_id=?", (daily_minutes, user_id))
        if language: cursor.execute("UPDATE user_profile SET language=? WHERE user_id=?", (language, user_id))
    else:
        cursor.execute(
            "INSERT INTO user_profile (user_id, name, coaching_style, main_goal, reminder_time, daily_minutes, language) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, name, coaching_style or 'friendly', main_goal, reminder_time, daily_minutes or 15, language or 'en')
        )
    conn.commit()


def get_user_profile(user_id):
    _, cursor = get_conn()
    cursor.execute("SELECT name, coaching_style, main_goal, created_at, reminder_time, daily_minutes, language FROM user_profile WHERE user_id=?", (user_id,))
    return cursor.fetchone()


def get_user_language(user_id):
    _, cursor = get_conn()
    cursor.execute("SELECT language FROM user_profile WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 'en'


def get_all_reminders():
    _, cursor = get_conn()
    cursor.execute("SELECT user_id, reminder_time, name, main_goal, daily_minutes FROM user_profile WHERE reminder_time IS NOT NULL")
    return cursor.fetchall()


def save_user_name(user_id, name):
    save_user_profile(user_id, name=name)


# =========================
# GOALS
# =========================
def save_goal(user_id, text):
    conn, cursor = get_conn()
    cursor.execute("INSERT INTO goals (user_id, text) VALUES (?, ?)", (user_id, text))
    conn.commit()
    save_user_profile(user_id, main_goal=text)


def get_goals(user_id):
    _, cursor = get_conn()
    cursor.execute("SELECT id, text, status, progress, created_at FROM goals WHERE user_id=? AND status='active' ORDER BY id DESC", (user_id,))
    return cursor.fetchall()


def complete_goal(user_id, goal_id):
    conn, cursor = get_conn()
    cursor.execute("UPDATE goals SET status='completed', completed_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?", (goal_id, user_id))
    conn.commit()


def update_goal_progress(user_id, goal_id, progress):
    conn, cursor = get_conn()
    cursor.execute("UPDATE goals SET progress=? WHERE id=? AND user_id=?", (progress, goal_id, user_id))
    conn.commit()


# =========================
# STREAK
# =========================
def update_streak(user_id):
    conn, cursor = get_conn()
    today = date.today().isoformat()
    cursor.execute("SELECT current_streak, longest_streak, last_active_date, total_active_days FROM streaks WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("INSERT INTO streaks (user_id, current_streak, longest_streak, last_active_date, total_active_days) VALUES (?, 1, 1, ?, 1)", (user_id, today))
        conn.commit()
        return 1

    current, longest, last_date, total = row
    if last_date == today:
        return current

    yesterday = (date.today() - timedelta(days=1)).isoformat()
    current = current + 1 if last_date == yesterday else 1
    longest = max(longest, current)
    total += 1

    cursor.execute("UPDATE streaks SET current_streak=?, longest_streak=?, last_active_date=?, total_active_days=? WHERE user_id=?",
                   (current, longest, today, total, user_id))
    conn.commit()
    return current


def get_streak(user_id):
    _, cursor = get_conn()
    cursor.execute("SELECT current_streak, longest_streak, total_active_days FROM streaks WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row if row else (0, 0, 0)


# =========================
# CHECKINS
# =========================
def save_checkin(user_id, note=""):
    conn, cursor = get_conn()
    today = date.today().isoformat()
    cursor.execute("SELECT id FROM daily_checkins WHERE user_id=? AND checkin_date=?", (user_id, today))
    if cursor.fetchone():
        return False
    cursor.execute("INSERT INTO daily_checkins (user_id, checkin_date, note) VALUES (?, ?, ?)", (user_id, today, note))
    conn.commit()
    return True


def get_checkins(user_id, limit=7):
    _, cursor = get_conn()
    cursor.execute("SELECT checkin_date, note FROM daily_checkins WHERE user_id=? ORDER BY checkin_date DESC LIMIT ?", (user_id, limit))
    return cursor.fetchall()


# =========================
# XP
# =========================
def add_xp(user_id, amount, reason=""):
    conn, cursor = get_conn()
    cursor.execute("SELECT total_xp, level FROM xp WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if row:
        total_xp, old_level = row[0] + amount, row[1]
        new_level = (total_xp // 100) + 1
        cursor.execute("UPDATE xp SET total_xp=?, level=? WHERE user_id=?", (total_xp, new_level, user_id))
    else:
        total_xp, old_level = amount, 1
        new_level = (total_xp // 100) + 1
        cursor.execute("INSERT INTO xp (user_id, total_xp, level) VALUES (?, ?, ?)", (user_id, total_xp, new_level))

    cursor.execute("INSERT INTO xp_log (user_id, amount, reason) VALUES (?, ?, ?)", (user_id, amount, reason))
    conn.commit()
    return total_xp, new_level, new_level > old_level


def get_xp(user_id):
    _, cursor = get_conn()
    cursor.execute("SELECT total_xp, level FROM xp WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return 0, 1, 100
    total_xp, level = row
    return total_xp, level, (level * 100) - total_xp


# =========================
# ACHIEVEMENTS
# =========================
ACHIEVEMENT_LIST = {
    "first_step":    ("🌱 First Step",     "Sent first message"),
    "first_goal":    ("🎯 Goal Setter",    "Set first goal"),
    "first_checkin": ("✅ First Checkin",  "First daily checkin"),
    "streak_3":      ("⚡ 3 Day Streak",   "3 consecutive days active"),
    "streak_7":      ("🔥 7 Day Streak",   "7 consecutive days active"),
    "streak_30":     ("🏆 30 Day Streak",  "30 consecutive days active"),
    "streak_90":     ("👑 90 Day Streak",  "90 consecutive days active"),
    "level_5":       ("💪 Level 5",        "Reached Level 5"),
    "level_10":      ("🔥 Level 10",       "Reached Level 10"),
    "comeback":      ("🦅 Comeback Hero",  "Returned after inactivity"),
}


def check_and_grant_achievements(user_id):
    conn, cursor = get_conn()
    cursor.execute("SELECT achievement_key FROM achievements WHERE user_id=?", (user_id,))
    existing = {row[0] for row in cursor.fetchall()}
    new_achievements = []

    current, longest, total = get_streak(user_id)
    total_xp, level, _ = get_xp(user_id)
    checkins = get_checkins(user_id, limit=1)
    goals = get_goals(user_id)

    def grant(key):
        if key not in existing:
            cursor.execute("INSERT INTO achievements (user_id, achievement_key) VALUES (?, ?)", (user_id, key))
            new_achievements.append(key)

    if total > 0: grant("first_step")
    if goals: grant("first_goal")
    if checkins: grant("first_checkin")
    if current >= 3: grant("streak_3")
    if current >= 7: grant("streak_7")
    if current >= 30: grant("streak_30")
    if current >= 90: grant("streak_90")
    if level >= 5: grant("level_5")
    if level >= 10: grant("level_10")

    conn.commit()
    return new_achievements


def get_achievements(user_id):
    _, cursor = get_conn()
    cursor.execute("SELECT achievement_key, achieved_at FROM achievements WHERE user_id=? ORDER BY achieved_at DESC", (user_id,))
    return cursor.fetchall()


# =========================
# TRUST
# =========================
def get_trust(user_id):
    _, cursor = get_conn()
    cursor.execute("SELECT score, total_verified, total_fake FROM trust WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row if row else (50, 0, 0)


def update_trust(user_id, delta):
    conn, cursor = get_conn()
    cursor.execute("SELECT score FROM trust WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row:
        new_score = max(0, min(100, row[0] + delta))
        cursor.execute("UPDATE trust SET score=? WHERE user_id=?", (new_score, user_id))
    else:
        new_score = max(0, min(100, 50 + delta))
        cursor.execute("INSERT INTO trust (user_id, score) VALUES (?, ?)", (user_id, new_score))
    conn.commit()
    return new_score


# =========================
# PREMIUM
# =========================
def is_premium(user_id):
    _, cursor = get_conn()
    cursor.execute("SELECT is_premium, expires_at FROM premium WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row or not row[0]:
        return False
    if row[1] and row[1] < date.today().isoformat():
        return False
    return True


def grant_premium(user_id, days=30, granted_by="system"):
    conn, cursor = get_conn()
    expires = (date.today() + timedelta(days=days)).isoformat()
    cursor.execute("SELECT user_id FROM premium WHERE user_id=?", (user_id,))
    if cursor.fetchone():
        cursor.execute("UPDATE premium SET is_premium=1, expires_at=?, granted_by=? WHERE user_id=?", (expires, granted_by, user_id))
    else:
        cursor.execute("INSERT INTO premium (user_id, is_premium, expires_at, granted_by) VALUES (?, 1, ?, ?)", (user_id, expires, granted_by))
    conn.commit()


# =========================
# BEHAVIOR & LEARNING
# =========================
def save_behavior(user_id, pattern_type, value):
    conn, cursor = get_conn()
    cursor.execute("INSERT INTO behavior_patterns (user_id, pattern_type, value) VALUES (?, ?, ?)", (user_id, pattern_type, value))
    conn.commit()


def save_learning(user_id, input_text, ai_response):
    conn, cursor = get_conn()
    cursor.execute("INSERT INTO learning (user_id, input_text, ai_response) VALUES (?, ?, ?)", (user_id, input_text, ai_response))
    conn.commit()
