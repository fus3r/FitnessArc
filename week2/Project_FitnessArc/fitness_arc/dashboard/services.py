from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from collections import defaultdict
from workouts.models import WorkoutSession, SetLog, PR
from nutrition.models import FoodLog
try:
    from running.models import Run
except ImportError:
    Run = None
import calendar 
def get_dashboard_data(user, ref_date=None):
    """Calcule toutes les données du dashboard pour un utilisateur"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    five_weeks_ago = today - timedelta(days=35)

    if ref_date is None:
        focus_date = today         
    else:
        focus_date = ref_date
    month_start = focus_date.replace(day=1)
    last_day = calendar.monthrange(focus_date.year, today.month)[1]
    month_end = today.replace(day=last_day)
    # --- Navigation de mois pour le calendrier ---
    current_month = month_start  

    # Mois précédent
    if current_month.month == 1:
        prev_month_year = current_month.year - 1
        prev_month_month = 12
    else:
        prev_month_year = current_month.year
        prev_month_month = current_month.month - 1

    # Mois suivant
    if current_month.month == 12:
        next_month_year = current_month.year + 1
        next_month_month = 1
    else:
        next_month_year = current_month.year
        next_month_month = current_month.month + 1

    # Nom mois
    current_month_label = current_month.strftime("%B %Y")

    
    # Calories nutrition (aujourd'hui)
    today_food_logs = FoodLog.objects.filter(owner=user, date=today)
    calories_consumed = float(sum(log.kcal for log in today_food_logs))
    protein_consumed = float(sum(log.protein for log in today_food_logs))
    
    # Calories workout (aujourd'hui)
    today_workouts = WorkoutSession.objects.filter(owner=user, date=today)
    calories_burned = float(sum(session.estimated_calories_burned for session in today_workouts))
    
    # Calories running (aujourd'hui)
    if Run is not None:
        today_runs = Run.objects.filter(user=user, start_date__date=today)
        calories_burned += float(sum(run.calories_burned or 0 for run in today_runs))
    
    # Balance calorique
    calorie_balance = calories_consumed - calories_burned
    
    # Volume d'entraînement (7 derniers jours)
    recent_sessions = WorkoutSession.objects.filter(
        owner=user,
        date__gte=week_ago
    ).prefetch_related('set_logs')
    
    weekly_volume = sum(session.total_volume for session in recent_sessions)
    
    # Comparaison avec la semaine précédente
    prev_week_end = week_ago - timedelta(days=1)
    prev_week_start = prev_week_end - timedelta(days=6)

    # Séances complétées la semaine précédente
    prev_week_sessions = WorkoutSession.objects.filter(
        owner=user,
        is_completed=True,
        date__gte=prev_week_start,
        date__lte=prev_week_end,
    ).prefetch_related('set_logs')

    # Nombre de séances semaine précédente
    prev_sessions_count = prev_week_sessions.count()

    # Volume semaine précédente
    prev_week_volume = sum(sess.total_volume for sess in prev_week_sessions)

    # Temps d’entraînement semaine précédente (en minutes)
    prev_week_training_time = 0
    for sess in prev_week_sessions:
        if sess.duration_minutes:
            prev_week_training_time += sess.duration_minutes

    # Calories brûlées semaine précédente
    prev_week_calories_burned = sum(
        sess.estimated_calories_burned for sess in prev_week_sessions
    )
    
    # Ajouter les calories de running pour la semaine précédente
    if Run is not None:
        prev_week_runs = Run.objects.filter(
            user=user,
            start_date__date__gte=prev_week_start,
            start_date__date__lte=prev_week_end,
        )
        prev_week_calories_burned += sum(run.calories_burned or 0 for run in prev_week_runs)

    # PRs récents (5 derniers)
    recent_prs = PR.objects.filter(owner=user).order_by('-date')[:5]
    all_prs = PR.objects.filter(owner=user).select_related('exercise').order_by(
        'exercise__name', 'metric', '-value'
    )

    best_prs_dict = {}
    for pr in all_prs:
        key = (pr.exercise_id, pr.metric)
        if key not in best_prs_dict:   # on garde le PR avec la plus grande valeur
            best_prs_dict[key] = pr

    best_prs = list(best_prs_dict.values())

    # Groupement par exercice pour l'affichage "onglet PR"
    grouped = defaultdict(list)
    for pr in best_prs:
        grouped[pr.exercise.name].append({
            'metric_label': pr.get_metric_display(),
            'value': pr.value,
            'date': pr.date,
        })
    
    best_prs_grouped = []
    for ex_name, prs_list in grouped.items():
        best_prs_grouped.append({
            'exercise': ex_name,
            'prs': prs_list,
        })

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
    
    month_sessions_count = month_sessions.count()
    month_total_duration = 0
    month_total_volume = 0
    month_total_calories_burned = 0

    for sess in month_sessions:
        if sess.duration_minutes:
            month_total_duration += sess.duration_minutes
        month_total_volume += sess.total_volume
        month_total_calories_burned += sess.estimated_calories_burned
    
    # Ajouter les calories de running pour le mois
    if Run is not None:
        month_runs = Run.objects.filter(
            user=user,
            start_date__date__gte=month_start,
            start_date__date__lte=month_end,
        )
        month_total_calories_burned += sum(run.calories_burned or 0 for run in month_runs)

    # Nombre de PR créés ce mois-ci
    month_prs_count = PR.objects.filter(
        owner=user,
        date__gte=month_start,
        date__lte=month_end,
    ).count()


    sessions_by_date = defaultdict(list)
    for session in month_sessions:
        sessions_by_date[session.date].append(session)

    cal = calendar.Calendar(firstweekday=0)  # 0 = lundi
    calendar_weeks = []

    for week in cal.monthdatescalendar(focus_date.year, focus_date.month):
        week_days = []
        for d in week:
            week_days.append({
                'date': d,                            
                'day': d.day,                         
                'in_month': (d.month == focus_date.month), 
                'is_today': (d == today),
                'has_workout': d in sessions_by_date,
                'sessions': sessions_by_date.get(d, []),
            })
        calendar_weeks.append(week_days)

        # --- Streak et constance mensuelle ---

    # Toutes les dates de séances complétées (sur 1 an par ex)
    one_year_ago = today - timedelta(days=365)
    all_dates_qs = WorkoutSession.objects.filter(
        owner=user,
        is_completed=True,
        date__gte=one_year_ago,
        date__lte=today,
    ).values_list('date', flat=True).distinct()

    # Met dans un set pour accès O(1)
    all_dates = set(all_dates_qs)

    # Streak actuel (en remontant à partir d'aujourd'hui)
    current_streak = 0
    cursor = today
    while cursor in all_dates:
        current_streak += 1
        cursor = cursor - timedelta(days=1)

    # Meilleur streak historique (sur 1 an)
    best_streak = 0
    # On parcourt les dates triées
    sorted_dates = sorted(all_dates)
    if sorted_dates:
        streak = 1
        for i in range(1, len(sorted_dates)):
            prev = sorted_dates[i - 1]
            curr = sorted_dates[i]
            if curr == prev + timedelta(days=1):
                streak += 1
            else:
                best_streak = max(best_streak, streak)
                streak = 1
        best_streak = max(best_streak, streak)

    # Constance mensuelle : nb de jours avec séance / nb de jours écoulés
    days_passed_in_month = (today - month_start).days + 1
    active_days_this_month = WorkoutSession.objects.filter(
        owner=user,
        is_completed=True,
        date__gte=month_start,
        date__lte=today,
    ).values('date').distinct().count()

    if days_passed_in_month > 0:
        monthly_consistency = round(
            active_days_this_month / days_passed_in_month * 100, 1
        )
    else:
        monthly_consistency = 0.0

    
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
        
        # Ajouter les calories de running pour ce jour
        if Run is not None:
            day_runs = Run.objects.filter(user=user, start_date__date=d)
            burned += sum(run.calories_burned or 0 for run in day_runs)
        
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
    
    week_sessions_diff = sessions_count - prev_sessions_count
    week_volume_diff = weekly_volume - prev_week_volume
    week_training_time_diff = weekly_training_time - prev_week_training_time
    week_calories_diff = calories_burned - prev_week_calories_burned

    # Répartition par groupe musculaire (dernier mois) ---

    muscle_volume = defaultdict(float)

    logs = SetLog.objects.filter(
        session__owner=user,
        session__is_completed=True,
        session__date__gte=month_ago,
    ).select_related('exercise')

    for log in logs:
        
        group = getattr(log.exercise, 'muscle_group', 'Autre') or 'Autre'

        vol = getattr(log, 'volume', None)
        if vol is None:
            vol = (log.weight_kg or 0) * (log.reps or 0)

        muscle_volume[group] += float(vol)

    muscle_groups_labels = []
    muscle_groups_values = []
    for g, v in sorted(muscle_volume.items()):
        muscle_groups_labels.append(g)
        muscle_groups_values.append(round(v, 1))


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
        'current_month_label': current_month_label,
        'prev_month_year': prev_month_year,
        'prev_month_month': prev_month_month,
        'next_month_year': next_month_year,
        'next_month_month': next_month_month,
        'recent_prs': recent_prs,
        'best_prs': best_prs,
        'best_prs_grouped': best_prs_grouped,
        'week_sessions_current': sessions_count,
        'week_sessions_previous': prev_sessions_count,
        'week_volume_current': weekly_volume,
        'week_volume_previous': prev_week_volume,
        'week_training_time_current': weekly_training_time,
        'week_training_time_previous': prev_week_training_time,
        'week_calories_current': calories_burned,
        'week_calories_previous': prev_week_calories_burned,
        'week_sessions_diff': week_sessions_diff,
        'week_volume_diff': week_volume_diff,
        'week_training_time_diff': week_training_time_diff,
        'week_calories_diff': week_calories_diff,
        'current_streak': current_streak,
        'best_streak': best_streak,
        'active_days_this_month': active_days_this_month,
        'days_passed_in_month': days_passed_in_month,
        'monthly_consistency': monthly_consistency,
        'month_sessions_count': month_sessions_count,
        'month_total_duration': month_total_duration,
        'month_total_volume': month_total_volume,
        'month_total_calories_burned': month_total_calories_burned,
        'month_prs_count': month_prs_count,
        'muscle_groups_labels': muscle_groups_labels,
        'muscle_groups_values': muscle_groups_values,
    }
