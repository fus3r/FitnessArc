from django.db import models
from django.contrib.auth.models import User

class Food(models.Model):
    UNIT_TYPES = [
        ('g', 'Grammes (g)'),
        ('ml', 'Millilitres (ml)'),
        ('unit', 'Unité(s)'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    kcal_per_100g = models.DecimalField(max_digits=6, decimal_places=2, help_text="Calories (kcal) pour 100g/100ml/unité")
    protein_per_100g = models.DecimalField(max_digits=5, decimal_places=2, help_text="Protéines (g) pour 100g/100ml/unité")
    carbs_per_100g = models.DecimalField(max_digits=5, decimal_places=2, help_text="Glucides (g) pour 100g/100ml/unité")
    fat_per_100g = models.DecimalField(max_digits=5, decimal_places=2, help_text="Lipides (g) pour 100g/100ml/unité")
    unit_type = models.CharField(max_length=10, choices=UNIT_TYPES, default='g', help_text="Type d'unité de mesure")
    is_public = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
    def get_unit_label(self):
        return dict(self.UNIT_TYPES).get(self.unit_type, 'g')

class FoodLog(models.Model):
    MEAL_TYPES = [
        ('breakfast', 'Petit-déjeuner'),
        ('lunch', 'Déjeuner'),
        ('dinner', 'Dîner'),
        ('snack', 'Collation'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='food_logs')
    date = models.DateField()
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, default=100, help_text="Quantité (en grammes, ml ou unités)")
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES, default='snack')
    
    class Meta:
        ordering = ['date', 'meal_type']
        verbose_name_plural = "Food Logs"

    @property
    def kcal(self):
        return (self.food.kcal_per_100g * self.quantity) / 100
    
    @property
    def protein(self):
        return (self.food.protein_per_100g * self.quantity) / 100
    
    @property
    def carbs(self):
        return (self.food.carbs_per_100g * self.quantity) / 100
    
    @property
    def fat(self):
        return (self.food.fat_per_100g * self.quantity) / 100

    def __str__(self):
        unit = self.food.get_unit_label()
        return f"{self.food.name} - {self.quantity}{unit} le {self.date}"
