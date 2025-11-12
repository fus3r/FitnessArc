# nutrition/forms.py

from django import forms
from .models import FoodLog, Food

class FoodLogForm(forms.ModelForm):
    class Meta:
        model = FoodLog
        fields = ['food', 'grams', 'meal_type']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-control', 'required': True}),
            'grams': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Poids en grammes', 'class': 'form-control', 'required': True}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # S'assurer que le queryset Food est bien chargé et trié par nom
        self.fields['food'].queryset = Food.objects.filter(is_public=True).order_by('name')
        self.fields['food'].empty_label = "-- Choisir un aliment --"