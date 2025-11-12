from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    # Colonnes list view
    list_display = ("user", "goal", "weight_kg", "height_cm", "sex", "created_at")
    # Filtres latéraux
    list_filter = ("goal", "sex")
    # Barre de recherche
    search_fields = ("user__username", "user__email")
    # Perf + ergonomie
    list_select_related = ("user",)
    ordering = ("user__username",)

    # Form d’édition
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Utilisateur", {"fields": ("user",)}),
        ("Données corporelles", {"fields": ("sex", "height_cm", "weight_kg", "goal")}),
        ("Meta", {"fields": ("created_at", "updated_at")}),
    )
    autocomplete_fields = ("user",)  # utile si beaucoup d’utilisateurs
