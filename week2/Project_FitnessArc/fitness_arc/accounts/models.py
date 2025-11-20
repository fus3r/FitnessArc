from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    RUNNING_DATA_SOURCE_CHOICES = [
        ('manual', 'Saisie manuelle'),
        ('strava', 'Strava'),
        ('garmin', 'Garmin'),
    ]
    GOAL_CHOICES = [
        ('bulk', 'Prise de masse'),
        ('cut', 'Perte de poids'),
        ('maintain', 'Maintien'),
    ]
    SEX_CHOICES = [
        ('M', 'Homme'),
        ('F', 'Femme'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True)
    goal = models.CharField(max_length=8, choices=GOAL_CHOICES, default='maintain')

    running_data_source = models.CharField(
        max_length=10,
        choices=RUNNING_DATA_SOURCE_CHOICES,
        default='manual',
        help_text="Source des données de running pour ce profil."
    )
    
    # Feature toggles - allow users to enable/disable specific modules
    feature_workouts = models.BooleanField(default=True, help_text="Activer le module Exercices & Workouts")
    feature_nutrition = models.BooleanField(default=True, help_text="Activer le module Nutrition")
    feature_running = models.BooleanField(default=True, help_text="Activer le module Running")
    feature_leaderboard = models.BooleanField(default=True, help_text="Activer le module Classement")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Profile<{self.user.username}>"


class Friendship(models.Model):
    """Relation d'amitié entre deux utilisateurs"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Refusée'),
    ]
    
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friendships_received')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('from_user', 'to_user')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.from_user.username} → {self.to_user.username} ({self.status})"