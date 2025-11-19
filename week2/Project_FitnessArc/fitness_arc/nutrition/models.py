from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

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


class Recipe(models.Model):
    """Recette avec ingrédients et valeurs nutritionnelles calculées"""
    DIFFICULTY_CHOICES = [
        ('easy', 'Facile'),
        ('medium', 'Moyen'),
        ('hard', 'Difficile'),
    ]
    
    MEAL_TYPE_CHOICES = [
        ('breakfast', 'Petit-déjeuner'),
        ('lunch', 'Déjeuner'),
        ('dinner', 'Dîner'),
        ('snack', 'Collation'),
    ]
    
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    instructions = models.TextField(help_text="Instructions de préparation")
    prep_time_minutes = models.PositiveIntegerField(help_text="Temps de préparation en minutes")
    cook_time_minutes = models.PositiveIntegerField(default=0, help_text="Temps de cuisson en minutes")
    servings = models.PositiveIntegerField(default=1, help_text="Nombre de portions")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPE_CHOICES, default='lunch')
    image_url = models.URLField(blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_recipes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def total_time_minutes(self):
        return self.prep_time_minutes + self.cook_time_minutes
    
    @property
    def total_kcal(self):
        """Calories totales de la recette"""
        total = Decimal('0')
        for ingredient in self.ingredients.all():
            total += (ingredient.food.kcal_per_100g * ingredient.quantity) / 100
        return round(total, 2)
    
    @property
    def total_protein(self):
        """Protéines totales de la recette"""
        total = Decimal('0')
        for ingredient in self.ingredients.all():
            total += (ingredient.food.protein_per_100g * ingredient.quantity) / 100
        return round(total, 2)
    
    @property
    def total_carbs(self):
        """Glucides totaux de la recette"""
        total = Decimal('0')
        for ingredient in self.ingredients.all():
            total += (ingredient.food.carbs_per_100g * ingredient.quantity) / 100
        return round(total, 2)
    
    @property
    def total_fat(self):
        """Lipides totaux de la recette"""
        total = Decimal('0')
        for ingredient in self.ingredients.all():
            total += (ingredient.food.fat_per_100g * ingredient.quantity) / 100
        return round(total, 2)
    
    @property
    def kcal_per_serving(self):
        """Calories par portion"""
        if self.servings > 0:
            return round(self.total_kcal / self.servings, 2)
        return 0
    
    @property
    def protein_per_serving(self):
        """Protéines par portion"""
        if self.servings > 0:
            return round(self.total_protein / self.servings, 2)
        return 0
    
    @property
    def carbs_per_serving(self):
        """Glucides par portion"""
        if self.servings > 0:
            return round(self.total_carbs / self.servings, 2)
        return 0
    
    @property
    def fat_per_serving(self):
        """Lipides par portion"""
        if self.servings > 0:
            return round(self.total_fat / self.servings, 2)
        return 0


class RecipeIngredient(models.Model):
    """Ingrédient d'une recette avec quantité"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ingredients')
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=6, decimal_places=2, help_text="Quantité en g/ml/unités")
    notes = models.CharField(max_length=200, blank=True, help_text="Ex: coupé en dés, émincé...")
    
    class Meta:
        unique_together = ['recipe', 'food']
        ordering = ['id']
    
    def __str__(self):
        unit = self.food.get_unit_label()
        return f"{self.quantity}{unit} de {self.food.name}"
