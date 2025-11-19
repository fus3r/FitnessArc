from django.contrib import admin
from .models import Food, FoodLog, Recipe, RecipeIngredient

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'kcal_per_100g', 'protein_per_100g', 'carbs_per_100g', 'fat_per_100g')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(FoodLog)
class FoodLogAdmin(admin.ModelAdmin):
    list_display = ('owner', 'date', 'food', 'quantity', 'meal_type', 'kcal')
    list_filter = ('date', 'meal_type', 'owner')
    search_fields = ('owner__username', 'food__name')
    date_hierarchy = 'date'
    
    def kcal(self, obj):
        return round(obj.kcal, 2)
    kcal.short_description = 'Kcal'


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ['food']


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'meal_type', 'difficulty', 'servings', 'total_time_minutes', 'kcal_per_serving', 'is_public')
    list_filter = ('meal_type', 'difficulty', 'is_public')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RecipeIngredientInline]
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('name', 'slug', 'description', 'meal_type', 'difficulty', 'is_public')
        }),
        ('Temps et portions', {
            'fields': ('prep_time_minutes', 'cook_time_minutes', 'servings')
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Média', {
            'fields': ('image_url',),
            'classes': ('collapse',)
        }),
        ('Métadonnées', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        }),
    )
    
    def kcal_per_serving(self, obj):
        return round(obj.kcal_per_serving, 0)
    kcal_per_serving.short_description = 'Kcal/portion'
