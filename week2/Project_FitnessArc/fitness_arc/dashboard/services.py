from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from collections import defaultdict
from workouts.models import WorkoutSession, SetLog, PR
from nutrition.models import FoodLog
import calendar 
def get_dashboard_data(user):
    """Calcule toutes les données du dashboard pour un utilisateur"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    five_weeks_ago = today - timedelta(days=35)
    month_start = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    month_end = today.replace(day=last_day)

    
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

    #Durée des séances
    weekly_training_time = 0
    for session in recent_sessions:
        if session.duration_minutes:
            weekly_training_time += session.duration_minutes
    weekly_training_hours = weekly_training_time // 60   
    weekly_training_min = weekly_training_time % 60
    
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

    # Calendrier du mois
    month_sessions = WorkoutSession.objects.filter(
        owner=user,
        date__gte=month_start,
        date__lte=month_end,
        is_completed=True,
    ).prefetch_related('set_logs__exercise', 'from_template')

    sessions_by_date = defaultdict(list)
    for session in month_sessions:
        sessions_by_date[session.date].append(session)

    cal = calendar.Calendar(firstweekday=0)  # 0 = lundi
    calendar_weeks = []

    for week in cal.monthdatescalendar(today.year, today.month):
        week_days = []
        for d in week:
            week_days.append({
                'date': d,                            
                'day': d.day,                         
                'in_month': (d.month == today.month), 
                'is_today': (d == today),
                'has_workout': d in sessions_by_date,
                'sessions': sessions_by_date.get(d, []),
            })
        calendar_weeks.append(week_days)
    
    # === Nouveaux Graphiques ===
    
    # 1. Workouts par Semaine (5 dernières semaines)
    weekly_workouts = defaultdict(int)
    all_sessions = WorkoutSession.objects.filter(
        owner=user,
        date__gte=five_weeks_ago,
        is_completed=True
    )
    
    for session in all_sessions:
        week_num = session.date.isocalendar()[1]
        weekly_workouts[week_num] += 1
    
    sorted_weeks = sorted(weekly_workouts.items())[-5:]
    weekly_workouts_labels = [f"S{w[0]}" for w in sorted_weeks]
    weekly_workouts_data = [w[1] for w in sorted_weeks]
    
    # 2. Calories Journalières (7 derniers jours)
    daily_calories_labels = []
    daily_calories_consumed = []
    daily_calories_burned = []
    
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        daily_calories_labels.append(date.strftime('%d/%m'))
        
        # Calories consommées
        food_logs = FoodLog.objects.filter(owner=user, date=date)
        consumed = sum(log.kcal for log in food_logs)
        daily_calories_consumed.append(round(float(consumed or 0), 1))
        
        # Calories brûlées
        workouts = WorkoutSession.objects.filter(owner=user, date=date, is_completed=True)
        burned = sum(w.estimated_calories_burned for w in workouts)
        daily_calories_burned.append(round(float(burned or 0), 1))
    
    # 3. Volume Hebdomadaire (5 dernières semaines)
    weekly_volumes = defaultdict(float)
    volume_sessions = WorkoutSession.objects.filter(
        owner=user,
        date__gte=five_weeks_ago,
        is_completed=True
    ).prefetch_related('set_logs')
    
    for session in volume_sessions:
        week_num = session.date.isocalendar()[1]
        weekly_volumes[week_num] += session.total_volume
    
    sorted_vol_weeks = sorted(weekly_volumes.items())[-5:]
    weekly_volume_labels = [f"S{w[0]}" for w in sorted_vol_weeks]
    weekly_volume_data = [round(float(w[1] or 0), 1) for w in sorted_vol_weeks]
    
    # 4. Macros du jour
    today_food_logs = FoodLog.objects.filter(owner=user, date=today)
    carbs_consumed = sum(log.carbs for log in today_food_logs)
    fat_consumed = sum(log.fat for log in today_food_logs)
    
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
        'carbs_consumed': round(carbs_consumed, 1),
        'fat_consumed': round(fat_consumed, 1),
        'weekly_workouts_labels': weekly_workouts_labels,
        'weekly_workouts_data': weekly_workouts_data,
        'weekly_training_time': weekly_training_time,
        'weekly_training_hours': weekly_training_hours,      
        'weekly_training_min': weekly_training_min,
        'daily_calories_labels': daily_calories_labels,
        'daily_calories_consumed': daily_calories_consumed,
        'daily_calories_burned': daily_calories_burned,
        'weekly_volume_labels': weekly_volume_labels,
        'weekly_volume_data': weekly_volume_data,
        'calendar_weeks': calendar_weeks,
    }
