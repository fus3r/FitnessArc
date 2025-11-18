# nutrition/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Affiche le journal du jour et permet l'ajout
    path('today/', views.nutrition_today, name='nutrition_today'),
    
    # NOUVEAU : Route pour supprimer un FoodLog spécifique (identifié par sa PK)
    path('delete/<int:pk>/', views.delete_food_log, name='delete_food_log'),
    
    # Recettes
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
]

