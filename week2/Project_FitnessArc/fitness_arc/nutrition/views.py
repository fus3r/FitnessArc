# nutrition/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Food, FoodLog
from .forms import FoodLogForm

@login_required
def nutrition_today(request):
    today = timezone.now().date()
    user_logs = FoodLog.objects.filter(owner=request.user, date=today).select_related('food')
    
    total_kcal = sum(log.kcal for log in user_logs)
    total_protein = sum(log.protein for log in user_logs)
    total_carbs = sum(log.carbs for log in user_logs)
    total_fat = sum(log.fat for log in user_logs)
    
    if request.method == 'POST':
        form = FoodLogForm(request.POST)
        if form.is_valid():
            new_log = form.save(commit=False)
            new_log.owner = request.user
            new_log.date = today
            new_log.save()
            return redirect('nutrition_today')
    else:
        form = FoodLogForm()
        
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
    
    return render(request, 'nutrition/nutrition_today.html', context)

@login_required
def delete_food_log(request, pk):
    log_to_delete = get_object_or_404(FoodLog, pk=pk, owner=request.user)
    food_name = log_to_delete.food.name
    log_to_delete.delete()
    messages.success(request, f"L'entrée '{food_name}' a été supprimée.")
    return redirect('nutrition_today')