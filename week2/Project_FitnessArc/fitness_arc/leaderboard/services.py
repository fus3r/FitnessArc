# leaderboard/services.py
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from workouts.models import WorkoutSession, PR


User = get_user_model()


def compute_user_stats(user):
    """
    Calculate basic stats for a user for the leaderboard.
    Returns XP, level, and league based on sessions, volume, and PRs.
    """
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)

    # Completed sessions in last 30 days
    sessions = WorkoutSession.objects.filter(
        owner=user,
        is_completed=True,
        date__gte=month_ago,
    )

    sessions_count = sessions.count()

    # Total volume over 30 days
    total_volume = sum(sess.total_volume for sess in sessions)

    # Number of PRs recorded (all time)
    prs_count = PR.objects.filter(owner=user).count()

    # XP calculation:
    #  - 10 XP per session
    #  - 1 XP per 100 kg of volume (last 30 days)
    #  - 5 XP per PR
    xp = (
        sessions_count * 10
        + (total_volume / 100.0)
        + prs_count * 5
    )

    # Level = XP // 50
    level = int(xp // 50)

    # League based on level
    if level >= 20:
        league = "Master"
    elif level >= 15:
        league = "Diamond"
    elif level >= 10:
        league = "Platinum"
    elif level >= 5:
        league = "Gold"
    elif level >= 2:
        league = "Silver"
    else:
        league = "Bronze"

    return {
        "user": user,
        "sessions_30d": sessions_count,
        "volume_30d": total_volume,
        "prs_count": prs_count,
        "xp": xp,
        "level": level,
        "league": league,
    }


def get_leaderboard(current_user):
    """
    Build the full leaderboard list + current user's rank.
    Currently includes all active users. Could be filtered to friends in the future.
    """
    # Only active accounts
    users = User.objects.filter(is_superuser=False)

    rows = []
    for u in users:
        stats = compute_user_stats(u)
        rows.append(stats)

    # Sort by XP descending
    rows.sort(key=lambda r: r["xp"], reverse=True)

    # Current user's rank
    current_rank = None
    for idx, row in enumerate(rows, start=1):
        if row["user"].id == current_user.id:
            current_rank = idx
            break

    return rows, current_rank
