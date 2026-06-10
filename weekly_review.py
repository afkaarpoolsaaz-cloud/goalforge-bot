from database import get_weekly_summary, get_active_goal


def format_weekly_review(user_id):
    summary = get_weekly_summary(user_id)
    active_goal = get_active_goal(user_id)
    goal_text = active_goal[1] if active_goal else "No active goal"
    return (
        f"📅 Weekly Review:\n\n"
        f"🎯 Active goal: {goal_text}\n"
        f"🔥 Streak: {summary['current_streak']} days\n"
        f"🏆 Best streak: {summary['longest_streak']} days\n"
        f"✅ Checkins: {summary['weekly_checkins']}/7\n"
        f"📊 Progress: {summary['progress']}%\n"
        f"💪 Consistency: {summary['consistency_score']}%\n"
    )
