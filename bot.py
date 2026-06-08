import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from dotenv import load_dotenv

from coach import get_welcome_message, forge_goal_discovery
from database import (
    save_memory, save_user_name, save_goal, get_goals, get_user_profile,
    save_user_profile, update_streak, get_streak, save_checkin, get_checkins,
    add_xp, get_xp, check_and_grant_achievements, get_achievements,
    get_trust, update_trust, is_premium, ACHIEVEMENT_LIST
)
from scheduler import send_reminders, send_weekly_report

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN is missing in .env file")

WAITING_GOAL = 1
WAITING_STYLE = 2
WAITING_REMINDER_TIME = 3
WAITING_REMINDER_MINUTES = 4
WAITING_CHECKIN = 5


def get_level_title(level):
    if level >= 10: return "🏆 Grand Master"
    elif level >= 7: return "👑 Legend"
    elif level >= 5: return "🔥 Elite"
    elif level >= 3: return "💪 Warrior"
    elif level >= 2: return "🗺 Explorer"
    return "🌱 Seed"


async def notify_achievements(update, new_achievements):
    for key in new_achievements:
        name, desc = ACHIEVEMENT_LIST.get(key, (key, ""))
        await update.message.reply_text(f"🏅 Achievement باز شد!\n\n{name}\n{desc}")


# =========================
# /start
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.first_name or "دوست"
    save_user_name(user.id, user_name)
    save_memory(user.id, "user", "/start")
    msg = get_welcome_message(user_name)
    save_memory(user.id, "bot", msg)
    await update.message.reply_text(msg)


# =========================
# /goal
# =========================
async def goal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 هدف جدیدت رو بنویس:\n\n"
        "مثال: میخوام در ۳ ماه زبان انگلیسی یاد بگیرم"
    )
    return WAITING_GOAL


async def goal_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    goal_text = update.message.text
    save_goal(user_id, goal_text)
    save_memory(user_id, "user", f"هدف جدید: {goal_text}")
    total_xp, level, leveled_up = add_xp(user_id, 10, "new_goal")
    new_achievements = check_and_grant_achievements(user_id)

    response = (
        f"✅ هدفت ثبت شد:\n«{goal_text}»\n\n"
        f"🔥 Forge این هدف رو دنبال میکنه.\n"
        f"⭐ +10 XP"
    )
    save_memory(user_id, "bot", response)
    await update.message.reply_text(response)
    await notify_achievements(update, new_achievements)
    return ConversationHandler.END


# =========================
# /goals
# =========================
async def goals_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    goals = get_goals(user_id)
    if not goals:
        await update.message.reply_text("هنوز هدفی ثبت نکردی.\nاز /goal استفاده کن.")
        return
    msg = "🎯 هدف‌های فعال تو:\n\n"
    for i, (gid, text, status, progress, created) in enumerate(goals, 1):
        msg += f"{i}. {text}\n   📊 پیشرفت: {progress}%\n\n"
    await update.message.reply_text(msg)


# =========================
# /profile
# =========================
async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)
    if not profile:
        await update.message.reply_text("پروفایلت هنوز کامل نشده. /start بزن.")
        return

    name, style, main_goal, created, reminder_time, daily_minutes = profile
    styles = {"friendly": "دوستانه 😊", "strict": "سخت‌گیر 💪", "military": "نظامی ⚔️",
              "mentor": "مربی 🧠", "professional": "حرفه‌ای 📊"}
    total_xp, level, xp_to_next = get_xp(user_id)
    current, longest, total_days = get_streak(user_id)
    trust_score, _, _ = get_trust(user_id)
    premium = "✅ Premium" if is_premium(user_id) else "❌ Free"

    await update.message.reply_text(
        f"👤 پروفایل تو:\n\n"
        f"اسم: {name or '—'}\n"
        f"سبک: {styles.get(style, style)}\n"
        f"هدف: {main_goal or 'ثبت نشده'}\n"
        f"یادآوری: {reminder_time or 'تنظیم نشده'}\n"
        f"وقت روزانه: {daily_minutes or 15} دقیقه\n\n"
        f"⭐ XP: {total_xp} | Level {level} — {get_level_title(level)}\n"
        f"🔥 Streak: {current} روز | رکورد: {longest}\n"
        f"🛡 Trust: {trust_score}/100\n"
        f"💎 {premium}\n\n"
        f"/style | /goal | /reminder | /xp | /achievements"
    )


