from database import is_premium


def format_premium_text(user_id):
    if is_premium(user_id):
        return (
            "💎 You are Premium!\n\n"
            "✅ Advanced coaching\n"
            "✅ Detailed reports\n"
            "✅ Priority responses"
        )
    return (
        "💎 GoalForge Premium\n\n"
        "How to get it:\n"
        "🏆 Reach Level 10\n"
        "🏅 Unlock 5 achievements\n"
        "🔥 30-day streak\n\n"
        "Keep going!"
    )
