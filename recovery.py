from database import get_inactivity_days


def format_recovery_message(name, inactivity_days):
    return (
        f"⏳ Hi {name}, I noticed you haven't checked in for {inactivity_days} days.\n"
        "Let's make today easy:\n"
        "✅ Write one sentence about what you want to do next.\n"
        "✅ After that, send /checkin."
    )
