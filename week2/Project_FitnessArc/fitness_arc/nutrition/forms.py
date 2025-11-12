# nutrition/forms.py

from django import forms
from .models import FoodLog

class FoodLogForm(forms.ModelForm):
    # Champ de recherche d'aliment (Food) : 
    # Plus tard, ce champ utilisera de l'auto-complétion 
    # Pour l'instant, on utilise un champ de sélection standard
    
    class Meta:
        model = FoodLog
        fields = ['food', 'grams', 'meal_type']
        widgets = {
            'grams': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Poids en grammes', 'required': True}),
            # L'ajout du food field peut nécessiter un QuerySet limité si le catalogue est énorme
        }