from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Exercise, WorkoutTemplate, TemplateItem, WorkoutSession, SetLog, PR

class TemplateItemInline(admin.TabularInline):
    model = TemplateItem
    extra = 1

@admin.register(WorkoutTemplate)
class WorkoutTemplateAdmin(admin.ModelAdmin):
    list_display = ("name","owner","is_public","created_at")
    inlines = [TemplateItemInline]

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ("name","muscle_group","equipment","difficulty")
    list_filter = ("muscle_group","equipment","difficulty")
    search_fields = ("name",)

class SetLogInline(admin.TabularInline):
    model = SetLog
    extra = 0

@admin.register(WorkoutSession)
class WorkoutSessionAdmin(admin.ModelAdmin):
    list_display = ("owner","date","from_template")
    inlines = [SetLogInline]

admin.site.register(PR)
