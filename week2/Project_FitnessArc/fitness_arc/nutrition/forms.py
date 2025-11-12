# nutrition/forms.py

from django import forms
from .models import FoodLog, Food

class FoodLogForm(forms.ModelForm):
    class Meta:
        model = FoodLog
        fields = ['food', 'quantity', 'meal_type']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-control', 'required': True, 'onchange': 'updateQuantityLabel()'}),
            'quantity': forms.NumberInput(attrs={'min': 1, 'step': '0.1', 'placeholder': 'Quantité', 'class': 'form-control', 'required': True, 'id': 'id_quantity'}),
            'meal_type': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'quantity': 'Quantité',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['food'].queryset = Food.objects.filter(is_public=True).order_by('name')
        self.fields['food'].empty_label = "-- Choisir un aliment --"