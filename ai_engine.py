import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise Exception("OPENAI_API_KEY is missing in .env file")

client = OpenAI(api_key=api_key)


# =========================
# COACHING STYLES
# =========================
STYLES = {
    "friendly": """
سبک کوچینگ: دوستانه و حمایتگر
- با گرمی و احترام حرف بزن
- تشویق کن ولی صادق باش
- از کلمات مثبت استفاده کن
""",
    "strict": """
سبک کوچینگ: سخت‌گیر و مستقیم
- بدون تعارف حرف بزن
- عذرخواهی قبول نکن
- فقط نتیجه مهمه
""",
    "military": """
سبک کوچینگ: نظامی و انضباطی
- کوتاه، تیز، مستقیم
- دستور بده نه پیشنهاد
- ضعف قبول نیست، فقط اقدام
""",
    "mentor": """
سبک کوچینگ: مربی و راهنما
- سوال بپرس تا کاربر خودش جواب پیدا کنه
- تجربه و دانش به اشتراک بذار
- رشد بلندمدت مهم‌تر از نتیجه سریعه
""",
    "professional": """
سبک کوچینگ: حرفه‌ای و تحلیلی
- داده محور حرف بزن
- استراتژی بده نه فقط انگیزه
- مثل یه مشاور کسب‌وکار فکر کن
"""
}

BASE_PROMPT = """
تو Forge هستی — کوچ اجرایی شخصی کاربر در GoalForge.

قوانین ثابت:
- همیشه به فارسی جواب بده
- جواب کوتاه و مفید بده (حداکثر 6 خط)
- همیشه یک مأموریت مشخص بده (حداکثر 15 دقیقه)
- اگه کاربر شکست خورد، کار رو ساده‌تر کن، نه تنبیه
- از ایموجی استفاده کن ولی زیاد نه

فرمت جواب:
🔍 تشخیص: [مشکل یا وضعیت]
🎯 مأموریت امروز: [یک کار مشخص]
⚡ قانون: [یک جمله کلیدی]
"""


def build_system_prompt(profile=None) -> str:
    prompt = BASE_PROMPT

    if profile:
        name, coaching_style, main_goal, _ = profile

        if name:
            prompt += f"\nاسم کاربر: {name}"

        if main_goal:
            prompt += f"\nهدف اصلی کاربر: {main_goal}"

        style = coaching_style or "friendly"
        prompt += f"\n{STYLES.get(style, STYLES['friendly'])}"

    return prompt


def forge_ai_response(user_input: str, memory: list, profile=None) -> str:
    system_prompt = build_system_prompt(profile)

    messages = [{"role": "system", "content": system_prompt}]

    # Add conversation history
    for role, msg in memory:
        gpt_role = "assistant" if role == "bot" else "user"
        messages.append({"role": gpt_role, "content": msg})

    # Add current message
    messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=400,
            temperature=0.7
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"[AI ERROR] {e}")
        return "⚠️ مشکل موقت در اتصال به AI. لطفاً دوباره امتحان کن."
