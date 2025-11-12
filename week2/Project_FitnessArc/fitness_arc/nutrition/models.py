# nutrition/models.py

from django.db import models
from django.contrib.auth.models import User # Nécessaire pour la Foreign Key vers l'utilisateur (après le merge de 'accounts')

class Food(models.Model):
    """
    Représente un aliment et ses valeurs nutritionnelles pour 100g.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    
    # Valeurs pour 100g [cite: 93]
    kcal_per_100g = models.DecimalField(max_digits=6, decimal_places=2, help_text="Calories (kcal) pour 100g")
    protein_per_100g = models.DecimalField(max_digits=5, decimal_places=2, help_text="Protéines (g) pour 100g")
    carbs_per_100g = models.DecimalField(max_digits=5, decimal_places=2, help_text="Glucides (g) pour 100g")
    fat_per_100g = models.DecimalField(max_digits=5, decimal_places=2, help_text="Lipides (g) pour 100g")
    
    is_public = models.BooleanField(default=True) # Pour distinguer les aliments du catalogue global et les aliments ajoutés par l'utilisateur si besoin.

    def __str__(self):
        return self.name

class FoodLog(models.Model):
    """
    Enregistrement journalier de la consommation d'un aliment par un utilisateur.
    """
    MEAL_TYPES = [
        ('breakfast', 'Petit-déjeuner'),
        ('lunch', 'Déjeuner'),
        ('dinner', 'Dîner'),
        ('snack', 'Collation'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_logs') # FK vers l'utilisateur [cite: 171]
    date = models.DateField()
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    grams = models.DecimalField(max_digits=6, decimal_places=2) # Poids consommé [cite: 94]
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='snack')
    
    class Meta:
        ordering = ['date', 'meal_type']
        verbose_name_plural = "Food Logs"

    # --- Propriétés calculées (pour éviter de stocker la valeur totale en DB) ---
    @property
    def kcal(self):
        """Calcule les calories totales de cette entrée."""
        # Exemple de calcul : (kcal_100g * grammes) / 100
        return (self.food.kcal_per_100g * self.grams) / 100
    
    @property
    def protein(self):
        """Calcule les grammes de protéines totales de cette entrée."""
        return (self.food.protein_per_100g * self.grams) / 100
    
    @property
    def carbs(self):
        """Calcule les grammes de glucides totales de cette entrée."""
        return (self.food.carbs_per_100g * self.grams) / 100
    
    @property
    def fat(self):
        """Calcule les grammes de lipides totales de cette entrée."""
        return (self.food.fat_per_100g * self.grams) / 100

    def __str__(self):
        return f"{self.food.name} - {self.grams}g le {self.date}"

# NOTE : Le modèle DaySummary est optionnel (calculé à la volée ou matérialisé)[cite: 46, 118]. 
# Ici, nous le calculons à la volée via les propriétés FoodLog.
