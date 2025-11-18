from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "goal", "weight_kg", "height_cm", "sex", "created_at")
    list_filter = ("goal", "sex")
    search_fields = ("user__username", "user__email")
    list_select_related = ("user",)
    ordering = ("user__username",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Utilisateur", {"fields": ("user",)}),
        ("Données corporelles", {"fields": ("sex", "height_cm", "weight_kg", "goal")}),
        ("Meta", {"fields": ("created_at", "updated_at")}),
    )
    autocomplete_fields = ("user",)  