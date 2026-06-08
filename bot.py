import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from dotenv import load_dotenv

from coach import get_welcome_message, forge_goal_discovery
from database import (
    save_memory, save_user_name, save_goal, get_goals, get_user_profile,
    save_user_profile, update_streak, get_streak, save_checkin, get_checkins,
    add_xp, get_xp, check_and_grant_achievements, get_achievements,
    get_trust, update_trust, is_premium, get_user_language, ACHIEVEMENT_LIST
)
from scheduler import send_reminders, send_weekly_report
from lang import LANGUAGES, STYLE_BUTTONS, STYLE_MAP, t

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise Exception("BOT_TOKEN is missing in .env file")

WAITING_LANGUAGE = 1
WAITING_GOAL = 2
WAITING_STYLE = 3
WAITING_REMINDER_TIME = 4
WAITING_REMINDER_MINUTES = 5
WAITING_CHECKIN = 6


def get_level_title(level, lang="en"):
    titles = {
        "en": ["🌱 Seed", "🗺 Explorer", "💪 Warrior", "💪 Warrior", "🔥 Elite", "🔥 Elite", "👑 Legend", "👑 Legend", "🏆 Grand Master"],
        "fa": ["🌱 دانه", "🗺 کاشف", "💪 جنگجو", "💪 جنگجو", "🔥 نخبه", "🔥 نخبه", "👑 افسانه", "👑 افسانه", "🏆 استاد بزرگ"],
        "ru": ["🌱 Семя", "🗺 Исследователь", "💪 Воин", "💪 Воин", "🔥 Элита", "🔥 Элита", "👑 Легенда", "👑 Легенда", "🏆 Гроссмейстер"],
        "de": ["🌱 Samen", "🗺 Entdecker", "💪 Krieger", "💪 Krieger", "🔥 Elite", "🔥 Elite", "👑 Legende", "👑 Legende", "🏆 Großmeister"],
        "tr": ["🌱 Tohum", "🗺 Kaşif", "💪 Savaşçı", "💪 Savaşçı", "🔥 Elit", "🔥 Elit", "👑 Efsane", "👑 Efsane", "🏆 Grandmaster"],
    }
    t_list = titles.get(lang, titles["en"])
    idx = min(level - 1, len(t_list) - 1)
    return t_list[idx]


async def notify_achievements(update, new_achievements, lang):
    for key in new_achievements:
        name, desc = ACHIEVEMENT_LIST.get(key, (key, ""))
        await update.message.reply_text(f"🏅 Achievement!\n\n{name}\n{desc}")


def main_menu_keyboard(lang):
    buttons = [
        [KeyboardButton("/goal"), KeyboardButton("/goals")],
        [KeyboardButton("/checkin"), KeyboardButton("/streak")],
        [KeyboardButton("/xp"), KeyboardButton("/achievements")],
        [KeyboardButton("/profile"), KeyboardButton("/report")],
        [KeyboardButton("/reminder"), KeyboardButton("/style")],
        [KeyboardButton("/help")],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


# =========================
# /start - language select
# =========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_buttons = []
    langs = list(LANGUAGES.items())
    for i in range(0, len(langs), 2):
        row = [langs[i][1]]
        if i + 1 < len(langs):
            row.append(langs[i+1][1])
        lang_buttons.append(row)

    markup = ReplyKeyboardMarkup(lang_buttons, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌍 Choose your language / زبانت رو انتخاب کن:", reply_markup=markup)
    return WAITING_LANGUAGE


async def language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_name = user.first_name or "Friend"
    chosen = update.message.text

    # Find language code
    lang_code = "en"
    for code, label in LANGUAGES.items():
        if label == chosen:
            lang_code = code
            break

    save_user_name(user.id, user_name)
    save_user_profile(user.id, language=lang_code)
    save_memory(user.id, "user", "/start")

    welcome = t("welcome", lang_code, name=user_name)
    commands = t("commands_title", lang_code) + t("commands_body", lang_code, name=user_name) if lang_code in ["fa", "en", "ru", "de", "tr"] else t("commands_title", lang_code)

    full_msg = welcome + "\n\n" + commands
    save_memory(user.id, "bot", welcome)

    await update.message.reply_text(full_msg, reply_markup=main_menu_keyboard(lang_code), parse_mode="Markdown")
    return ConversationHandler.END


# =========================
# /goal
# =========================
async def goal_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update.effective_user.id)
    await update.message.reply_text(t("goal_prompt", lang))
    return WAITING_GOAL


async def goal_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    goal_text = update.message.text

    save_goal(user_id, goal_text)
    save_memory(user_id, "user", f"Goal: {goal_text}")
    add_xp(user_id, 10, "new_goal")
    new_achievements = check_and_grant_achievements(user_id)

    response = t("goal_saved", lang, goal=goal_text)
    save_memory(user_id, "bot", response)
    await update.message.reply_text(response)
    await notify_achievements(update, new_achievements, lang)
    return ConversationHandler.END


# =========================
# /goals
# =========================
async def goals_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    goals = get_goals(user_id)
    if not goals:
        await update.message.reply_text("No goals yet. Use /goal to add one.")
        return
    msg = "🎯 Goals:\n\n"
    for i, (gid, text, status, progress, created) in enumerate(goals, 1):
        msg += f"{i}. {text}\n   📊 {progress}%\n\n"
    await update.message.reply_text(msg)


# =========================
# /profile
# =========================
async def profile_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)
    if not profile:
        await update.message.reply_text("No profile yet. Use /start")
        return

    name, style, main_goal, created, reminder_time, daily_minutes, language = profile
    total_xp, level, xp_to_next = get_xp(user_id)
    current, longest, total_days = get_streak(user_id)
    trust_score, _, _ = get_trust(user_id)
    premium = "✅ Premium" if is_premium(user_id) else "❌ Free"
    lang = language or "en"

    xp_in_level = total_xp % 100
    bar = "█" * (xp_in_level // 10) + "░" * (10 - xp_in_level // 10)

    await update.message.reply_text(
        f"👤 Profile — {name}\n\n"
        f"🌍 Language: {LANGUAGES.get(lang, lang)}\n"
        f"🎯 Goal: {main_goal or '—'}\n"
        f"⏰ Reminder: {reminder_time or '—'}\n"
        f"⏱ Daily time: {daily_minutes or 15} min\n\n"
        f"⭐ XP: {total_xp} | [{bar}]\n"
        f"🏅 Level {level} — {get_level_title(level, lang)}\n"
        f"🔥 Streak: {current} days | Best: {longest}\n"
        f"🛡 Trust: {trust_score}/100\n"
        f"💎 {premium}"
    )


# =========================
# /style
# =========================
async def style_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update.effective_user.id)
    btns = STYLE_BUTTONS.get(lang, STYLE_BUTTONS["en"])
    keyboard = [[btns[0], btns[1]], [btns[2], btns[3]], [btns[4]]]
    await update.message.reply_text(
        t("style_prompt", lang),
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    )
    return WAITING_STYLE


