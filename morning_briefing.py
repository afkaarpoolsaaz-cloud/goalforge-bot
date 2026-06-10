from database import get_weekly_summary, get_last_mood, get_active_goal


def format_morning_briefing(user_id):
    active_goal = get_active_goal(user_id)
    goal_text = active_goal[1] if active_goal else "No active goal"
    last_mood = get_last_mood(user_id) or "Not set"
    summary = get_weekly_summary(user_id)
    return (
        f"☀️ Smart Briefing:\n\n"
        f"🎯 Today’s focus: {goal_text}\n"
        f"🔥 Current streak: {summary['current_streak']} days\n"
        f"📊 Weekly consistency: {summary['consistency_score']}%\n"
        f"✅ Checkins this week: {summary['weekly_checkins']}/7\n"
        f"💬 Last mood: {last_mood}\n"
        f"⚡ Quick task: Spend 10 minutes on your main goal today."
    )
