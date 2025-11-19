from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Exercise, WorkoutTemplate, TemplateItem, WorkoutSession, SetLog, PR, SportCategory

@admin.register(SportCategory)
class SportCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon", "has_specific_exercises", "order")
    list_filter = ("has_specific_exercises",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

class TemplateItemInline(admin.TabularInline):
    model = TemplateItem
    extra = 1

@admin.register(WorkoutTemplate)
class WorkoutTemplateAdmin(admin.ModelAdmin):
    list_display = ("name","owner","is_public","created_at")
    inlines = [TemplateItemInline]

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name","sport_category","muscle_group","equipment","difficulty")
    list_filter = ("sport_category","muscle_group","equipment","difficulty")
    search_fields = ("name",)

class SetLogInline(admin.TabularInline):
    model = SetLog
    extra = 0

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ("owner","date","from_template")
    inlines = [SetLogInline]

admin.site.register(PR)