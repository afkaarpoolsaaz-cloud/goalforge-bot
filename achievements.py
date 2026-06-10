from database import get_achievements, ACHIEVEMENT_LIST


def format_achievements_text(user_id):
    achieved = get_achievements(user_id)
    if not achieved:
        return (
            "No achievements yet!\n\n"
            "• /goal → 🎯 Goal Setter\n"
            "• /checkin → ✅ First Checkin\n"
            "• 3 days active → ⚡ 3 Day Streak"
        )
    msg = f"🏅 Achievements ({len(achieved)}):\n\n"
    for key, achieved_at in achieved:
        name, desc = ACHIEVEMENT_LIST.get(key, (key, ""))
        msg += f"{name}\n   {desc}\n\n"
    msg += f"📊 {len(achieved)} of {len(ACHIEVEMENT_LIST)} unlocked"
    return msg


def format_achievement_notification(key):
    name, desc = ACHIEVEMENT_LIST.get(key, (key, ""))
    return f"🏅 Achievement!\n\n{name}\n{desc}"