async def style_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    choice = update.message.text
    style = STYLE_MAP.get(choice, "friendly")
    save_user_profile(user_id, coaching_style=style)
    await update.message.reply_text(
        f"✅ {choice}",
        reply_markup=main_menu_keyboard(lang)
    )
    return ConversationHandler.END


# =========================
# /language
# =========================
async def language_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang_buttons = []
    langs = list(LANGUAGES.items())
    for i in range(0, len(langs), 2):
        row = [langs[i][1]]
        if i + 1 < len(langs):
            row.append(langs[i+1][1])
        lang_buttons.append(row)
    markup = ReplyKeyboardMarkup(lang_buttons, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌍 Choose language:", reply_markup=markup)
    return WAITING_LANGUAGE


# =========================
# /reminder
# =========================
async def reminder_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update.effective_user.id)
    await update.message.reply_text(t("reminder_prompt", lang))
    return WAITING_REMINDER_TIME


async def reminder_time_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update.effective_user.id)
    time_text = update.message.text.strip()
    try:
        parts = time_text.split(":")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59): raise ValueError()
        formatted = f"{hour:02d}:{minute:02d}"
    except:
        await update.message.reply_text("❌ Format: HH:MM (e.g. 21:30)")
        return WAITING_REMINDER_TIME
    context.user_data["reminder_time"] = formatted
    await update.message.reply_text(f"✅ {formatted}\n\nHow many minutes per day? (e.g. 15, 30, 60)")
    return WAITING_REMINDER_MINUTES


async def reminder_minutes_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    try:
        minutes = int(update.message.text.strip())
        if not (5 <= minutes <= 480): raise ValueError()
    except:
        await update.message.reply_text("❌ Enter a number between 5 and 480")
        return WAITING_REMINDER_MINUTES
    reminder_time = context.user_data.get("reminder_time")
    save_user_profile(user_id, reminder_time=reminder_time, daily_minutes=minutes)
    await update.message.reply_text(
        f"🔥 Reminder set!\n⏰ {reminder_time}\n⏱ {minutes} min/day",
        reply_markup=main_menu_keyboard(lang)
    )
    return ConversationHandler.END


# =========================
# /checkin
# =========================
async def checkin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update.effective_user.id)
    await update.message.reply_text(t("checkin_prompt", lang))
    return WAITING_CHECKIN


