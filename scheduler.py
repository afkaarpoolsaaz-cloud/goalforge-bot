import asyncio
from datetime import datetime, date, timedelta
from database import get_all_reminders, get_streak, get_checkins, get_goals


async def send_reminders(app):
    """Check every minute - send daily reminders and weekly reports"""
    while True:
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        weekday = now.weekday()  # 0=Monday, 6=Sunday

        users = get_all_reminders()

        for user_id, reminder_time, name, main_goal, daily_minutes in users:

            # Daily reminder
            if reminder_time == time_str:
                await send_daily_reminder(app, user_id, name, main_goal, daily_minutes)

            # Weekly report - every Friday at 20:00 (or any day at reminder time if Friday)
            if weekday == 4 and time_str == "20:00":
                await send_weekly_report(app, user_id, name)

        await asyncio.sleep(60)


async def send_daily_reminder(app, user_id, name, main_goal, daily_minutes):
    goal_text = main_goal or "هدفت"
    minutes = daily_minutes or 15

    current, longest, total = get_streak(user_id)

    streak_msg = ""
    if current >= 7:
        streak_msg = f"🔥 Streak: {current} روز متوالی — عالیه!\n"
    elif current > 0:
        streak_msg = f"⚡ Streak: {current} روز — ادامه بده!\n"

    msg = (
        f"🔥 {name}، وقت Forge هست!\n\n"
        f"🎯 هدف: {goal_text}\n"
        f"⏱ امروز {minutes} دقیقه وقت داری\n"
        f"{streak_msg}\n"
        f"امروز چیکار کردی؟ /checkin بزن و بگو."
    )

    try:
        await app.bot.send_message(chat_id=user_id, text=msg)
        print(f"[REMINDER] Sent to {user_id} ({name})")
    except Exception as e:
        print(f"[REMINDER ERROR] {user_id}: {e}")


async def send_weekly_report(app, user_id, name):
    try:
        current, longest, total = get_streak(user_id)
        checkins = get_checkins(user_id, limit=7)
        goals = get_goals(user_id)

        checkin_count = len(checkins)
        active_goal = goals[0][1] if goals else "ثبت نشده"

        # Performance rating
        if checkin_count >= 6:
            rating = "🏆 عالی"
        elif checkin_count >= 4:
            rating = "🔥 خوب"
        elif checkin_count >= 2:
            rating = "⚡ متوسط"
        else:
            rating = "⚠️ ضعیف"

        msg = (
            f"📊 گزارش هفتگی — {name}\n"
            f"{'='*25}\n\n"
            f"🎯 هدف: {active_goal}\n\n"
            f"📅 چک‌این این هفته: {checkin_count} از ۷ روز\n"
            f"🔥 Streak فعلی: {current} روز\n"
            f"🏆 رکورد Streak: {longest} روز\n"
            f"📆 کل روزهای فعال: {total} روز\n\n"
            f"عملکرد این هفته: {rating}\n\n"
        )

        if checkin_count < 3:
            msg += "💡 هفته بعد سعی کن هر روز /checkin بزنی."
        else:
            msg += "💡 هفته خوبی داشتی! همین روند رو ادامه بده."

        await app.bot.send_message(chat_id=user_id, text=msg)
        print(f"[WEEKLY REPORT] Sent to {user_id} ({name})")
    except Exception as e:
        print(f"[WEEKLY REPORT ERROR] {user_id}: {e}")
