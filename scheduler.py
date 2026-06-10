import asyncio
from datetime import datetime
from database import (
    get_all_reminders, get_streak, get_checkins, get_goals,
    get_active_goal, get_last_mood, get_inactivity_days
)


async def send_reminders(app):
    while True:
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        weekday = now.weekday()
        day_of_month = now.day

        users = get_all_reminders()

        for user_id, reminder_time, name, main_goal, daily_minutes in users:
            if reminder_time == time_str:
                await send_daily_briefing(app, user_id, name, main_goal, daily_minutes)
                inactivity_days = get_inactivity_days(user_id)
                if inactivity_days is not None and inactivity_days >= 3:
                    await send_inactivity_recovery(app, user_id, name, inactivity_days)
            if weekday == 4 and time_str == "20:00":
                await send_weekly_report(app, user_id, name)
            if day_of_month == 1 and time_str == "20:00":
                await send_monthly_review(app, user_id, name)

        await asyncio.sleep(60)


async def send_daily_briefing(app, user_id, name, main_goal, daily_minutes):
    goal_text = main_goal or "your main goal"
    minutes = daily_minutes or 15
    current, longest, total = get_streak(user_id)
    mood = get_last_mood(user_id) or "not recorded"

    streak_msg = ""
    if current >= 7:
        streak_msg = f"🔥 Streak: {current} days — amazing!\n"
    elif current > 0:
        streak_msg = f"⚡ Streak: {current} days — keep going!\n"

    msg = (
        f"☀️ Good morning, {name}!\n\n"
        f"🎯 Today’s focus: {goal_text}\n"
        f"💬 Mood: {mood}\n"
        f"⏱ Suggested practice: {minutes} min\n"
        f"{streak_msg}"
        f"💡 Quick task: Spend 10 minutes toward your goal now.\n"
        f"When you finish, share with /checkin"
    )

    try:
        await app.bot.send_message(chat_id=user_id, text=msg)
        print(f"[DAILY BRIEFING] Sent to {user_id}")
    except Exception as e:
        print(f"[BRIEFING ERROR] {user_id}: {e}")


async def send_inactivity_recovery(app, user_id, name, inactivity_days):
    msg = (
        f"⏳ Hi {name}, I noticed you haven't checked in for {inactivity_days} days.\n"
        f"Let's make today easy:\n"
        f"✅ Write one sentence about what you want to do next.\n"
        f"✅ After that, send /checkin."
    )
    try:
        await app.bot.send_message(chat_id=user_id, text=msg)
        print(f"[RECOVERY] Sent to {user_id}")
    except Exception as e:
        print(f"[RECOVERY ERROR] {user_id}: {e}")


async def send_monthly_review(app, user_id, name):
    try:
        current, longest, total = get_streak(user_id)
        checkins = get_checkins(user_id, limit=30)
        goals = get_goals(user_id)
        active_goal = goals[0][1] if goals else "Not set"
        checkin_count = len(checkins)

        rating = "🏆 Excellent" if checkin_count >= 20 else "🔥 Good" if checkin_count >= 12 else "⚡ Average"

        msg = (
            f"📅 Monthly Review — {name}\n"
            f"{'='*25}\n\n"
            f"🎯 Goal: {active_goal}\n\n"
            f"📅 Check-ins this month: {checkin_count}/30\n"
            f"🔥 Current Streak: {current} days\n"
            f"🏆 Longest Streak: {longest} days\n"
            f"📆 Total Active Days: {total}\n\n"
            f"Performance: {rating}\n\n"
        )
        if checkin_count < 10:
            msg += "💡 Next month, aim for 10 small check-ins. Start with 5 minutes."
        else:
            msg += "💡 Great month! Keep this momentum and build a small habit."

        await app.bot.send_message(chat_id=user_id, text=msg)
        print(f"[MONTHLY REVIEW] Sent to {user_id}")
    except Exception as e:
        print(f"[MONTHLY REVIEW ERROR] {user_id}: {e}")


async def send_weekly_report(app, user_id, name):
    try:
        current, longest, total = get_streak(user_id)
        checkins = get_checkins(user_id, limit=7)
        goals = get_goals(user_id)

        checkin_count = len(checkins)
        active_goal = goals[0][1] if goals else "Not set"

        if checkin_count >= 6:
            rating = "🏆 Excellent"
        elif checkin_count >= 4:
            rating = "🔥 Good"
        elif checkin_count >= 2:
            rating = "⚡ Average"
        else:
            rating = "⚠️ Needs improvement"

        msg = (
            f"📊 Weekly Report — {name}\n"
            f"{'='*25}\n\n"
            f"🎯 Goal: {active_goal}\n\n"
            f"📅 Check-ins this week: {checkin_count}/7\n"
            f"🔥 Current Streak: {current} days\n"
            f"🏆 Longest Streak: {longest} days\n"
            f"📆 Total Active Days: {total}\n\n"
            f"Performance: {rating}\n\n"
        )

        if checkin_count < 3:
            msg += "💡 Try to /checkin every day next week."
        else:
            msg += "💡 Great week! Keep this momentum."

        await app.bot.send_message(chat_id=user_id, text=msg)
        print(f"[WEEKLY REPORT] Sent to {user_id}")
    except Exception as e:
        print(f"[WEEKLY REPORT ERROR] {user_id}: {e}")
