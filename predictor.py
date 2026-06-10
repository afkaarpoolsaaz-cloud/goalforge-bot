def predict_user_risk(memory_text: str) -> str:
    """
    Analyze text and return risk level:
    high_risk / medium_risk / low_risk
    """
    text = memory_text.lower()
    score = {"low_risk": 0, "medium_risk": 0, "high_risk": 0}

    high_signals = [
        "ولش کن", "حوصله ندارم", "give up", "quit", "i'm done",
        "сдаюсь", "бросить", "放弃", "aufgeben", "me rindo"
    ]
    for w in high_signals:
        if w in text:
            score["high_risk"] += 3

    cant_signals = [
        "سخته", "نمی‌تونم", "نمیتونم", "can't", "cannot", "impossible",
        "не могу", "невозможно", "做不到", "不可能", "unmöglich", "imposible"
    ]
    for w in cant_signals:
        if w in text:
            score["high_risk"] += 2

    confused_signals = [
        "نمی‌دونم", "نمیدونم", "don't know", "not sure", "confused",
        "не знаю", "不知道", "weiß nicht", "no sé"
    ]
    for w in confused_signals:
        if w in text:
            score["medium_risk"] += 2

    positive_signals = [
        "برنامه", "هدف", "plan", "goal", "цель", "план",
        "目标", "计划", "ziel", "objetivo"
    ]
    for w in positive_signals:
        if w in text:
            score["low_risk"] += 2

    return max(score, key=score.get)
