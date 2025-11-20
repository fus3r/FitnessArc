# Create your views here.

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_leaderboard


@login_required
def index(request):
    """
    Page principale du leaderboard.
    """
    rows, current_rank = get_leaderboard(request.user)

    # Top 10 global
    top_10 = rows[:10]

    # Stats perso (ou None si pas trouvé, très peu probable)
    me = None
    for r in rows:
        if r["user"] == request.user:
            me = r
            break

    context = {
        "top_10": top_10,
        "me": me,
        "current_rank": current_rank,
        "total_players": len(rows),
    }
    return render(request, "leaderboard/index.html", context)
