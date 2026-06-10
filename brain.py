from database import get_memory


def predict_user_state(user_id: int) -> str:
    """
    Analyze last messages and return state:
    coach_mode / motivation_mode / normal_mode
    """
    history = get_memory(user_id, limit=15)
    messages = [msg for role, msg in history if role == "user"]
    combined = " ".join(messages).lower()

    score = {"coach": 0, "motivation": 0, "normal": 0}

    for w in ["goal", "plan", "هدف", "برنامه", "цель", "目标", "objetivo", "ziel"]:
        if w in combined:
            score["coach"] += 1

    for w in ["money", "income", "پول", "درآمد", "деньги", "收入", "dinero", "geld"]:
        if w in combined:
            score["coach"] += 2

    for w in ["tired", "خسته", "устал", "cansado", "müde", "give up", "ولش کن", "حوصله ندارم", "сдаюсь"]:
        if w in combined:
            score["motivation"] += 3

    for w in ["hard", "سخته", "трудно", "难", "difícil", "schwer", "can't", "نمی‌تونم", "не могу"]:
        if w in combined:
            score["motivation"] += 2

    best = max(score, key=score.get)

    if score[best] == 0:
        return "normal_mode"
    if best == "coach":
        return "coach_mode"
    if best == "motivation":
        return "motivation_mode"
    return "normal_mode"
