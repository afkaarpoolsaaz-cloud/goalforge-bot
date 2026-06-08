from ai_engine import forge_ai_response
from database import get_memory, save_memory, save_learning, get_user_profile, save_behavior


def get_welcome_message(user_name: str) -> str:
    return (
        f"🔥 سلام {user_name}!\n\n"
        "من Forge هستم — کوچ اجرایی شخصی‌ات.\n\n"
        "بهم بگو:\n"
        "👉 الان روی چه هدفی کار می‌کنی؟\n\n"
        "اگه هنوز هدف نداری، فقط بگو «نمی‌دونم» تا کمکت کنم پیداش کنی."
    )


def forge_goal_discovery(user_text: str, user_id) -> str:

    # Load memory
    memory = get_memory(user_id, limit=10)

    # Load user profile
    profile = get_user_profile(user_id)

    # Detect behavior patterns
    text_lower = user_text.lower()
    if any(w in text_lower for w in ["نمیتونم", "نمی‌تونم", "سخته", "خسته"]):
        save_behavior(user_id, "struggle", user_text)
    elif any(w in text_lower for w in ["کردم", "تموم", "انجام دادم", "موفق"]):
        save_behavior(user_id, "success", user_text)

    # Get AI response with profile
    response = forge_ai_response(user_text, memory, profile)

    # Save learning
    try:
        save_learning(user_id, user_text, response)
    except Exception as e:
        print(f"[LEARNING SAVE ERROR] {e}")

    return response
