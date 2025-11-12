from django.utils import timezone
from datetime import timedelta
from workouts.models import WorkoutSession, SetLog, PR
from nutrition.models import FoodLog

def get_dashboard_data(user):
    """Calcule toutes les données du dashboard pour un utilisateur"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    # Calories nutrition (aujourd'hui)
    today_food_logs = FoodLog.objects.filter(owner=user, date=today)
    calories_consumed = sum(log.kcal for log in today_food_logs)
    protein_consumed = sum(log.protein for log in today_food_logs)
    
    # Calories workout (aujourd'hui)
    today_workouts = WorkoutSession.objects.filter(owner=user, date=today)
    calories_burned = sum(session.estimated_calories_burned for session in today_workouts)
    
    # Balance calorique
    calorie_balance = calories_consumed - calories_burned
    
    # Volume d'entraînement (7 derniers jours)
    recent_sessions = WorkoutSession.objects.filter(
        owner=user,
        date__gte=week_ago
    ).prefetch_related('set_logs')
    
    weekly_volume = sum(session.total_volume for session in recent_sessions)
    
    # PRs récents (5 derniers)
    recent_prs = PR.objects.filter(owner=user).order_by('-date')[:5]
    
    # Nombre de séances cette semaine
    sessions_count = recent_sessions.count()
    
    return {
        'calories_consumed': round(calories_consumed, 1),
        'protein_consumed': round(protein_consumed, 1),
        'calories_burned': round(calories_burned, 1),
        'calorie_balance': round(calorie_balance, 1),
        'weekly_volume': round(weekly_volume, 1),
        'sessions_count': sessions_count,
        'recent_prs': recent_prs,
        'today': today,
    }
