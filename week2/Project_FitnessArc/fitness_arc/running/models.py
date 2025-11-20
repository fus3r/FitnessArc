from django.db import models
from django.conf import settings


class StravaAuth(models.Model):
    """
    Stores a user's Strava authorization with access/refresh tokens and expiration.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="strava_auth",
    )
    athlete_id = models.BigIntegerField(null=True, blank=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Strava auth de {self.user.username}"


class GarminAuth(models.Model):
    """
    Stores a user's Garmin Connect credentials.
    Uses python-garminconnect which requires email/password.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="garmin_auth",
    )
    email = models.EmailField(help_text="Garmin Connect email")
    # Note: encrypted password storage recommended in production
    password = models.CharField(max_length=255, help_text="Garmin Connect password (encrypted)")
    
    is_active = models.BooleanField(default=True, help_text="Active connection")
    last_sync = models.DateTimeField(null=True, blank=True, help_text="Last sync")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Garmin auth de {self.user.username}"


class Run(models.Model):
    """
    A running activity from Strava or Garmin Connect.
    """
    SOURCE_CHOICES = [
        ('strava', 'Strava'),
        ('garmin', 'Garmin Connect'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="runs",
    )
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='strava', help_text="Activity source")
    strava_id = models.BigIntegerField(null=True, blank=True, unique=True)
    garmin_id = models.BigIntegerField(null=True, blank=True, help_text="Garmin activity ID")  

    name = models.CharField(max_length=255)
    distance_m = models.FloatField()          
    moving_time_s = models.IntegerField()     
    elapsed_time_s = models.IntegerField()    
    start_date = models.DateTimeField()

    average_speed = models.FloatField(
        null=True,
        blank=True,
        help_text="Average speed in m/s",
    )
    average_pace_s_per_km = models.FloatField(
        null=True,
        blank=True,
        help_text="Average pace in seconds per km",
    )
    elevation_gain_m = models.FloatField(
        null=True,
        blank=True,
        help_text="Elevation gain in meters",
    )
    calories_burned = models.FloatField(
        null=True,
        blank=True,
        help_text="Calories burned (kcal)",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.distance_km:.1f} km)"

    @property
    def distance_km(self):
        return self.distance_m / 1000 if self.distance_m else 0

    @property
    def moving_time_hms(self):
        """
        Retourne une durée lisible, ex: '42m13s' ou '1h03m20s'
        """
        s = self.moving_time_s or 0
        h = s // 3600
        m = (s % 3600) // 60
        sec = s % 60
        if h:
            return f"{h}h{m:02d}m{sec:02d}s"
        return f"{m}m{sec:02d}s"

    @property
    def pace_min_per_km(self):
        """
        Retourne une allure style '4:35 /km'
        """
        if not self.average_pace_s_per_km:
            return None
        total_sec = int(self.average_pace_s_per_km)
        minutes = total_sec // 60
        seconds = total_sec % 60
        return f"{minutes}:{seconds:02d} /km"

    def estimate_calories(self):
        """
        Estime les calories brûlées pour cette course.
        Formule simplifiée : ~1 kcal/kg/km pour la course à pied.
        Si le poids de l'utilisateur est disponible, on l'utilise.
        Sinon, on utilise une valeur par défaut de 70 kg.
        """
        weight_kg = 70  # Valeur par défaut
        if hasattr(self.user, 'profile') and self.user.profile.weight_kg:
            weight_kg = float(self.user.profile.weight_kg)
        
        distance_km = self.distance_km
        # Formule : calories ≈ poids (kg) × distance (km) × 1.036
        # Le facteur 1.036 est une moyenne pour la course à pied
        calories = weight_kg * distance_km * 1.036
        return round(calories, 1)

    def save(self, *args, **kwargs):
        # Calcule automatiquement les calories si non définies
        if self.calories_burned is None:
            self.calories_burned = self.estimate_calories()
        
        # Calcule la vitesse et l'allure moyennes
        if self.distance_m and self.moving_time_s:
            # Vitesse moyenne en m/s
            self.average_speed = self.distance_m / self.moving_time_s
            
            # Allure moyenne en secondes par km
            distance_km = self.distance_m / 1000
            if distance_km > 0:
                self.average_pace_s_per_km = self.moving_time_s / distance_km
        
        super().save(*args, **kwargs)
