from ai_engine import forge_ai_response
from database import (
    get_memory, save_memory, save_learning,
    get_user_profile, save_behavior, get_user
)
from lang import t


def get_welcome_message(user_id: int, user_name: str) -> str:
    user = get_user(user_id)
    lang = user[2] if user else "en"
    return t("welcome", lang, name=user_name)


def forge_chat(user_text: str, user_id: int) -> str:
    memory = get_memory(user_id, limit=15)
    profile = get_user_profile(user_id)

    text_lower = user_text.lower()
    if any(w in text_lower for w in ["can't", "cannot", "نمیتونم", "نمی‌تونم", "سخته", "خسته", "не могу", "impossible"]):
        save_behavior(user_id, "struggle", user_text)
    elif any(w in text_lower for w in ["done", "finished", "کردم", "تموم", "انجام دادم", "готово", "完成"]):
        save_behavior(user_id, "success", user_text)

    save_memory(user_id, "user", user_text)
    response = forge_ai_response(user_text, memory, profile)
    save_memory(user_id, "bot", response)

    try:
        save_learning(user_id, user_text, response)
    except Exception as e:
        print(f"[LEARNING SAVE ERROR] {e}")

    return response


def forge_goal_discovery(user_text: str, user_id: int) -> str:
    """Alias for the main AI coaching flow used by the Telegram bot."""
    return forge_chat(user_text, user_id)
