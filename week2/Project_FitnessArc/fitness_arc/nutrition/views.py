# nutrition/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from .models import Food, FoodLog
from .forms import FoodLogForm # Le formulaire sera créé à l'étape 3

@login_required
def nutrition_today(request):
    """
    Affiche le journal alimentaire du jour de l'utilisateur et gère l'ajout de FoodLog.
    """
    today = timezone.now().date()
    user_logs = FoodLog.objects.filter(owner=request.user, date=today).select_related('food')
    
    # 1. Calcul des totaux journaliers (Must-have [cite: 38])
    # Note: On calcule les totaux en Python ici en itérant sur les logs pour utiliser les @property
    # Ceci est simple, mais devra être optimisé avec des annotations de DB (queries agrégées) plus tard
    
    total_kcal = sum(log.kcal for log in user_logs)
    total_protein = sum(log.protein for log in user_logs)
    total_carbs = sum(log.carbs for log in user_logs)
    total_fat = sum(log.fat for log in user_logs)
    
    # 2. Gestion du formulaire d'ajout
    if request.method == 'POST':
        form = FoodLogForm(request.POST)
        if form.is_valid():
            new_log = form.save(commit=False)
            new_log.owner = request.user
            new_log.date = today
            new_log.save()
            # Django messages : Vous voudrez peut-être ajouter un message de succès ici
            return redirect('nutrition_today') # Redirection pour éviter la soumission multiple
    else:
        form = FoodLogForm()
        
    # 3. Rendu du template
    context = {
        'current_date': today,
        'logs': user_logs,
        'form': form,
        'totals': {
            'kcal': round(total_kcal, 2),
            'protein': round(total_protein, 2),
            'carbs': round(total_carbs, 2),
            'fat': round(total_fat, 2),
        }
    }
    
    # Utilisation du template nutrition_today.html (Must-have )
    return render(request, 'nutrition/nutrition_today.html', context)