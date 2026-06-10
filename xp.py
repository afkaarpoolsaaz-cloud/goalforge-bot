from database import get_xp, get_streak


def progress_bar(percentage):
    filled = int(max(0, min(100, percentage)) / 10)
    return "█" * filled + "░" * (10 - filled)


def format_xp_text(user_id, lang, get_level_title):
    total_xp, level, xp_to_next = get_xp(user_id)
    current, _, _ = get_streak(user_id)
    xp_in_level = total_xp % 100
    bar = progress_bar(xp_in_level)
    return (
        f"⭐ XP Status:\n\n"
        f"🏅 Level {level} — {get_level_title(level, lang)}\n"
        f"[{bar}] {xp_in_level}/100\n"
        f"✨ Total: {total_xp} XP\n"
        f"🎯 To next level: {xp_to_next} XP\n"
        f"🔥 Streak: {current} days\n\n"
        f"💡 /checkin = 20-30 XP\n"
        f"💡 /goal = 10 XP"
    )
