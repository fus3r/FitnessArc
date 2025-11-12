from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import get_dashboard_data

@login_required
def dashboard_index(request):
    data = get_dashboard_data(request.user)
    return render(request, 'dashboard/index.html', data)
