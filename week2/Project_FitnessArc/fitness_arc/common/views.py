from django.shortcuts import render
from django.utils import timezone

# Create your views here.

def index(request):
    """Page d'accueil du site"""
    context = {}
    
    if request.user.is_authenticated:
        today = timezone.now().date()
        context['templates_count'] = request.user.workout_templates.count()
        context['today_logs_count'] = request.user.food_logs.filter(date=today).count()
    
    return render(request, 'common/index.html', context)
