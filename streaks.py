from database import get_streak


def format_streak_text(user_id):
    current, longest, total = get_streak(user_id)
    if current == 0:
        return "No streak yet!\nUse /checkin every day to start. 🔥"
    emoji = "🏆" if current >= 30 else "🔥" if current >= 14 else "⚡" if current >= 7 else "✅"
    return f"{emoji} Streak:\n\n🔥 Current: {current} days\n🏆 Best: {longest} days\n📅 Total active: {total} days"
