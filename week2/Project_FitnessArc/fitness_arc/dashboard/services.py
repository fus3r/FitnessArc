from django.utils import timezone
from datetime import timedelta
from workouts.models import WorkoutSession, SetLog, PR
from nutrition.models import FoodLog

def get_dashboard_data(user):
    """Calcule toutes les données du dashboard pour un utilisateur"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
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
    
    # Historique des séances (30 derniers jours, complétées uniquement)
    workout_history = WorkoutSession.objects.filter(
        owner=user,
        date__gte=month_ago,
        is_completed=True
    ).prefetch_related('set_logs__exercise').order_by('-date')[:10]
    
    # Calculer les détails pour chaque workout
    workout_details = []
    for session in workout_history:
        # PRs détectés pendant cette séance
        session_prs = PR.objects.filter(owner=user, date=session.date)
        
        # Exercices uniques
        exercises = {}
        for log in session.set_logs.all():
            ex_name = log.exercise.name
            if ex_name not in exercises:
                exercises[ex_name] = {'sets': 0, 'reps': 0}
            exercises[ex_name]['sets'] += 1
            exercises[ex_name]['reps'] += log.reps
        
        workout_details.append({
            'session': session,
            'exercises': exercises,
            'prs_count': session_prs.count(),
            'total_sets': session.set_logs.count(),
        })
    
    return {
        'calories_consumed': round(calories_consumed, 1),
        'protein_consumed': round(protein_consumed, 1),
        'calories_burned': round(calories_burned, 1),
        'calorie_balance': round(calorie_balance, 1),
        'weekly_volume': round(weekly_volume, 1),
        'sessions_count': sessions_count,
        'recent_prs': recent_prs,
        'workout_history': workout_details,
        'today': today,
    }
