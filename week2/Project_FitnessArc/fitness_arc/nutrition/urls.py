# nutrition/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Display today's journal and allow adding entries
    path('today/', views.nutrition_today, name='nutrition_today'),
    
    # Route to delete a specific FoodLog by ID
    path('delete/<int:pk>/', views.delete_food_log, name='delete_food_log'),
    
    # Recipes
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/<slug:slug>/', views.recipe_detail, name='recipe_detail'),
]

