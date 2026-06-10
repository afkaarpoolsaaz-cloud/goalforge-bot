from database import get_trust


def format_trust_text(user_id):
    score, verified, fake = get_trust(user_id)
    label = (
        "🟢 Excellent" if score >= 80 else
        "🟡 Good" if score >= 60 else
        "🟠 Average" if score >= 40 else
        "🔴 Low"
    )
    return (
        f"🛡 Trust Score:\n\n{score}/100 — {label}\n\n"
        "✅ Daily checkin: +2\n"
        "🎯 Goal complete: +5\n"
        "❌ Inactivity: -1/day"
    )
