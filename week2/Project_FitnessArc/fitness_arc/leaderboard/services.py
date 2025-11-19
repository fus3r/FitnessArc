# leaderboard/services.py
from datetime import timedelta

from django.utils import timezone
from django.contrib.auth import get_user_model

from workouts.models import WorkoutSession, PR


User = get_user_model()


def compute_user_stats(user):
    """
    Calcule les stats de base d'un utilisateur pour le leaderboard.
    """
    today = timezone.now().date()
    month_ago = today - timedelta(days=30)

    # Séances complétées sur 30 jours
    sessions = WorkoutSession.objects.filter(
        owner=user,
        is_completed=True,
        date__gte=month_ago,
    )

    sessions_count = sessions.count()

    # Volume total sur 30 jours
    total_volume = sum(sess.total_volume for sess in sessions)

    # Nombre de PR enregistrés (tous temps)
    prs_count = PR.objects.filter(owner=user).count()

    # "XP" simplifié
    #  - 10 XP par séance
    #  - 1 XP par 100 kg de volume (30 derniers jours)
    #  - 5 XP par PR
    xp = (
        sessions_count * 10
        + (total_volume / 100.0)
        + prs_count * 5
    )

    # Niveau = XP // 50 (par exemple)
    level = int(xp // 50)

    # Ligue en fonction du niveau
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
    Construit la liste complète du leaderboard + la position de l'utilisateur courant.
    Pour l'instant on prend *tous* les utilisateurs actifs.
    Plus tard on pourra filtrer sur "amis".
    """
    # Que les comptes actifs
    users = User.objects.filter(is_active=True)

    rows = []
    for u in users:
        stats = compute_user_stats(u)
        rows.append(stats)

    # Tri décroissant par XP
    rows.sort(key=lambda r: r["xp"], reverse=True)

    # Rang de l'utilisateur courant
    current_rank = None
    for idx, row in enumerate(rows, start=1):
        if row["user"].id == current_user.id:
            current_rank = idx
            break

    return rows, current_rank