# =========================
# /style
# =========================
async def style_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["😊 دوستانه", "💪 سخت‌گیر"], ["⚔️ نظامی", "🧠 مربی"], ["📊 حرفه‌ای"]]
    await update.message.reply_text("سبک کوچینگ Forge رو انتخاب کن:",
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return WAITING_STYLE


async def style_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    style_map = {"😊 دوستانه": "friendly", "💪 سخت‌گیر": "strict",
                 "⚔️ نظامی": "military", "🧠 مربی": "mentor", "📊 حرفه‌ای": "professional"}
    style = style_map.get(update.message.text, "friendly")
    save_user_profile(user_id, coaching_style=style)
    await update.message.reply_text(f"✅ سبک کوچینگ تغییر کرد به: {update.message.text}",
        reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# =========================
# /reminder
# =========================
async def reminder_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏰ چه ساعتی Forge بهت پیام بده؟\n\nفرمت: HH:MM\nمثال: 21:30")
    return WAITING_REMINDER_TIME


async def reminder_time_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    time_text = update.message.text.strip()
    try:
        parts = time_text.split(":")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59): raise ValueError()
        formatted = f"{hour:02d}:{minute:02d}"
    except:
        await update.message.reply_text("❌ فرمت اشتباهه! مثال: 08:00")
        return WAITING_REMINDER_TIME
    context.user_data["reminder_time"] = formatted
    await update.message.reply_text(f"✅ ساعت {formatted} ثبت شد.\n\nروزانه چند دقیقه وقت داری؟\nمثال: 15 یا 30")
    return WAITING_REMINDER_MINUTES


async def reminder_minutes_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        minutes = int(update.message.text.strip())
        if not (5 <= minutes <= 480): raise ValueError()
    except:
        await update.message.reply_text("❌ عدد اشتباهه! بین ۵ تا ۴۸۰ بنویس.")
        return WAITING_REMINDER_MINUTES
    reminder_time = context.user_data.get("reminder_time")
    save_user_profile(user_id, reminder_time=reminder_time, daily_minutes=minutes)
    await update.message.reply_text(
        f"🔥 یادآوری تنظیم شد!\n⏰ ساعت: {reminder_time}\n⏱ مدت: {minutes} دقیقه"
    )
    return ConversationHandler.END


# =========================
# /checkin
# =========================
async def checkin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ چک‌این روزانه\n\nامروز چیکار کردی؟ بنویس:")
    return WAITING_CHECKIN


async def checkin_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    note = update.message.text
    saved = save_checkin(user_id, note)
    update_streak(user_id)
    current, longest, total = get_streak(user_id)

    if saved:
        xp_amount = 30 if current >= 7 else 25 if current >= 3 else 20
        total_xp, level, leveled_up = add_xp(user_id, xp_amount, "daily_checkin")
        update_trust(user_id, +2)
        new_achievements = check_and_grant_achievements(user_id)

        msg = (
            f"✅ چک‌این ثبت شد!\n\n"
            f"📝 «{note}»\n\n"
            f"🔥 Streak: {current} روز\n"
            f"⭐ +{xp_amount} XP (مجموع: {total_xp})\n"
            f"🏅 Level: {level} — {get_level_title(level)}"
        )
        if leveled_up:
            msg += f"\n\n🎉 Level Up! به Level {level} رسیدی!"

        await update.message.reply_text(msg)
        await notify_achievements(update, new_achievements)
    else:
        total_xp, level, _ = get_xp(user_id)
        await update.message.reply_text(
            f"امروز قبلاً چک‌این کردی! ✅\n\n"
            f"🔥 Streak: {current} روز | ⭐ XP: {total_xp}"
        )
    return ConversationHandler.END


# =========================
# /streak
# =========================
async def streak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current, longest, total = get_streak(user_id)
    if current == 0:
        await update.message.reply_text("هنوز streak نداری!\nهر روز /checkin بزن تا شروع بشه. 🔥")
        return
    emoji = "🏆" if current >= 30 else "🔥" if current >= 14 else "⚡" if current >= 7 else "✅"
    await update.message.reply_text(
        f"{emoji} Streak تو:\n\n"
        f"🔥 فعلی: {current} روز متوالی\n"
        f"🏆 رکورد: {longest} روز\n"
        f"📅 کل روزهای فعال: {total} روز"
    )


# =========================
# /xp
# =========================
async def xp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    total_xp, level, xp_to_next = get_xp(user_id)
    current, _, _ = get_streak(user_id)
    xp_in_level = total_xp % 100
    bar = "█" * (xp_in_level // 10) + "░" * (10 - xp_in_level // 10)
    await update.message.reply_text(
        f"⭐ وضعیت XP:\n\n"
        f"🏅 Level {level} — {get_level_title(level)}\n"
        f"[{bar}] {xp_in_level}/100\n"
        f"✨ مجموع: {total_xp} XP\n"
        f"🎯 تا Level بعدی: {xp_to_next} XP\n"
        f"🔥 Streak: {current} روز\n\n"
        f"💡 /checkin = 20-30 XP\n"
        f"💡 /goal جدید = 10 XP"
    )


# =========================
# /achievements
# =========================
async def achievements_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    achieved = get_achievements(user_id)

    if not achieved:
        await update.message.reply_text(
            "هنوز Achievement نداری!\n\n"
            "برای شروع:\n"
            "• /goal بزن → 🎯 Goal Setter\n"
            "• /checkin بزن → ✅ First Checkin\n"
            "• ۳ روز متوالی فعال باش → ⚡ 3 Day Streak"
        )
        return

    msg = f"🏅 Achievements تو ({len(achieved)} تا):\n\n"
    for key, achieved_at in achieved:
        name, desc = ACHIEVEMENT_LIST.get(key, (key, ""))
        msg += f"{name}\n   {desc}\n\n"

    total = len(ACHIEVEMENT_LIST)
    msg += f"📊 {len(achieved)} از {total} باز شده"
    await update.message.reply_text(msg)


# =========================
# /trust
# =========================
async def trust_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score, verified, fake = get_trust(user_id)

    if score >= 80: label = "🟢 خیلی خوب"
    elif score >= 60: label = "🟡 خوب"
    elif score >= 40: label = "🟠 متوسط"
    else: label = "🔴 ضعیف"

    await update.message.reply_text(
        f"🛡 Trust Score تو:\n\n"
        f"امتیاز: {score}/100 — {label}\n\n"
        f"Trust Score با:\n"
        f"✅ چک‌این روزانه: +2\n"
        f"🎯 تکمیل هدف: +5\n"
        f"❌ بی‌فعالیت: -1 در روز\n\n"
        f"Trust Score بالا = رتبه بهتر در Rank"
    )


# =========================
# /report
# =========================
async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)
    name = profile[0] if profile else "دوست"
    await send_weekly_report(context.application, user_id, name)


# =========================
# /premium
# =========================
async def premium_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_premium(user_id):
        await update.message.reply_text(
            "💎 تو Premium هستی!\n\n"
            "✅ کوچینگ پیشرفته\n"
            "✅ گزارش تفصیلی\n"
            "✅ اولویت پاسخ"
        )
    else:
        await update.message.reply_text(
            "💎 GoalForge Premium\n\n"
            "راه‌های دریافت:\n"
            "🏆 رسیدن به Level 10\n"
            "🏅 باز کردن ۵ Achievement\n"
            "🔥 Streak 30 روزه\n\n"
            "به تلاشت ادامه بده!"
        )


# =========================
# /status
# =========================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 GoalForge آنلاین است.")


# =========================
# /help
# =========================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📌 دستورات GoalForge:\n\n"
        "🎯 هدف‌ها:\n"
        "/goal — هدف جدید\n"
        "/goals — لیست هدف‌ها\n\n"
        "📊 پیشرفت:\n"
        "/checkin — چک‌این روزانه\n"
        "/streak — وضعیت streak\n"
        "/xp — XP و Level\n"
        "/achievements — دستاوردها\n"
        "/trust — Trust Score\n"
        "/report — گزارش هفتگی\n\n"
        "⚙️ تنظیمات:\n"
        "/profile — پروفایل من\n"
        "/style — سبک کوچینگ\n"
        "/reminder — یادآوری روزانه\n"
        "/premium — وضعیت Premium\n\n"
        "یا فقط پیام بده، Forge جواب میده 🔥"
    )


