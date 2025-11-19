from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

# Create your models here.
class SportCategory(models.Model):
    """Catégories de sports : Musculation, Sports collectifs, Natation, etc."""
    name = models.CharField(max_length=100, unique=True, help_text="Nom de la catégorie (ex: Musculation, Football)")
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji ou classe d'icône (ex: 🏋️, ⚽)")
    description = models.TextField(blank=True)
    has_specific_exercises = models.BooleanField(default=True, help_text="True si ce sport a ses propres exercices spécifiques")
    order = models.PositiveIntegerField(default=0, help_text="Ordre d'affichage")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Catégorie de sport"
        verbose_name_plural = "Catégories de sports"
    
    def __str__(self):
        return f"{self.icon} {self.name}" if self.icon else self.name

class Exercise(models.Model):
    MUSCLE = [
        ("chest","Pecs"), ("back","Dos"), ("legs","Jambes"),
        ("shoulders","Épaules"), ("arms","Bras"), ("core","Abdos"), ("fullbody","Corps complet"),
        ("cardio","Cardio"), ("technique","Technique")
    ]
    EQUIP = [("barbell","Barre"),("dumbbell","Haltères"),
             ("machine","Machine"),("cable","Poulie"),("bodyweight","Poids du corps"),
             ("ball","Ballon"),("racket","Raquette"),("water","Eau"),("none","Aucun")]
    
    # Catégorie de sport (Musculation, Football, Natation, etc.)
    sport_category = models.ForeignKey(
        SportCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="exercises",
        help_text="Catégorie de sport de cet exercice"
    )
    
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    muscle_group = models.CharField(max_length=20, choices=MUSCLE, blank=True)
    equipment = models.CharField(max_length=20, choices=EQUIP)
    difficulty = models.PositiveSmallIntegerField(default=3)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='exercises/', blank=True, null=True, help_text="Image de démonstration")
    
    def __str__(self): return self.name

class WorkoutTemplate(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workout_templates")
    name = models.CharField(max_length=200)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self): return f"{self.name}"

class TemplateItem(models.Model):
    template = models.ForeignKey(WorkoutTemplate, on_delete=models.CASCADE, related_name="items")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    sets = models.PositiveIntegerField(default=3)
    reps = models.PositiveIntegerField(default=10)
    rest_seconds = models.PositiveIntegerField(default=90)
    notes = models.TextField(blank=True)
    class Meta: ordering = ["order"]

class WorkoutSession(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workout_sessions")
    date = models.DateField(auto_now_add=True)
    from_template = models.ForeignKey(WorkoutTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(default=0, help_text="Durée de la séance en minutes")
    is_completed = models.BooleanField(default=False, help_text="Séance terminée")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self): return f"Session {self.date}"
    
    @property
    def total_volume(self):
        return sum(sl.volume for sl in self.set_logs.all())
    
    @property
    def estimated_calories_burned(self):
        """
        Estimation des calories brûlées selon :
        - Musculation intense : ~6 kcal/min
        - Musculation modérée : ~4 kcal/min
        - Moyenne : 5 kcal/min
        """
        if self.duration_minutes == 0:
            return 0
        return self.duration_minutes * 5

class SetLog(models.Model):
    session = models.ForeignKey(WorkoutSession, on_delete=models.CASCADE, related_name="set_logs")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    set_number = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight_kg = models.DecimalField(max_digits=6, decimal_places=2)
    rpe = models.PositiveSmallIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    @property
    def volume(self): return float(self.weight_kg) * self.reps

class PR(models.Model):
    METRIC = [("max_weight","Charge max"),("max_reps","Reps max"),("est_1rm","1RM estimé")]
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="prs")
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    metric = models.CharField(max_length=20, choices=METRIC)
    value = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    class Meta: unique_together = ("owner","exercise","metric")