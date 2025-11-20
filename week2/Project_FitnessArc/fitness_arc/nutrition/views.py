# nutrition/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import feature_required
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from .models import Food, FoodLog
from .forms import FoodLogForm
import json
from decimal import Decimal
import unicodedata

def normalize_string(s):
    """Supprime les accents et caractères spéciaux"""
    nfkd_form = unicodedata.normalize('NFKD', s)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)]).lower()

@login_required
@feature_required('nutrition')
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
        'name_normalized': normalize_string(f.name),
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


@login_required
def recipe_list(request):
    """Liste des recettes filtrées selon le profil utilisateur"""
    from .models import Recipe
    
    user_profile = request.user.profile
    recipes = Recipe.objects.filter(is_public=True).prefetch_related('ingredients__food')
    
    # Filtrage par type de repas (optionnel)
    meal_filter = request.GET.get('meal_type')
    if meal_filter:
        recipes = recipes.filter(meal_type=meal_filter)
    
    # Filtrage par difficulté (optionnel)
    difficulty_filter = request.GET.get('difficulty')
    if difficulty_filter:
        recipes = recipes.filter(difficulty=difficulty_filter)
    
    # Calcul des objectifs caloriques de l'utilisateur
    daily_goal = calculate_daily_goal(user_profile)
    
    # Récupération de la consommation actuelle du jour
    today = timezone.now().date()
    logs = FoodLog.objects.filter(owner=request.user, date=today)
    current_intake = {
        'kcal': sum(Decimal(str(log.kcal)) for log in logs),
        'protein': sum(Decimal(str(log.protein)) for log in logs),
        'carbs': sum(Decimal(str(log.carbs)) for log in logs),
        'fat': sum(Decimal(str(log.fat)) for log in logs)
    }
    
    remaining = {
        'kcal': Decimal(str(daily_goal['kcal'])) - current_intake['kcal'],
        'protein': Decimal(str(daily_goal['protein'])) - current_intake['protein'],
        'carbs': Decimal(str(daily_goal['carbs'])) - current_intake['carbs'],
        'fat': Decimal(str(daily_goal['fat'])) - current_intake['fat']
    }
    
    # Tri des recettes par pertinence (calories proches du restant)
    if remaining['kcal'] > 0:
        recipes_with_score = []
        for recipe in recipes:
            kcal_diff = abs(Decimal(str(recipe.kcal_per_serving)) - remaining['kcal'])
            recipes_with_score.append((recipe, kcal_diff))
        recipes_with_score.sort(key=lambda x: x[1])
        recipes = [r[0] for r in recipes_with_score]
    
    context = {
        'recipes': recipes,
        'daily_goal': daily_goal,
        'current_intake': current_intake,
        'remaining': remaining,
        'user_goal': user_profile.goal,
        'meal_types': Recipe.MEAL_TYPE_CHOICES,
        'difficulties': Recipe.DIFFICULTY_CHOICES,
    }
    
    return render(request, 'nutrition/recipe_list.html', context)


@login_required
def recipe_detail(request, slug):
    """Détail d'une recette avec ses ingrédients"""
    from .models import Recipe
    
    recipe = get_object_or_404(Recipe, slug=slug, is_public=True)
    ingredients = recipe.ingredients.select_related('food').all()
    
    # Calcul des valeurs nutritionnelles
    nutrition_info = {
        'total': {
            'kcal': recipe.total_kcal,
            'protein': recipe.total_protein,
            'carbs': recipe.total_carbs,
            'fat': recipe.total_fat,
        },
        'per_serving': {
            'kcal': recipe.kcal_per_serving,
            'protein': recipe.protein_per_serving,
            'carbs': recipe.carbs_per_serving,
            'fat': recipe.fat_per_serving,
        }
    }
    
    context = {
        'recipe': recipe,
        'ingredients': ingredients,
        'nutrition_info': nutrition_info,
    }
    
    return render(request, 'nutrition/recipe_detail.html', context)


def calculate_daily_goal(profile):
    """Calcule les objectifs journaliers selon le profil"""
    # Formule simplifiée basée sur le poids et l'objectif
    if not profile.weight_kg:
        # Valeurs par défaut si pas de poids renseigné
        return {
            'kcal': 2000,
            'protein': 150,
            'carbs': 200,
            'fat': 60
        }
    
    weight = float(profile.weight_kg)
    
    if profile.goal == 'bulk':
        # Prise de masse: surplus calorique
        kcal = weight * 35
        protein = weight * 2.2
        carbs = weight * 5
        fat = weight * 1
    elif profile.goal == 'cut':
        # Perte de poids: déficit calorique
        kcal = weight * 25
        protein = weight * 2.5
        carbs = weight * 2
        fat = weight * 0.8
    else:  # maintain
        # Maintien
        kcal = weight * 30
        protein = weight * 2
        carbs = weight * 3.5
        fat = weight * 0.9
    
    return {
        'kcal': round(kcal),
        'protein': round(protein),
        'carbs': round(carbs),
        'fat': round(fat)
    }