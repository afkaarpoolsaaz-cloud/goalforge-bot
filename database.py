import sqlite3
from datetime import datetime, date, timedelta

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

# ---------- schema setup ----------
cursor.execute("""
CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    text TEXT,
    status TEXT DEFAULT 'active',
    progress INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_settings (
    user_id INTEGER PRIMARY KEY,
    language TEXT DEFAULT 'en',
    name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    role TEXT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS streaks (
    user_id INTEGER PRIMARY KEY,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_active_date TEXT,
    total_active_days INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS daily_checkins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    checkin_date TEXT,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS user_profile (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    coaching_style TEXT DEFAULT 'friendly',
    main_goal TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reminder_time TEXT,
    daily_minutes INTEGER DEFAULT 15,
    language TEXT DEFAULT 'en'
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS xp (
    user_id INTEGER PRIMARY KEY,
    total_xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS xp_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount INTEGER,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    achievement_key TEXT,
    achieved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS trust (
    user_id INTEGER PRIMARY KEY,
    score INTEGER DEFAULT 50,
    total_verified INTEGER DEFAULT 0,
    total_fake INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS premium (
    user_id INTEGER PRIMARY KEY,
    is_premium INTEGER DEFAULT 0,
    expires_at TEXT,
    granted_by TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS learning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    input_text TEXT,
    ai_response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS behavior_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    pattern_type TEXT,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()

ACHIEVEMENT_LIST = {
    "first_goal": ("First Goal", "You added your first goal."),
    "first_checkin": ("First Checkin", "You completed your first checkin."),
    "3_day_streak": ("3 Day Streak", "You kept a 3-day streak."),
    "7_day_streak": ("7 Day Streak", "You kept a 7-day streak."),
    "30_day_streak": ("30 Day Streak", "You kept a 30-day streak."),
    "goal_crusher": ("Goal Crusher", "You completed your first goal."),
    "consistency_master": ("Consistency Master", "You stayed consistent for 10 days."),
}

# ---------- user settings ----------

def save_user_name(user_id, name):
    cursor.execute(
        "INSERT INTO user_settings (user_id, name) VALUES (?, ?)"
        " ON CONFLICT(user_id) DO UPDATE SET name=excluded.name",
        (user_id, name)
    )
    conn.commit()
    save_user_profile(user_id, name=name)


def save_user_profile(user_id, **kwargs):
    existing = get_user_profile(user_id)
    if existing:
        updates = []
        values = []
        for key, value in kwargs.items():
            if key in ["name", "coaching_style", "main_goal", "reminder_time", "daily_minutes", "language"]:
                updates.append(f"{key}=?")
                values.append(value)
        if updates:
            values.append(user_id)
            cursor.execute(
                f"UPDATE user_profile SET {', '.join(updates)} WHERE user_id=?",
                tuple(values)
            )
            conn.commit()
    else:
        data = {
            "user_id": user_id,
            "name": kwargs.get("name"),
            "coaching_style": kwargs.get("coaching_style", "friendly"),
            "main_goal": kwargs.get("main_goal"),
            "reminder_time": kwargs.get("reminder_time"),
            "daily_minutes": kwargs.get("daily_minutes", 15),
            "language": kwargs.get("language", "en"),
        }
        cursor.execute(
            "INSERT INTO user_profile (user_id, name, coaching_style, main_goal, reminder_time, daily_minutes, language)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                data["user_id"],
                data["name"],
                data["coaching_style"],
                data["main_goal"],
                data["reminder_time"],
                data["daily_minutes"],
                data["language"],
            )
        )
        conn.commit()


def get_user_profile(user_id):
    cursor.execute("SELECT user_id, name, coaching_style, main_goal, created_at, reminder_time, daily_minutes, language FROM user_profile WHERE user_id=?", (user_id,))
    return cursor.fetchone()


def get_user(user_id):
    profile = get_user_profile(user_id)
    if profile:
        return profile
    cursor.execute("SELECT user_id, name, language FROM user_settings WHERE user_id=?", (user_id,))
    return cursor.fetchone()


def get_user_language(user_id):
    profile = get_user_profile(user_id)
    if profile and profile[7]:
        return profile[7]
    cursor.execute("SELECT language FROM user_settings WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return row[0] if row and row[0] else "en"

# ---------- memory ----------

def save_memory(user_id, role, message):
    cursor.execute(
        "INSERT INTO memory (user_id, role, message) VALUES (?, ?, ?)",
        (user_id, role, message)
    )
    conn.commit()


def get_memory(user_id, limit=15):
    cursor.execute(
        "SELECT role, message FROM memory WHERE user_id=? ORDER BY id DESC LIMIT ?",
        (user_id, limit)
    )
    rows = cursor.fetchall()
    return list(reversed(rows))

# ---------- goals ----------

def save_goal(user_id, text):
    cursor.execute(
        "INSERT INTO goals (user_id, text, status, progress) VALUES (?, ?, 'active', 0)",
        (user_id, text)
    )
    conn.commit()
    save_user_profile(user_id, main_goal=text)


def get_goals(user_id):
    cursor.execute(
        "SELECT id, text, status, progress, created_at FROM goals WHERE user_id=? ORDER BY created_at DESC",
        (user_id,)
    )
    return cursor.fetchall()


def delete_goal(goal_id, user_id):
    cursor.execute(
        "DELETE FROM goals WHERE id=? AND user_id=?",
        (goal_id, user_id)
    )
    conn.commit()


def mark_done(goal_id, user_id):
    cursor.execute(
        "UPDATE goals SET status='done', progress=100 WHERE id=? AND user_id=?",
        (goal_id, user_id)
    )
    conn.commit()


def get_progress(user_id):
    cursor.execute("SELECT COUNT(*) FROM goals WHERE user_id=?", (user_id,))
    total = cursor.fetchone()[0]
    if total == 0:
        return 0
    cursor.execute("SELECT COUNT(*) FROM goals WHERE user_id=? AND status='done'", (user_id,))
    done = cursor.fetchone()[0]
    return int((done / total) * 100)

# ---------- checkins and streaks ----------

def save_checkin(user_id, note):
    today = date.today().isoformat()
    cursor.execute(
        "SELECT 1 FROM daily_checkins WHERE user_id=? AND checkin_date=?",
        (user_id, today)
    )
    if cursor.fetchone():
        return False
    cursor.execute(
        "INSERT INTO daily_checkins (user_id, checkin_date, note) VALUES (?, ?, ?)",
        (user_id, today, note)
    )
    conn.commit()
    return True


def get_checkins(user_id, limit=None):
    query = "SELECT id, user_id, checkin_date, note, created_at FROM daily_checkins WHERE user_id=? ORDER BY checkin_date DESC"
    params = [user_id]
    if limit:
        query += " LIMIT ?"
        params.append(limit)
    cursor.execute(query, tuple(params))
    return cursor.fetchall()


def update_streak(user_id):
    today = date.today()
    yesterday = today - timedelta(days=1)
    cursor.execute("SELECT current_streak, longest_streak, last_active_date, total_active_days FROM streaks WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if row:
        current, longest, last_date_text, total_active = row
        last_date = date.fromisoformat(last_date_text) if last_date_text else None
        if last_date == today:
            return current, longest, total_active
        if last_date == yesterday:
            current += 1
        else:
            current = 1
        total_active += 1
        longest = max(longest, current)
        cursor.execute(
            "UPDATE streaks SET current_streak=?, longest_streak=?, last_active_date=?, total_active_days=? WHERE user_id=?",
            (current, longest, today.isoformat(), total_active, user_id)
        )
    else:
        current = 1
        longest = 1
        total_active = 1
        cursor.execute(
            "INSERT INTO streaks (user_id, current_streak, longest_streak, last_active_date, total_active_days) VALUES (?, ?, ?, ?, ?)",
            (user_id, current, longest, today.isoformat(), total_active)
        )
    conn.commit()
    return current, longest, total_active


def get_streak(user_id):
    cursor.execute("SELECT current_streak, longest_streak, total_active_days FROM streaks WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        return 0, 0, 0
    return row

# ---------- XP and achievements ----------

def get_xp(user_id):
    cursor.execute("SELECT total_xp, level FROM xp WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO xp (user_id, total_xp, level) VALUES (?, 0, 1)", (user_id,))
        conn.commit()
        return 0, 1, 100
    total_xp, level = row
    xp_to_next = 100 - (total_xp % 100)
    return total_xp, level, xp_to_next


def add_xp(user_id, amount, reason=None):
    total_xp, level, _ = get_xp(user_id)
    previous_level = level
    total_xp += amount
    level = max(1, total_xp // 100 + 1)
    cursor.execute("INSERT INTO xp_log (user_id, amount, reason) VALUES (?, ?, ?)", (user_id, amount, reason))
    cursor.execute("UPDATE xp SET total_xp=?, level=? WHERE user_id=?", (total_xp, level, user_id))
    conn.commit()
    leveled_up = level > previous_level
    return total_xp, level, leveled_up


def get_achievements(user_id):
    cursor.execute("SELECT achievement_key, achieved_at FROM achievements WHERE user_id=? ORDER BY id DESC", (user_id,))
    return cursor.fetchall()


def check_and_grant_achievements(user_id):
    achieved = {row[0] for row in get_achievements(user_id)}
    new = []

    cursor.execute("SELECT COUNT(*) FROM goals WHERE user_id=?", (user_id,))
    goals_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM daily_checkins WHERE user_id=?", (user_id,))
    checkins_count = cursor.fetchone()[0]
    cursor.execute("SELECT current_streak, longest_streak FROM streaks WHERE user_id=?", (user_id,))
    streak_row = cursor.fetchone() or (0, 0)
    current_streak, longest_streak = streak_row
    cursor.execute("SELECT COUNT(*) FROM goals WHERE user_id=? AND status='done'", (user_id,))
    done_goals = cursor.fetchone()[0]

    if goals_count >= 1 and "first_goal" not in achieved:
        new.append("first_goal")
    if checkins_count >= 1 and "first_checkin" not in achieved:
        new.append("first_checkin")
    if longest_streak >= 3 and "3_day_streak" not in achieved:
        new.append("3_day_streak")
    if longest_streak >= 7 and "7_day_streak" not in achieved:
        new.append("7_day_streak")
    if longest_streak >= 30 and "30_day_streak" not in achieved:
        new.append("30_day_streak")
    if done_goals >= 1 and "goal_crusher" not in achieved:
        new.append("goal_crusher")
    if checkins_count >= 10 and "consistency_master" not in achieved:
        new.append("consistency_master")

    for key in new:
        cursor.execute("INSERT INTO achievements (user_id, achievement_key) VALUES (?, ?)", (user_id, key))
    if new:
        conn.commit()
    return new

# ---------- trust ----------

def get_trust(user_id):
    cursor.execute("SELECT score, total_verified, total_fake FROM trust WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    if not row:
        cursor.execute("INSERT INTO trust (user_id, score, total_verified, total_fake) VALUES (?, 50, 0, 0)", (user_id,))
        conn.commit()
        return 50, 0, 0
    return row


def update_trust(user_id, change, verified=False, fake=False):
    score, total_verified, total_fake = get_trust(user_id)
    score = max(0, min(100, score + change))
    total_verified += 1 if verified else 0
    total_fake += 1 if fake else 0
    cursor.execute(
        "INSERT INTO trust (user_id, score, total_verified, total_fake) VALUES (?, ?, ?, ?)"
        " ON CONFLICT(user_id) DO UPDATE SET score=excluded.score, total_verified=excluded.total_verified, total_fake=excluded.total_fake",
        (user_id, score, total_verified, total_fake)
    )
    conn.commit()
    return score, total_verified, total_fake


def is_premium(user_id):
    cursor.execute("SELECT is_premium FROM premium WHERE user_id=?", (user_id,))
    row = cursor.fetchone()
    return bool(row and row[0] == 1)

# ---------- reminders ----------

def get_all_reminders():
    cursor.execute(
        "SELECT user_id, reminder_time, name, main_goal, daily_minutes FROM user_profile WHERE reminder_time IS NOT NULL"
    )
    rows = cursor.fetchall()
    results = []
    for user_id, reminder_time, name, main_goal, daily_minutes in rows:
        if not name:
            cursor.execute("SELECT name FROM user_settings WHERE user_id=?", (user_id,))
            setting_row = cursor.fetchone()
            name = setting_row[0] if setting_row and setting_row[0] else "Friend"
        results.append((user_id, reminder_time, name, main_goal, daily_minutes))
    return results

# ---------- learning and behavior ----------

def save_learning(user_id, input_text, ai_response):
    cursor.execute(
        "INSERT INTO learning (user_id, input_text, ai_response) VALUES (?, ?, ?)",
        (user_id, input_text, ai_response)
    )
    conn.commit()


def save_behavior(user_id, pattern_type, value):
    cursor.execute(
        "INSERT INTO behavior_patterns (user_id, pattern_type, value) VALUES (?, ?, ?)",
        (user_id, pattern_type, value)
    )
    conn.commit()


def save_mood(user_id, mood):
    cursor.execute(
        "INSERT INTO behavior_patterns (user_id, pattern_type, value) VALUES (?, 'mood', ?)",
        (user_id, mood)
    )
    conn.commit()


def get_last_mood(user_id):
    cursor.execute(
        "SELECT value FROM behavior_patterns WHERE user_id=? AND pattern_type='mood' ORDER BY created_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def get_mood_history(user_id, limit=10):
    cursor.execute(
        "SELECT value, created_at FROM behavior_patterns WHERE user_id=? AND pattern_type='mood' ORDER BY created_at DESC LIMIT ?",
        (user_id, limit)
    )
    return cursor.fetchall()


def get_active_goal(user_id):
    cursor.execute(
        "SELECT id, text FROM goals WHERE user_id=? AND status='active' ORDER BY created_at ASC LIMIT 1",
        (user_id,)
    )
    return cursor.fetchone()


def get_recent_checkins(user_id, days=7):
    cursor.execute(
        "SELECT COUNT(*) FROM daily_checkins WHERE user_id=? AND checkin_date >= date('now', ?)",
        (user_id, f'-{days-1} days')
    )
    return cursor.fetchone()[0]


def get_consistency_score(user_id, days=7):
    count = get_recent_checkins(user_id, days)
    return int((count / days) * 100)


def get_weekly_summary(user_id):
    weekly_checkins = get_recent_checkins(user_id, 7)
    active_goals = [g for g in get_goals(user_id) if g[2] == 'active']
    done_goals = [g for g in get_goals(user_id) if g[2] == 'done']
    current, longest, total = get_streak(user_id)
    progress = get_progress(user_id)
    return {
        'weekly_checkins': weekly_checkins,
        'active_goals': len(active_goals),
        'done_goals': len(done_goals),
        'current_streak': current,
        'longest_streak': longest,
        'consistency_score': get_consistency_score(user_id, 7),
        'progress': progress,
    }


def get_monthly_summary(user_id):
    monthly_checkins = get_recent_checkins(user_id, 30)
    active_goals = [g for g in get_goals(user_id) if g[2] == 'active']
    done_goals = [g for g in get_goals(user_id) if g[2] == 'done']
    current, longest, total = get_streak(user_id)
    progress = get_progress(user_id)
    return {
        'monthly_checkins': monthly_checkins,
        'active_goals': len(active_goals),
        'done_goals': len(done_goals),
        'current_streak': current,
        'longest_streak': longest,
        'consistency_score': get_consistency_score(user_id, 30),
        'progress': progress,
    }


def get_user_rank_score(user_id):
    total_xp, level, _ = get_xp(user_id)
    current, longest, _ = get_streak(user_id)
    trust_score, _, _ = get_trust(user_id)
    return int(total_xp + current * 20 + trust_score * 2)


def get_rank(user_id):
    cursor.execute(
        "SELECT xp.user_id, xp.total_xp, COALESCE(streaks.current_streak, 0), COALESCE(trust.score, 50) "
        "FROM xp "
        "LEFT JOIN streaks ON xp.user_id = streaks.user_id "
        "LEFT JOIN trust ON xp.user_id = trust.user_id"
    )
    rows = cursor.fetchall()
    scores = []
    for uid, total_xp, current_streak, trust_score in rows:
        score = int(total_xp + current_streak * 20 + trust_score * 2)
        scores.append((uid, score))
    scores.sort(key=lambda item: item[1], reverse=True)
    rank = 1
    for idx, (uid, score) in enumerate(scores, start=1):
        if uid == user_id:
            rank = idx
            break
    return rank, len(scores), next((score for uid, score in scores if uid == user_id), 0)


def get_hall_of_fame(limit=5):
    cursor.execute(
        "SELECT xp.user_id, xp.total_xp, COALESCE(streaks.current_streak, 0), COALESCE(trust.score, 50) "
        "FROM xp "
        "LEFT JOIN streaks ON xp.user_id = streaks.user_id "
        "LEFT JOIN trust ON xp.user_id = trust.user_id"
    )
    rows = cursor.fetchall()
    scores = []
    for uid, total_xp, current_streak, trust_score in rows:
        score = int(total_xp + current_streak * 20 + trust_score * 2)
        name = None
        cursor.execute("SELECT name FROM user_profile WHERE user_id=?", (uid,))
        row = cursor.fetchone()
        if row and row[0]:
            name = row[0]
        else:
            cursor.execute("SELECT name FROM user_settings WHERE user_id=?", (uid,))
            row2 = cursor.fetchone()
            name = row2[0] if row2 and row2[0] else f"User {uid}"
        scores.append((uid, name, score))
    scores.sort(key=lambda item: item[2], reverse=True)
    return scores[:limit]


def get_last_checkin_date(user_id):
    cursor.execute(
        "SELECT checkin_date FROM daily_checkins WHERE user_id=? ORDER BY checkin_date DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    return row[0] if row else None


def get_inactivity_days(user_id):
    last_checkin = get_last_checkin_date(user_id)
    if not last_checkin:
        return None
    last = date.fromisoformat(last_checkin)
    delta = date.today() - last
    return delta.days


def get_total_users():
    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM user_profile")
    return cursor.fetchone()[0] or 0


def get_active_users_last_days(days=7):
    cursor.execute(
        "SELECT COUNT(DISTINCT user_id) FROM daily_checkins WHERE checkin_date >= date('now', ?)",
        (f'-{days-1} days',)
    )
    return cursor.fetchone()[0] or 0


def get_average_streak():
    cursor.execute("SELECT AVG(current_streak) FROM streaks")
    row = cursor.fetchone()
    return int(row[0]) if row and row[0] else 0


def get_completed_goals_count():
    cursor.execute("SELECT COUNT(*) FROM goals WHERE status='done'")
    return cursor.fetchone()[0] or 0


def get_language_distribution():
    cursor.execute("SELECT language, COUNT(*) FROM user_profile GROUP BY language")
    return cursor.fetchall()


def get_top_goals(limit=5):
    cursor.execute(
        "SELECT text, COUNT(*) as count FROM goals GROUP BY text ORDER BY count DESC LIMIT ?",
        (limit,)
    )
    return cursor.fetchall()


def get_founder_dashboard():
    return {
        'total_users': get_total_users(),
        'weekly_active': get_active_users_last_days(7),
        'monthly_active': get_active_users_last_days(30),
        'average_streak': get_average_streak(),
        'completed_goals': get_completed_goals_count(),
        'language_distribution': get_language_distribution(),
        'top_goals': get_top_goals(5),
    }