# =========================
# Main message handler
# =========================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text

    save_memory(user_id, "user", user_text)
    update_streak(user_id)

    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    response = forge_goal_discovery(user_text, user_id)
    save_memory(user_id, "bot", response)

    new_achievements = check_and_grant_achievements(user_id)
    await update.message.reply_text(response)
    await notify_achievements(update, new_achievements)


# =========================
# Cancel
# =========================
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لغو شد.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


# =========================
# Post init
# =========================
async def post_init(app):
    asyncio.create_task(send_reminders(app))


# =========================
# App setup
# =========================
app = Application.builder().token(TOKEN).post_init(post_init).build()

goal_conv = ConversationHandler(
    entry_points=[CommandHandler("goal", goal_cmd)],
    states={WAITING_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, goal_received)]},
    fallbacks=[CommandHandler("cancel", cancel)]
)
style_conv = ConversationHandler(
    entry_points=[CommandHandler("style", style_cmd)],
    states={WAITING_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, style_received)]},
    fallbacks=[CommandHandler("cancel", cancel)]
)
reminder_conv = ConversationHandler(
    entry_points=[CommandHandler("reminder", reminder_cmd)],
    states={
        WAITING_REMINDER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_time_received)],
        WAITING_REMINDER_MINUTES: [MessageHandler(filters.TEXT & ~filters.COMMAND, reminder_minutes_received)],
    },
    fallbacks=[CommandHandler("cancel", cancel)]
)
checkin_conv = ConversationHandler(
    entry_points=[CommandHandler("checkin", checkin_cmd)],
    states={WAITING_CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkin_received)]},
    fallbacks=[CommandHandler("cancel", cancel)]
)

app.add_handler(reminder_conv)
app.add_handler(style_conv)
app.add_handler(checkin_conv)
app.add_handler(goal_conv)
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("goals", goals_list))
app.add_handler(CommandHandler("profile", profile_cmd))
app.add_handler(CommandHandler("streak", streak_cmd))
app.add_handler(CommandHandler("xp", xp_cmd))
app.add_handler(CommandHandler("achievements", achievements_cmd))
app.add_handler(CommandHandler("trust", trust_cmd))
app.add_handler(CommandHandler("report", report_cmd))
app.add_handler(CommandHandler("premium", premium_cmd))
app.add_handler(CommandHandler("status", status))
app.add_handler(CommandHandler("help", help_cmd))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🔥 GoalForge Bot Running...")
app.run_polling()
