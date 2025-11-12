# nutrition/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Food, FoodLog
from .forms import FoodLogForm
import json
from decimal import Decimal

def nutrition_today(request):
    today = timezone.now().date()
    
    if request.method == "POST":
        form = FoodLogForm(request.POST)
        if form.is_valid():
            log = form.save(commit=False)
            log.owner = request.user
            log.date = today
            log.save()
            messages.success(request, "Aliment ajouté avec succès!")
            return redirect("nutrition_today")
    else:
        form = FoodLogForm()
    
    logs = FoodLog.objects.filter(owner=request.user, date=today).select_related('food')
    
    totals = {
        'kcal': sum(float(log.kcal) for log in logs),
        'protein': sum(float(log.protein) for log in logs),
        'carbs': sum(float(log.carbs) for log in logs),
        'fat': sum(float(log.fat) for log in logs)
    }
    
    logs_json = json.dumps([{
        'id': log.id,
        'food_name': log.food.name,
        'quantity': float(log.quantity),
        'unit': log.food.get_unit_label(),
        'meal_type': log.meal_type,
        'kcal': float(log.kcal),
        'protein': float(log.protein),
        'carbs': float(log.carbs),
        'fat': float(log.fat)
    } for log in logs])
    
    totals_json = json.dumps({
        'kcal': round(totals['kcal'], 1),
        'protein': round(totals['protein'], 1),
        'carbs': round(totals['carbs'], 1),
        'fat': round(totals['fat'], 1)
    })
    
    foods_json = json.dumps([{
        'id': f.id,
        'name': f.name,
        'unit_type': f.unit_type
    } for f in Food.objects.filter(is_public=True).order_by('name')])
    
    return render(request, 'nutrition/nutrition_today.html', {
        'form': form,
        'logs': logs,
        'totals': totals,
        'logs_json': logs_json,
        'totals_json': totals_json,
        'foods_json': foods_json,
        'current_date': today
    })

@login_required
def delete_food_log(request, pk):
    log_to_delete = get_object_or_404(FoodLog, pk=pk, owner=request.user)
    food_name = log_to_delete.food.name
    log_to_delete.delete()
    messages.success(request, f"L'entrée '{food_name}' a été supprimée.")
    return redirect('nutrition_today')