from telegram import ReplyKeyboardMarkup, KeyboardButton
from database import save_mood, get_last_mood

MOOD_OPTIONS = ["Excellent", "Good", "Neutral", "Tired", "Struggling"]


def get_mood_markup():
    buttons = [[KeyboardButton(option)] for option in MOOD_OPTIONS]
    return ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)


def format_mood_saved(mood):
    return f"✅ Mood saved: {mood}"


def latest_mood(user_id):
    return get_last_mood(user_id)
