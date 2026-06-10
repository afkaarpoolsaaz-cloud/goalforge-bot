from database import get_rank


def format_rank_text(user_id):
    rank, total, score = get_rank(user_id)
    return (
        f"🏅 Your Rank: {rank}/{total}\n"
        f"⭐ Score: {score}\n"
    )
