
from datetime import date
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_dashboard_data


@login_required
def index(request):
    """
    Vue principale du tableau de bord.
    - Lit ?year=YYYY&month=MM dans l'URL pour le calendrier
    - Appelle get_dashboard_data(user, ref_date=...)
    """

    year = request.GET.get("year")
    month = request.GET.get("month")
    ref_date = None

    if year and month:
        try:
            ref_date = date(int(year), int(month), 1)
        except ValueError:
            ref_date = None  
            
    context = get_dashboard_data(request.user, ref_date=ref_date)
    return render(request, "dashboard/index.html", context)