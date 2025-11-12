from django.urls import path
from . import views

urlpatterns = [
    # Affiche le journal du jour et permet l'ajout
    path('today/', views.nutrition_today, name='nutrition_today'), 
    
    # Endpoint pour traiter l'ajout (peut être intégré dans nutrition_today)
    # path('add/', views.add_food_log, name='add_food_log'), # Optionnel si tout est dans la vue 'today'
]