async def checkin_received(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    note = update.message.text

    saved = save_checkin(user_id, note)
    update_streak(user_id)
    current, longest, total = get_streak(user_id)

    if saved:
        xp_amount = 30 if current >= 7 else 25 if current >= 3 else 20
        total_xp, level, leveled_up = add_xp(user_id, xp_amount, "daily_checkin")
        update_trust(user_id, +2)
        new_achievements = check_and_grant_achievements(user_id)

        msg = f"✅ Checkin saved!\n\n📝 «{note}»\n\n🔥 Streak: {current} days\n⭐ +{xp_amount} XP (Total: {total_xp})\n🏅 Level {level} — {get_level_title(level, lang)}"
        if leveled_up:
            msg += f"\n\n🎉 Level Up! Level {level}!"

        await update.message.reply_text(msg)
        await notify_achievements(update, new_achievements, lang)
    else:
        total_xp, level, _ = get_xp(user_id)
        await update.message.reply_text(f"Already checked in today! ✅\n\n🔥 Streak: {current} | ⭐ XP: {total_xp}")
    return ConversationHandler.END


# =========================
# /streak
# =========================
async def streak_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    current, longest, total = get_streak(user_id)
    if current == 0:
        await update.message.reply_text("No streak yet!\nUse /checkin every day to start. 🔥")
        return
    emoji = "🏆" if current >= 30 else "🔥" if current >= 14 else "⚡" if current >= 7 else "✅"
    await update.message.reply_text(f"{emoji} Streak:\n\n🔥 Current: {current} days\n🏆 Best: {longest} days\n📅 Total active: {total} days")


# =========================
# /xp
# =========================
async def xp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    total_xp, level, xp_to_next = get_xp(user_id)
    current, _, _ = get_streak(user_id)
    xp_in_level = total_xp % 100
    bar = "█" * (xp_in_level // 10) + "░" * (10 - xp_in_level // 10)
    await update.message.reply_text(
        f"⭐ XP Status:\n\n"
        f"🏅 Level {level} — {get_level_title(level, lang)}\n"
        f"[{bar}] {xp_in_level}/100\n"
        f"✨ Total: {total_xp} XP\n"
        f"🎯 To next level: {xp_to_next} XP\n"
        f"🔥 Streak: {current} days\n\n"
        f"💡 /checkin = 20-30 XP\n"
        f"💡 /goal = 10 XP"
    )


# =========================
# /achievements
# =========================
async def achievements_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    achieved = get_achievements(user_id)
    if not achieved:
        await update.message.reply_text("No achievements yet!\n\n• /goal → 🎯 Goal Setter\n• /checkin → ✅ First Checkin\n• 3 days active → ⚡ 3 Day Streak")
        return
    msg = f"🏅 Achievements ({len(achieved)}):\n\n"
    for key, achieved_at in achieved:
        name, desc = ACHIEVEMENT_LIST.get(key, (key, ""))
        msg += f"{name}\n   {desc}\n\n"
    msg += f"📊 {len(achieved)} of {len(ACHIEVEMENT_LIST)} unlocked"
    await update.message.reply_text(msg)


# =========================
# /trust
# =========================
async def trust_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    score, verified, fake = get_trust(user_id)
    label = "🟢 Excellent" if score >= 80 else "🟡 Good" if score >= 60 else "🟠 Average" if score >= 40 else "🔴 Low"
    await update.message.reply_text(f"🛡 Trust Score:\n\n{score}/100 — {label}\n\n✅ Daily checkin: +2\n🎯 Goal complete: +5\n❌ Inactivity: -1/day")


# =========================
# /report
# =========================
async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    profile = get_user_profile(user_id)
    name = profile[0] if profile else "User"
    await send_weekly_report(context.application, user_id, name)


# =========================
# /premium
# =========================
async def premium_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if is_premium(user_id):
        await update.message.reply_text("💎 You are Premium!\n\n✅ Advanced coaching\n✅ Detailed reports\n✅ Priority responses")
    else:
        await update.message.reply_text("💎 GoalForge Premium\n\nHow to get it:\n🏆 Reach Level 10\n🏅 Unlock 5 achievements\n🔥 30-day streak\n\nKeep going!")


# =========================
# /status
# =========================
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔥 GoalForge Online.")


# =========================
# /help
# =========================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    lang = get_user_language(user_id)
    msg = t("commands_title", lang) + (t("commands_body", lang) if lang in ["fa", "en", "ru", "de", "tr"] else (
        "\n🎯 /goal /goals\n📊 /checkin /streak /xp /achievements /trust /report\n⚙️ /profile /style /reminder /language /premium"
    ))
    await update.message.reply_text(msg, reply_markup=main_menu_keyboard(lang), parse_mode="Markdown")


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
    await notify_achievements(update, new_achievements, get_user_language(user_id))


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_user_language(update.effective_user.id)
    await update.message.reply_text("❌ Cancelled.", reply_markup=main_menu_keyboard(lang))
    return ConversationHandler.END


async def post_init(app):
    asyncio.create_task(send_reminders(app))


# =========================
# App setup
# =========================
app = Application.builder().token(TOKEN).post_init(post_init).build()

start_conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={WAITING_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_selected)]},
    fallbacks=[CommandHandler("cancel", cancel)]
)
language_conv = ConversationHandler(
    entry_points=[CommandHandler("language", language_cmd)],
    states={WAITING_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_selected)]},
    fallbacks=[CommandHandler("cancel", cancel)]
)
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

app.add_handler(start_conv)
app.add_handler(language_conv)
app.add_handler(reminder_conv)
app.add_handler(style_conv)
app.add_handler(checkin_conv)
app.add_handler(goal_conv)
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
