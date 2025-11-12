from django.contrib import admin
from .models import Food, FoodLog

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'kcal_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ('owner', 'date', 'food', 'grams', 'meal_type', 'kcal')
    list_filter = ('date', 'meal_type', 'owner')
    search_fields = ('owner__username', 'food__name')
    date_hierarchy = 'date'
    
    def kcal(self, obj):
        return round(obj.kcal, 2)
    kcal.short_description = 'Kcal'
